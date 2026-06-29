import requests
import os
import sys

BACKEND_URL = "http://localhost:8000"

def create_dummy_wav(path):
    # Create a minimal valid WAV file (44 bytes header + empty data)
    with open(path, "wb") as f:
        f.write(b'RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00D\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00')

def test_clone_flow():
    print("Testing Voice Cloning API...")
    test_file = "test_recording.wav"
    create_dummy_wav(test_file)
    
    # 1. Test Cloning (Upload/Record)
    print("\n[1] Uploading reference audio...")
    try:
        with open(test_file, "rb") as f:
            files = {"file": ("test_recording.wav", f, "audio/wav")}
            data = {
                "name": "AutoTest Voice",
                "language": "English",
                "description": "Testing the cloning pipeline",
                "consent": "true"
            }
            res = requests.post(f"{BACKEND_URL}/api/voices/clone", files=files, data=data)
            
        if res.status_code != 200:
            print(f"FAILED to clone voice: {res.status_code} - {res.text}")
            return
        
        voice_data = res.json()
        voice_id = voice_data.get("id")
        print(f"SUCCESS: Voice cloned and saved with ID {voice_id}")
    except requests.exceptions.ConnectionError:
        print("FAILED: Cannot connect to backend. Is the server running?")
        return

    # 2. Test Generation
    print("\n[2] Generating TTS audio using cloned voice...")
    payload = {
        "text": "Hello, this is a fully automated test of the voice cloning pipeline.",
        "voice_id": voice_id,
        "mode": "short_form"
    }
    res = requests.post(f"{BACKEND_URL}/api/tts/generate", json=payload)
    if res.status_code == 200:
        print(f"SUCCESS: Audio generated! URL: {res.json().get('audio_url')}")
    else:
        print(f"FAILED to generate audio: {res.status_code} - {res.text}")
        
    os.remove(test_file)

if __name__ == "__main__":
    test_clone_flow()
