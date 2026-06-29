import asyncio
import aiohttp
import os

async def main():
    async with aiohttp.ClientSession() as session:
        # 1. Login to get token
        login_data = {"username": "admin", "password": "admin123"}
        async with session.post("http://127.0.0.1:8000/api/auth/login", data=login_data) as resp:
            if resp.status != 200:
                print(f"Login failed: {await resp.text()}")
                return
            token_data = await resp.json()
            token = token_data["access_token"]
            print(f"Logged in successfully.")
            
        headers = {"Authorization": f"Bearer {token}"}
        
        # 2. Check Clone Status
        async with session.get("http://127.0.0.1:8000/api/voices/clone/status", headers=headers) as resp:
            status = await resp.json()
            print(f"Clone Status: {status}")
            
        # 3. Create dummy wav file for testing
        with open("test_dummy.wav", "wb") as f:
            f.write(b"RIFF\x24\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x44\xac\x00\x00\x88\x58\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00")
            
        # 4. Clone voice
        data = aiohttp.FormData()
        data.add_field("name", "Test Agent Voice")
        data.add_field("description", "Automated test voice")
        data.add_field("language", "English")
        data.add_field("consent", "true")
        data.add_field("file", open("test_dummy.wav", "rb"), filename="test_dummy.wav", content_type="audio/wav")
        
        print("Submitting cloning request...")
        async with session.post("http://127.0.0.1:8000/api/voices/clone", data=data, headers=headers) as resp:
            if resp.status == 200:
                result = await resp.json()
                print(f"SUCCESS! Cloned Voice ID: {result['id']}, Engine Voice ID: {result['voice_id']}")
            else:
                print(f"FAILED! Status: {resp.status}, Error: {await resp.text()}")

asyncio.run(main())
