import requests
import json
import time

url = "http://127.0.0.1:8000/api/voices/clone"
files = {'file': ('andrew.mp3', open('backend/andrew.mp3', 'rb'), 'audio/mpeg')}
data = {
    'name': 'Andrew Urdu Test',
    'description': 'Testing cross lingual',
    'language': 'Urdu',
    'consent': True
}

# Assume auth is bypassed for local test or we need a token?
# Let's test with a fake token or check if endpoints are protected.
# Wait, auth is required: `current_user = Depends(get_current_user)`
# So I need to login first.

auth_data = {"username": "admin", "password": "Admin123!"}
login_res = requests.post("http://127.0.0.1:8000/api/auth/token", data=auth_data)
token = login_res.json().get("access_token")
headers = {"Authorization": f"Bearer {token}"}

print("Cloning Voice...")
res = requests.post(url, data=data, files=files, headers=headers)
print("Clone Response:", res.status_code, res.text)
if res.status_code == 200:
    voice_id = res.json()["voice_id"]
    db_id = res.json()["id"]
    print(f"Created voice DB ID: {db_id}, XTTS ID: {voice_id}")
    
    gen_data = {
        "text": "یہ ایک ٹیسٹ ہے۔", # "This is a test." in Urdu
        "voice_id": db_id,
        "mode": "short_form"
    }
    print("Generating speech in Urdu...")
    gen_res = requests.post("http://127.0.0.1:8000/api/tts/generate", json=gen_data, headers=headers)
    print("Gen Response:", gen_res.status_code, gen_res.text)
