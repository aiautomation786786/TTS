import sys
import os
import asyncio

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.database import SessionLocal
from app.models.voice import Voice
from app.services.tts_engines import engine_manager

async def sync_voices(db):
    print("Syncing voices from engines...")
    piper_engine = engine_manager.get_engine("piper")
    if await piper_engine.is_available():
        piper_voices = await piper_engine.get_voices()
        for v in piper_voices:
            # Check if voice already exists
            existing = db.query(Voice).filter(Voice.voice_id == v["voice_id"]).first()
            if not existing:
                print(f"Adding Piper voice: {v['name']} ({v['voice_id']})")
                new_voice = Voice(
                    name=v["name"],
                    voice_id=v["voice_id"],
                    engine=v["engine"],
                    language=v["language"],
                    locale=v["locale"],
                    gender=v["gender"],
                    style=v["style"],
                    category=v["category"],
                    quality_label=v["quality_label"],
                    use_case_tags=v["tags"],
                    tone_tags="[]",
                    recommended_for="[]",
                    is_builtin=True,
                    is_active=True,
                    is_cloned=False,
                    preview_status="working",
                    generation_status="working"
                )
                db.add(new_voice)
        db.commit()
    else:
        print("Piper not available, skipping Piper sync.")

async def validate_voices():
    print("=======================================")
    print("        Voice Validation Script        ")
    print("=======================================")
    
    db = SessionLocal()
    await sync_voices(db)
    print("=======================================")
    
    db = SessionLocal()
    
    voices = db.query(Voice).all()
    active_voices = [v for v in voices if v.is_active]
    
    print(f"Total Voices in Database: {len(voices)}")
    print(f"Active Voices: {len(active_voices)}")
    
    engine_counts = {}
    lang_counts = {}
    
    for v in active_voices:
        engine_counts[v.engine] = engine_counts.get(v.engine, 0) + 1
        lang_counts[v.language] = lang_counts.get(v.language, 0) + 1
        
    print("\n--- Voices by Engine ---")
    for engine, count in engine_counts.items():
        print(f"  {engine}: {count} working voices")
        
    print("\n--- Premium Voices by Language ---")
    for lang, count in lang_counts.items():
        print(f"  {lang}: {count} voices")
        
    db.close()
    print("=======================================")

if __name__ == "__main__":
    asyncio.run(validate_voices())
