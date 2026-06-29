import time
import os
from fastapi import HTTPException
from sqlalchemy.orm import Session
from ..models.user import User
from ..models.voice import Voice
from ..models.generation import Generation
from ..utils.audio import generate_output_filename, get_audio_duration, get_file_size
from ..config import get_settings
from .tts_engines import engine_manager
from .clone_service import clone_service
from ..utils.voice_validation import LANGUAGE_TO_CODE
from deep_translator import GoogleTranslator

async def generate_speech(db: Session, user: User, text: str, voice_id: int, speed: float, pitch: str, project_id: int = None, auto_translate: bool = False) -> Generation:
    settings = get_settings()
    
    if len(text) > settings.MAX_TEXT_LENGTH:
        raise HTTPException(status_code=400, detail=f"Text exceeds maximum length of {settings.MAX_TEXT_LENGTH}")
        
    if user.chars_used + len(text) > user.char_quota:
        raise HTTPException(status_code=400, detail="Character quota exceeded for this month.")
        
    voice = db.query(Voice).filter(Voice.id == voice_id).first()
    if not voice:
        raise HTTPException(status_code=404, detail="Voice not found.")
        
    if auto_translate:
        target_lang = LANGUAGE_TO_CODE.get(voice.language, 'en')
        try:
            text = GoogleTranslator(source='auto', target=target_lang).translate(text)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Translation failed: {str(e)}")
        
    filename = generate_output_filename(user.id, "mp3")
    output_path = os.path.join(settings.OUTPUT_DIR, filename)
    
    start_time = time.perf_counter()
    if voice.is_cloned and voice.engine == "coqui":
        try:
            lang_code = LANGUAGE_TO_CODE.get(voice.language, 'en')
            output_path = await clone_service.generate_with_clone(text, voice.voice_id, output_path, speed, lang_code)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    else:
        try:
            engine = engine_manager.get_engine(voice.engine)
            if not await engine.is_available():
                raise HTTPException(status_code=500, detail=f"Engine {voice.engine} is not available. Please check system status.")
            await engine.generate(text, voice.voice_id, speed, pitch, output_path)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
            
    generation_time = time.perf_counter() - start_time
            
    # Save Generation
    duration = get_audio_duration(output_path)
    file_size = get_file_size(output_path)
    
    generation = Generation(
        user_id=user.id,
        text=text,
        voice_id=voice.id,
        voice_name=voice.name,
        voice_engine=voice.engine,
        audio_path=output_path,
        audio_duration=duration,
        char_count=len(text),
        speed=speed,
        pitch=pitch,
        file_size=file_size,
        status="completed",
        project_id=project_id,
        generation_time_seconds=generation_time
    )
    
    user.chars_used += len(text)
    user.generation_count += 1
    
    db.add(generation)
    db.commit()
    db.refresh(generation)
    
    return generation

def get_available_voices(db: Session, engine_filter: str = None) -> list:
    query = db.query(Voice).filter(Voice.is_active == True)
    if engine_filter:
        query = query.filter(Voice.engine == engine_filter)
    return query.all()

def get_supported_languages(db: Session) -> list:
    langs = db.query(Voice.language, Voice.locale).filter(Voice.is_active == True).distinct().all()
    return [{"name": l[0], "code": l[1]} for l in langs]
