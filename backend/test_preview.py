import asyncio
import traceback
from app.database import SessionLocal
from app.services.voice_service import get_voice_preview

async def test():
    db = SessionLocal()
    for vid in [2, 3, 4]:
        try:
            print(f"Generating preview for voice {vid}...")
            url = await get_voice_preview(db, vid)
            print(f"URL for voice {vid}:", url)
        except Exception as e:
            print(f"EXCEPTION for voice {vid}:", traceback.format_exc())

if __name__ == '__main__':
    asyncio.run(test())
