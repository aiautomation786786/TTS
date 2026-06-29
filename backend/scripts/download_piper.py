import urllib.request
import os

print("Downloading Piper Default Voices...")
model_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'models', 'piper'))
os.makedirs(model_dir, exist_ok=True)

model_url = "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/en_US-lessac-medium.onnx"
json_url = "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json"

model_path = os.path.join(model_dir, "en_US-lessac-medium.onnx")
json_path = os.path.join(model_dir, "en_US-lessac-medium.onnx.json")

if not os.path.exists(model_path):
    print(f"Downloading {model_url}...")
    urllib.request.urlretrieve(model_url, model_path)
else:
    print("Model already exists.")

if not os.path.exists(json_path):
    print(f"Downloading {json_url}...")
    urllib.request.urlretrieve(json_url, json_path)
else:
    print("JSON config already exists.")

print("Done! Piper TTS is ready.")
