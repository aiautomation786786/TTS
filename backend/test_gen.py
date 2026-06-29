import asyncio
from app.database import SessionLocal, init_db
from app.models.user import User
from app.services.tts_service import generate_speech
from app.models.user import User
from app.models.voice import Voice
from app.models.generation import Generation, SystemSettings
from app.models.preset import VoicePreset
from app.models.pronunciation import PronunciationRule
from app.models.batch import BatchJob, BatchItem
from app.models.notification import Notification
from app.models.favorite import FavoriteVoice

async def test():
    db = SessionLocal()
    user = db.query(User).first()
    print("Testing generation...")
    try:
        gen = await generate_speech(db, user, "hi", 1, 1.0, "+0Hz")
        print("Success!", gen.audio_path)
    except Exception as e:
        import traceback
        traceback.print_exc()

asyncio.run(test())
