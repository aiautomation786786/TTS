import os
import requests
import subprocess
import time

def test_download_formats():
    print("========================================")
    print("VALIDATE DOWNLOAD FORMATS (MP3/WAV)")
    print("========================================")
    
    # 1. Check if FFmpeg is installed
    try:
        res = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, check=True)
        print("[PASS] FFmpeg is installed and accessible.")
    except Exception as e:
        print(f"[FAIL] FFmpeg is missing or not in PATH: {e}")
        return False
        
    print("\nSimulating file conversion test...")
    # Create a dummy silent audio file using ffmpeg to test conversion
    dummy_path = os.path.join(os.path.dirname(__file__), "..", "data", "outputs", "test_silent.mp3")
    wav_path = dummy_path.replace(".mp3", "_converted.wav")
    
    os.makedirs(os.path.dirname(dummy_path), exist_ok=True)
    
    try:
        # Generate 1 second of silence
        subprocess.run(
            ["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", "1", "-q:a", "9", "-acodec", "libmp3lame", dummy_path],
            capture_output=True, check=True
        )
        print(f"[PASS] Created test source file: {dummy_path}")
        
        # Test conversion to WAV
        subprocess.run(
            ["ffmpeg", "-y", "-i", dummy_path, wav_path],
            capture_output=True, check=True
        )
        
        if os.path.exists(wav_path) and os.path.getsize(wav_path) > 0:
            print(f"[PASS] Converted MP3 to WAV successfully. Size: {os.path.getsize(wav_path)} bytes")
        else:
            print("[FAIL] WAV file not created or is empty.")
            return False
            
    except Exception as e:
        print(f"[FAIL] Conversion process failed: {e}")
        return False
    finally:
        # Cleanup
        if os.path.exists(dummy_path): os.remove(dummy_path)
        if os.path.exists(wav_path): os.remove(wav_path)
        
    print("\n[SUCCESS] Download Format Conversion Validation Passed.")
    return True

if __name__ == "__main__":
    test_download_formats()
