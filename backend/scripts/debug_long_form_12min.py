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
from fastapi import BackgroundTasks

class DummyBackgroundTasks:
    def __init__(self):
        self.tasks = []
    
    def add_task(self, func, *args, **kwargs):
        self.tasks.append((func, args, kwargs))

async def main():
    print("=== Long Form TTS Debug Script ===")
    
    db = SessionLocal()
    user = db.query(User).first()
    if not user:
        print("FAIL: No user found in database.")
        return

    # Find a working voice (Edge-TTS Aria or similar)
    voice = db.query(Voice).filter(Voice.engine == "edge-tts").first()
    if not voice:
        print("FAIL: No Edge-TTS voice found in database.")
        return
        
    print(f"Using Voice: {voice.name} (ID: {voice.id})")
    
    # Create 16000+ char text
    text = "This is a test of the long form TTS generation system. It needs to be sufficiently long to trigger the chunking logic. " * 150
    print(f"Test text length: {len(text)} characters")
    
    bg_tasks = DummyBackgroundTasks()
    
    try:
        print("Starting long form job...")
        job = await start_long_form_job(bg_tasks, db, user, text, voice.id, 1.0, "+0Hz")
        print(f"Job created successfully: ID {job.id}, total chunks expected: {job.total_chunks}")
        
        if not bg_tasks.tasks:
            print("FAIL: Background task was not scheduled.")
            return
            
        # Manually run the background task
        func, args, kwargs = bg_tasks.tasks[0]
        print(f"Running background worker manually...")
        
        # We need to run it concurrently and poll it, or just await it.
        # Since we are in a debug script, we just await it and poll from another task or just wait.
        # Let's run it directly.
        worker_task = asyncio.create_task(func(*args, **kwargs))
        
        while not worker_task.done():
            # refresh job
            db.refresh(job)
            print(f"Status: {job.status} | Progress: {job.progress}% | Chunks: {job.completed_chunks}/{job.total_chunks}")
            await asyncio.sleep(1)
            
        db.refresh(job)
        print(f"Final Status: {job.status}")
        
        if job.status == "failed":
            print(f"FAIL: Job failed with error: {job.error_message}")
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
