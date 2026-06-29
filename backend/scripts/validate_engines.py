import sys
import os
import asyncio

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.services.tts_engines import engine_manager

def print_result(name, passed, detail=""):
    status = "[PASS]" if passed else "[FAIL]"
    print(f"{status} {name} {detail}")

async def validate_engines():
    print("=======================================")
    print("       Engine Validation Script        ")
    print("=======================================")
    
    statuses = await engine_manager.get_all_status()
    
    for engine_info in statuses:
        name = engine_info["name"]
        print(f"\n--- Testing Engine: {name} ---")
        
        diag = engine_info.get("diagnostics", {})
        is_installed = diag.get("installed", False)
        is_configured = diag.get("configured", False)
        
        print_result(f"{name} Installed", is_installed)
        print_result(f"{name} Configured", is_configured)
        
        if is_installed and is_configured:
            # Try to get voices
            engine = engine_manager.get_engine(name)
            try:
                voices = await engine.get_voices()
                print_result(f"{name} Voices Loaded", True, f"({len(voices)} voices)")
            except Exception as e:
                print_result(f"{name} Voices Loaded", False, str(e))
                
            # For Piper, test generation
            if name == "Piper" and voices:
                try:
                    test_voice = voices[0]["voice_id"]
                    test_output = os.path.join(os.path.dirname(__file__), '..', 'data', 'temp_chunks', 'test_piper.wav')
                    os.makedirs(os.path.dirname(test_output), exist_ok=True)
                    
                    await engine.generate("This is a test.", test_voice, speed=1.0, output_path=test_output)
                    print_result(f"{name} Audio Generation", True)
                    if os.path.exists(test_output):
                        os.remove(test_output)
                except Exception as e:
                    print_result(f"{name} Audio Generation", False, str(e))
        else:
            print(f"Skipping generation tests for {name} (Not fully configured)")
            if diag.get("last_error"):
                print(f"Error: {diag['last_error']}")
                
    print("\n=======================================")

if __name__ == "__main__":
    asyncio.run(validate_engines())
