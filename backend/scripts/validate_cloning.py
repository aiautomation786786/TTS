import requests
import sys

WORKER_URL = "http://127.0.0.1:8001"

def test_cloning_worker():
    print("========================================")
    print("VALIDATE COQUI XTTS CLONING WORKER")
    print("========================================")
    
    print(f"Checking worker health at {WORKER_URL}/health...")
    try:
        res = requests.get(f"{WORKER_URL}/health", timeout=5.0)
        res.raise_for_status()
        data = res.json()
        print("[PASS] Worker is online.")
        print(f"  Python Version : {data.get('python_version')}")
        print(f"  TTS Installed  : {data.get('tts_installed')}")
        print(f"  CUDA Available : {data.get('cuda_available')}")
        print(f"  Model Loaded   : {data.get('model_loaded')}")
        
        if not data.get("ready"):
            print("[WARN] Worker is online but TTS is not ready or failed to load model.")
            return False
            
        print("\n[SUCCESS] Coqui XTTS Cloning Worker Validation Passed.")
        return True
    except requests.exceptions.ConnectionError:
        print("[FAIL] Worker is OFFLINE. Did you run run_coqui_worker.bat?")
        return False
    except Exception as e:
        print(f"[FAIL] Unexpected error: {e}")
        return False

if __name__ == "__main__":
    test_cloning_worker()
