import urllib.request
import urllib.parse
import json

data = urllib.parse.urlencode({'username': 'admin', 'password': 'admin123'}).encode()
req = urllib.request.Request('http://127.0.0.1:8000/api/auth/login', data=data)
res = urllib.request.urlopen(req)
token = json.loads(res.read())['access_token']

req2 = urllib.request.Request('http://127.0.0.1:8000/api/tts/generate', 
    data=json.dumps({'text': 'hi', 'voice_id': 1, 'speed': 1.0, 'pitch': '+0Hz'}).encode(),
    headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'})

try:
    print(urllib.request.urlopen(req2).read().decode())
except urllib.error.HTTPError as e:
    print("HTTP ERROR:", e.code, e.read().decode())
except Exception as e:
    print("ERROR:", e)
