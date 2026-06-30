import urllib.request
import os

print("Downloading Piper Default Voices...")
model_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'models', 'piper'))
os.makedirs(model_dir, exist_ok=True)

VOICES = [
    ("en/en_US/lessac/medium/en_US-lessac-medium", "en_US-lessac-medium"),
    ("en/en_US/lessac/high/en_US-lessac-high", "en_US-lessac-high"),
    ("en/en_US/amy/medium/en_US-amy-medium", "en_US-amy-medium"),
    ("en/en_GB/alan/medium/en_GB-alan-medium", "en_GB-alan-medium"),
    ("en/en_US/danny/low/en_US-danny-low", "en_US-danny-low")
]

for url_path, filename in VOICES:
    model_url = f"https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/{url_path}.onnx"
    json_url = f"https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/{url_path}.onnx.json"
    
    model_path = os.path.join(model_dir, f"{filename}.onnx")
    json_path = os.path.join(model_dir, f"{filename}.onnx.json")
    
    if not os.path.exists(model_path):
        print(f"Downloading {filename}.onnx...")
        urllib.request.urlretrieve(model_url, model_path)
    
    if not os.path.exists(json_path):
        print(f"Downloading {filename}.onnx.json...")
        urllib.request.urlretrieve(json_url, json_path)

print("Done! Piper TTS voices are ready.")
