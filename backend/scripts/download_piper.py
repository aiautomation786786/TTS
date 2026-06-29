import urllib.request
import zipfile
import os
import shutil

print("Downloading Piper...")
url = "https://github.com/rhasspy/piper/releases/download/2023.11.14-2/piper_windows_amd64.zip"
zip_path = "piper.zip"
model_dir = r"D:\TTS\backend\models\piper"

os.makedirs(model_dir, exist_ok=True)
urllib.request.urlretrieve(url, zip_path)

print("Extracting Piper...")
with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.extractall(model_dir)

# The zip contains a folder called 'piper'. Let's move its contents to model_dir
piper_extracted_dir = os.path.join(model_dir, "piper")
if os.path.exists(piper_extracted_dir):
    for item in os.listdir(piper_extracted_dir):
        s = os.path.join(piper_extracted_dir, item)
        d = os.path.join(model_dir, item)
        if os.path.exists(d):
            if os.path.isdir(d):
                shutil.rmtree(d)
            else:
                os.remove(d)
        shutil.move(s, d)
    shutil.rmtree(piper_extracted_dir)

os.remove(zip_path)
print("Done!")
