import os
import shutil
import asyncio
from sqlalchemy.orm import Session
import sys

# Add the parent directory to sys.path so we can import 'app'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.voice import Voice
from app.config import get_settings
from app.utils.audio_merge import merge_audio_files

settings = get_settings()

async def main():
    print("=======================================")
    print("    Long Form Readiness Check")
    print("=======================================")

    ready = True

    # Check FFmpeg
    ffmpeg_path = shutil.which("ffmpeg")
    if ffmpeg_path:
        print(f"[PASS] FFmpeg Available: Yes ({ffmpeg_path})")
    else:
        print("[FAIL] FFmpeg Available: No")
        ready = False

    # Check Folders Writable
    try:
        os.makedirs(settings.TEMP_CHUNK_DIR, exist_ok=True)
        test_file = os.path.join(settings.TEMP_CHUNK_DIR, "test_write.txt")
        with open(test_file, "w") as f:
            f.write("test")
        os.remove(test_file)
        print("[PASS] Temp Folder Writable: Yes")
    except Exception as e:
        print(f"[FAIL] Temp Folder Writable: No ({str(e)})")
        ready = False

    try:
        os.makedirs(settings.LONG_FORM_DIR, exist_ok=True)
        test_file = os.path.join(settings.LONG_FORM_DIR, "test_write.txt")
        with open(test_file, "w") as f:
            f.write("test")
        os.remove(test_file)
        print("[PASS] Output Folder Writable: Yes")
    except Exception as e:
        print(f"[FAIL] Output Folder Writable: No ({str(e)})")
        ready = False

    # Check Active Voice
    db = SessionLocal()
    voice = db.query(Voice).filter(Voice.engine == "edge-tts").first()
    if voice:
        print(f"[PASS] Active Voice Available: Yes ({voice.name})")
    else:
        print("[FAIL] Active Voice Available: No")
        ready = False

    # Edge-TTS Generation Test
    chunk_path1 = os.path.join(settings.TEMP_CHUNK_DIR, "ready_test_chunk_1.mp3")
    chunk_path2 = os.path.join(settings.TEMP_CHUNK_DIR, "ready_test_chunk_2.mp3")
    output_path = os.path.join(settings.LONG_FORM_DIR, "ready_test_merged.mp3")
    
    try:
        if voice:
            import edge_tts
            print("Testing Edge-TTS Generation...")
            communicate = edge_tts.Communicate("Testing chunk one.", voice.voice_id)
            await communicate.save(chunk_path1)
            communicate2 = edge_tts.Communicate("Testing chunk two.", voice.voice_id)
            await communicate2.save(chunk_path2)
            
            if os.path.exists(chunk_path1) and os.path.exists(chunk_path2):
                print("[PASS] Edge-TTS Generation Test: Pass")
            else:
                print("[FAIL] Edge-TTS Generation Test: Fail (Files missing)")
                ready = False
                
            # Merge Test
            print("Testing FFmpeg Merge...")
            success = merge_audio_files([chunk_path1, chunk_path2], output_path)
            if success and os.path.exists(output_path):
                print("[PASS] Merge Test: Pass")
                os.remove(output_path)
            else:
                print("[FAIL] Merge Test: Fail")
                ready = False
                
            os.remove(chunk_path1)
            os.remove(chunk_path2)
    except Exception as e:
        print(f"[FAIL] Edge-TTS / Merge Test: Exception ({str(e)})")
        ready = False
    finally:
        db.close()

    print("=======================================")
    if ready:
        print("[OK] SYSTEM IS READY FOR 12-MINUTE LONG FORM GENERATION")
    else:
        print("[ERROR] SYSTEM IS NOT READY FOR 12-MINUTE GENERATION")
    print("=======================================")

if __name__ == "__main__":
    asyncio.run(main())
