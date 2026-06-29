import asyncio
import os
import shutil
import uuid
import traceback
import subprocess
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from ..models.generation import Generation
from ..models.voice import Voice
from ..models.user import User
from ..config import get_settings
from ..utils.audio import generate_output_filename, get_audio_duration, get_file_size
from ..utils.chunking import split_text_into_chunks
from ..utils.audio_merge import merge_audio_files
from .tts_engines import engine_manager
from .clone_service import clone_service

from ..utils.voice_validation import LANGUAGE_TO_CODE
from deep_translator import GoogleTranslator

settings = get_settings()

def get_job(db: Session, job_id: int, user_id: int) -> Generation | None:
    return db.query(Generation).filter(Generation.id == job_id, Generation.user_id == user_id, Generation.mode == "long_form").first()

async def start_long_form_job(background_tasks, db: Session, user: User, text: str, voice_id: int, speed: float, pitch: str, project_id: int = None, auto_translate: bool = False) -> Generation:
    if len(text) > settings.LONG_FORM_MAX_CHARS:
        raise ValueError(f"Text exceeds long form maximum length of {settings.LONG_FORM_MAX_CHARS} characters.")
        
    voice = db.query(Voice).filter(Voice.id == voice_id).first()
    if not voice:
        raise ValueError("Voice not found.")
        
    if user.chars_used + len(text) > user.char_quota:
        raise ValueError("Character quota exceeded for this month.")

    if auto_translate:
        target_lang = LANGUAGE_TO_CODE.get(voice.language, 'en')
        try:
            text = GoogleTranslator(source='auto', target=target_lang).translate(text)
        except Exception as e:
            raise ValueError(f"Translation failed: {str(e)}")

    # 0. Check FFmpeg availability and directories
    os.makedirs(settings.TEMP_CHUNK_DIR, exist_ok=True)
    os.makedirs(settings.LONG_FORM_DIR, exist_ok=True)
    if shutil.which("ffmpeg") is None:
        raise ValueError("FFmpeg is required for long-form audio merging. Please install FFmpeg.")

    # 1. Chunk the text
    chunks = split_text_into_chunks(text, max_size=settings.LONG_FORM_CHUNK_SIZE)
    if not chunks:
        raise ValueError("Could not split text into valid chunks.")

    # 2. Create the pending Generation record
    job = Generation(
        user_id=user.id,
        text=text,
        voice_id=voice.id,
        voice_name=voice.name,
        voice_engine=voice.engine,
        char_count=len(text),
        speed=speed,
        pitch=pitch,
        mode="long_form",
        status="pending",
        total_chunks=len(chunks),
        completed_chunks=0,
        progress=0.0,
        project_id=project_id
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    
    # 3. Deduct quota now
    user.chars_used += len(text)
    db.commit()

    # 4. Start background processing (we return immediately)
    background_tasks.add_task(process_long_form_job_background, job.id, chunks, voice.voice_id, voice.is_cloned, voice.engine)
    
    return job

async def process_long_form_job_background(job_id: int, chunks: list[str], engine_voice_id: str, is_cloned: bool, engine_name: str, start_index: int = 0):
    from ..database import SessionLocal
    db = SessionLocal()
    
    try:
        job = db.query(Generation).filter(Generation.id == job_id).first()
        if not job:
            return

        import time
        start_time = time.perf_counter()

        job.status = "chunking" if start_index == 0 else "generating"
        db.commit()

        chunk_files = []
        
        # Reconstruct previously generated chunks if retrying
        if start_index > 0:
            for i in range(start_index):
                chunk_files.append(os.path.join(settings.TEMP_CHUNK_DIR, f"job_{job.id}_chunk_{i}.mp3"))

        engine = engine_manager.get_engine(engine_name) if not is_cloned else None
        
        for i in range(start_index, len(chunks)):
            job.status = "generating"
            db.commit()
            
            chunk_text = chunks[i]
            chunk_path = os.path.join(settings.TEMP_CHUNK_DIR, f"job_{job.id}_chunk_{i}.mp3")
            
            attempts = 0
            max_attempts = 3
            success = False
            last_error = ""
            
            while attempts < max_attempts and not success:
                try:
                    if attempts == 1:
                        # First retry: light sanitization
                        from .text_sanitizer import sanitize_for_tts
                        chunk_text = sanitize_for_tts(chunk_text, aggressive=False)["cleaned"]
                    elif attempts == 2:
                        # Second retry: aggressive sanitization
                        from .text_sanitizer import sanitize_for_tts
                        chunk_text = sanitize_for_tts(chunk_text, aggressive=True)["cleaned"]
                        
                    if is_cloned and engine_name == "coqui":
                        await clone_service.generate_with_clone(chunk_text, engine_voice_id, chunk_path, job.speed)
                    else:
                        if not await engine.is_available():
                            raise Exception(f"Engine {engine_name} became unavailable.")
                        await engine.generate(chunk_text, engine_voice_id, job.speed, job.pitch, chunk_path)
                    
                    success = True
                except Exception as ex:
                    attempts += 1
                    last_error = str(ex)
                    import time
                    time.sleep(1) # brief pause before retry
                    
            if not success:
                # Store exact chunk failure details
                job.failed_chunk_index = i
                job.failed_chunk_text_preview = chunks[i][:200] + "..." if len(chunks[i]) > 200 else chunks[i]
                job.failed_engine_error = last_error
                raise Exception(f"Chunk {i} failed after {max_attempts} attempts. Error: {last_error}")
                
            chunk_files.append(chunk_path)
            
            # Update progress
            job.completed_chunks = i + 1
            # 90% is generation, 10% is merging
            job.progress = min(90.0, (job.completed_chunks / job.total_chunks) * 90.0)
            db.commit()
            
        # All chunks generated, now merge
        job.status = "merging"
        job.progress = 95.0
        db.commit()
        
        final_filename = generate_output_filename(job.user_id, "mp3")
        final_path = os.path.join(settings.LONG_FORM_DIR, final_filename)
        
        merge_success = merge_audio_files(chunk_files, final_path)
        if not merge_success:
            raise Exception("FFmpeg failed to merge audio chunks.")
            
        # Success! Finalize job
        generation_time = time.perf_counter() - start_time
        
        job.audio_path = final_path
        job.audio_duration = get_audio_duration(final_path)
        job.file_size = get_file_size(final_path)
        job.status = "completed"
        job.progress = 100.0
        job.error_message = None
        job.generation_time_seconds = generation_time
        db.commit()
        
        # Cleanup temp chunks
        for f in chunk_files:
            if os.path.exists(f):
                os.remove(f)
                
    except Exception as e:
        db.rollback()
        # Ensure we don't crash if job wasn't found before failing
        job = db.query(Generation).filter(Generation.id == job_id).first()
        if job:
            job.status = "failed"
            import traceback
            import time
            try:
                generation_time = time.perf_counter() - start_time
                job.generation_time_seconds = generation_time
            except:
                pass
            job.error_message = str(e) + "\n\n" + traceback.format_exc()
            db.commit()
        print(f"Long Form Job {job_id} Failed: {str(e)}")
    finally:
        db.close()

async def retry_failed_job(background_tasks, db: Session, job: Generation) -> bool:
    if job.status != "failed":
        raise ValueError("Only failed jobs can be retried.")
        
    voice = db.query(Voice).filter(Voice.id == job.voice_id).first()
    if not voice:
        raise ValueError("Original voice not found in database.")
        
    chunks = split_text_into_chunks(job.text, max_size=settings.LONG_FORM_CHUNK_SIZE)
    
    # Reset status
    job.status = "pending"
    job.error_message = None
    db.commit()
    
    background_tasks.add_task(process_long_form_job_background, job.id, chunks, voice.voice_id, voice.is_cloned, voice.engine, job.completed_chunks)
    return True
