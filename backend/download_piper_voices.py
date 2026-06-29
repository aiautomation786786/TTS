import os
import urllib.request

models_dir = r"d:\TTS\backend\models\piper"
os.makedirs(models_dir, exist_ok=True)

voices = [
    {
        "name": "en_GB-cori-high",
        "url_onnx": "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_GB/cori/high/en_GB-cori-high.onnx",
        "url_json": "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_GB/cori/high/en_GB-cori-high.onnx.json"
    },
    {
        "name": "en_US-joe-medium",
        "url_onnx": "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/joe/medium/en_US-joe-medium.onnx",
        "url_json": "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/joe/medium/en_US-joe-medium.onnx.json"
    },
    {
        "name": "en_US-kristin-medium",
        "url_onnx": "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/kristin/medium/en_US-kristin-medium.onnx",
        "url_json": "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/kristin/medium/en_US-kristin-medium.onnx.json"
    },
    {
        "name": "en_GB-northern_english_male-medium",
        "url_onnx": "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_GB/northern_english_male/medium/en_GB-northern_english_male-medium.onnx",
        "url_json": "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_GB/northern_english_male/medium/en_GB-northern_english_male-medium.onnx.json"
    },
    {
        "name": "en_US-kathleen-low",
        "url_onnx": "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/kathleen/low/en_US-kathleen-low.onnx",
        "url_json": "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/kathleen/low/en_US-kathleen-low.onnx.json"
    }
]

for v in voices:
    print(f"Downloading {v['name']}...")
    onnx_path = os.path.join(models_dir, f"{v['name']}.onnx")
    json_path = os.path.join(models_dir, f"{v['name']}.onnx.json")
    
    if not os.path.exists(onnx_path):
        urllib.request.urlretrieve(v['url_onnx'], onnx_path)
    if not os.path.exists(json_path):
        urllib.request.urlretrieve(v['url_json'], json_path)

print("Successfully downloaded 5 more premium Piper voices.")
