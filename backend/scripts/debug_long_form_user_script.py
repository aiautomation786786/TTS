import asyncio
import os
import sys
import time

# Add the parent directory to sys.path so we can import 'app'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.user import User
from app.models.voice import Voice
from app.services.long_form_service import start_long_form_job, process_long_form_job_background
from app.utils.chunking import split_text_into_chunks
from app.utils.text_sanitizer import sanitize_for_tts

class DummyBackgroundTasks:
    def __init__(self):
        self.tasks = []
    
    def add_task(self, func, *args, **kwargs):
        self.tasks.append((func, args, kwargs))

async def main():
    print("=======================================")
    print("    Long Form User Script Debugger     ")
    print("=======================================")
    
    script_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "test_scripts", "user_long_form_script.txt")
    
    if not os.path.exists(script_path):
        print(f"FAIL: Script file not found at {script_path}")
        return
        
    with open(script_path, "r", encoding="utf-16") as f:
        try:
            original_text = f.read().strip()
        except UnicodeError:
            with open(script_path, "r", encoding="utf-8") as f2:
                original_text = f2.read().strip()
        
    if not original_text:
        print("FAIL: Script is empty.")
        return

    print("--- 1. Script Analysis ---")
    print(f"Original Length: {len(original_text)} chars")
    print(f"Original Words: {len(original_text.split())} words")
    
    sanitized = sanitize_for_tts(original_text)
    text = sanitized["cleaned"]
    stats = sanitized["stats"]
    
    print(f"Cleaned Length: {stats['cleaned_length']} chars")
    print(f"Removed Chars: {stats['removed_characters']}")
    if stats['removed_characters'] > 0:
        print("WARNING: Unsafe characters were detected and removed/normalized.")
        
    chunks = split_text_into_chunks(text)
    print(f"\n--- 2. Chunking Analysis ---")
    print(f"Total Chunks Generated: {len(chunks)}")
    for i, chunk in enumerate(chunks):
        print(f"  Chunk {i}: {len(chunk)} chars -> {chunk[:50].replace(chr(10), ' ')}...")
        if len(chunk) > 1200:
            print(f"  [!] WARNING: Chunk {i} exceeds safe limit of 1200 chars ({len(chunk)} chars).")

    db = SessionLocal()
    user = db.query(User).first()
    if not user:
        print("FAIL: No user found in database.")
        db.close()
        return

    # Find a working voice
    voice = db.query(Voice).filter(Voice.name == "Ryan").first()
    if not voice:
        print("FAIL: Voice 'Ryan' not found in database.")
        db.close()
        return
        
    print(f"\n--- 3. Database & Job Creation ---")
    print(f"Using Voice: {voice.name} (ID: {voice.id})")
    
    bg_tasks = DummyBackgroundTasks()
    
    try:
        print("Starting long form job...")
        job = await start_long_form_job(bg_tasks, db, user, text, voice.id, 1.0, "+0Hz")
        print(f"Job created successfully: ID {job.id}, total chunks expected: {job.total_chunks}")
        
        if not bg_tasks.tasks:
            print("FAIL: Background task was not scheduled.")
            return
            
        func, args, kwargs = bg_tasks.tasks[0]
        print(f"\n--- 4. Generation Process ---")
        
        worker_task = asyncio.create_task(func(*args, **kwargs))
        
        last_progress = -1
        while not worker_task.done():
            db.refresh(job)
            if job.progress != last_progress:
                print(f"Status: {job.status} | Progress: {job.progress:.1f}% | Chunks: {job.completed_chunks}/{job.total_chunks}")
                last_progress = job.progress
            await asyncio.sleep(2)
            
        db.refresh(job)
        print(f"\n--- 5. Final Results ---")
        print(f"Final Status: {job.status}")
        
        if job.status == "failed":
            print(f"FAIL: Job failed!")
            if job.failed_chunk_index is not None:
                print(f"Failed Chunk Index: {job.failed_chunk_index}")
                print(f"Engine Error: {job.failed_engine_error}")
                print(f"Text Preview: {job.failed_chunk_text_preview}")
            else:
                print(f"Error Message: {job.error_message}")
            return
            
        if job.status == "completed":
            print(f"SUCCESS! Final audio path: {job.audio_path}")
            if os.path.exists(job.audio_path) and os.path.getsize(job.audio_path) > 0:
                print(f"Verified: File exists and size is {os.path.getsize(job.audio_path)} bytes.")
                print("PASS")
            else:
                print("FAIL: File does not exist or is empty.")
    except Exception as e:
        print(f"FAIL: Exception occurred: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(main())
