import urllib.request
import os

model_dir = r"D:\TTS\backend\models\piper"
onnx_path = os.path.join(model_dir, "en_US-lessac-high.onnx")
json_path = os.path.join(model_dir, "en_US-lessac-high.onnx.json")

print("Removing old files...")
if os.path.exists(onnx_path): os.remove(onnx_path)
if os.path.exists(json_path): os.remove(json_path)

print("Downloading JSON...")
urllib.request.urlretrieve("https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/high/en_US-lessac-high.onnx.json", json_path)

print("Downloading ONNX...")
urllib.request.urlretrieve("https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/high/en_US-lessac-high.onnx", onnx_path)

print("Done!")
