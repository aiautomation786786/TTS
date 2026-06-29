from fastapi.testclient import TestClient
from app.main import app
import json

client = TestClient(app)

res_login = client.post("/api/auth/login", data={"username": "admin", "password": "admin123"})
token = res_login.json()["access_token"]

try:
    res = client.post("/api/tts/generate", 
        json={"text": "hi", "voice_id": 1, "speed": 1.0, "pitch": "+0Hz"},
        headers={"Authorization": f"Bearer {token}"})
    print(res.status_code)
    print(res.json())
except Exception as e:
    import traceback
    traceback.print_exc()
