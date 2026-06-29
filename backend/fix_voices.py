import asyncio
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models.voice import Voice
from app.services.tts_engines import engine_manager

CURATED_VOICES = [
    # English (US)
    {"name": "Aria", "voice_id": "en-US-AriaNeural", "engine": "edge-tts", "language": "English", "locale": "en-US", "gender": "Female", "style": "conversational", "category": "neural", "quality_label": "Premium", "accent": "American", "use_case": "Conversational, YouTube", "tags": '["Premium", "Conversational", "YouTube"]', "description": "Warm and engaging female voice."},
    {"name": "Jenny", "voice_id": "en-US-JennyNeural", "engine": "edge-tts", "language": "English", "locale": "en-US", "gender": "Female", "style": "narration", "category": "neural", "quality_label": "Premium", "accent": "American", "use_case": "Narration, Commercial", "tags": '["Premium", "Narration", "Commercial"]', "description": "Clear and professional female voice."},
    {"name": "Ana", "voice_id": "en-US-AnaNeural", "engine": "edge-tts", "language": "English", "locale": "en-US", "gender": "Female", "style": "friendly", "category": "neural", "quality_label": "Standard", "accent": "American", "use_case": "Friendly, Casual", "tags": '["Friendly", "Casual"]', "description": "Friendly and approachable female voice."},
    {"name": "Ava", "voice_id": "en-US-AvaNeural", "engine": "edge-tts", "language": "English", "locale": "en-US", "gender": "Female", "style": "professional", "category": "neural", "quality_label": "Standard", "accent": "American", "use_case": "Professional, Business", "tags": '["Professional", "Business"]', "description": "Professional female voice."},
    {"name": "Emma", "voice_id": "en-US-EmmaNeural", "engine": "edge-tts", "language": "English", "locale": "en-US", "gender": "Female", "style": "clear", "category": "neural", "quality_label": "Premium", "accent": "American", "use_case": "Presentations", "tags": '["Premium", "Clear", "Education"]', "description": "Crystal clear female voice."},
    {"name": "Michelle", "voice_id": "en-US-MichelleNeural", "engine": "edge-tts", "language": "English", "locale": "en-US", "gender": "Female", "style": "warm", "category": "neural", "quality_label": "Premium", "accent": "American", "use_case": "Podcast", "tags": '["Premium", "Warm", "Podcast"]', "description": "Warm conversational female voice."},
    {"name": "Guy", "voice_id": "en-US-GuyNeural", "engine": "edge-tts", "language": "English", "locale": "en-US", "gender": "Male", "style": "narration", "category": "neural", "quality_label": "Premium", "accent": "American", "use_case": "News, Documentary", "tags": '["Premium", "Documentary", "News"]', "description": "Authoritative male voice."},
    {"name": "Andrew", "voice_id": "en-US-AndrewNeural", "engine": "edge-tts", "language": "English", "locale": "en-US", "gender": "Male", "style": "warm", "category": "neural", "quality_label": "Premium", "accent": "American", "use_case": "Storytelling, Warm", "tags": '["Premium", "Storytelling", "Audiobook"]', "description": "Warm male narrator voice."},
    {"name": "Brian", "voice_id": "en-US-BrianNeural", "engine": "edge-tts", "language": "English", "locale": "en-US", "gender": "Male", "style": "deep", "category": "neural", "quality_label": "Premium", "accent": "American", "use_case": "YouTube, Deep", "tags": '["Premium", "Deep", "YouTube"]', "description": "Rich deep male voice."},
    {"name": "Christopher", "voice_id": "en-US-ChristopherNeural", "engine": "edge-tts", "language": "English", "locale": "en-US", "gender": "Male", "style": "professional", "category": "neural", "quality_label": "Standard", "accent": "American", "use_case": "Business", "tags": '["Professional", "Business"]', "description": "Professional male voice."},
    {"name": "Eric", "voice_id": "en-US-EricNeural", "engine": "edge-tts", "language": "English", "locale": "en-US", "gender": "Male", "style": "energetic", "category": "neural", "quality_label": "Standard", "accent": "American", "use_case": "Marketing", "tags": '["Energetic", "Marketing"]', "description": "Energetic male voice."},
    {"name": "Roger", "voice_id": "en-US-RogerNeural", "engine": "edge-tts", "language": "English", "locale": "en-US", "gender": "Male", "style": "formal", "category": "neural", "quality_label": "Premium", "accent": "American", "use_case": "Formal, News", "tags": '["Premium", "Formal"]', "description": "Formal male voice."},
    {"name": "Steffan", "voice_id": "en-US-SteffanNeural", "engine": "edge-tts", "language": "English", "locale": "en-US", "gender": "Male", "style": "cinematic", "category": "neural", "quality_label": "Premium", "accent": "American", "use_case": "Trailer", "tags": '["Premium", "Cinematic"]', "description": "Cinematic male voice."},

    # English (UK)
    {"name": "Libby", "voice_id": "en-GB-LibbyNeural", "engine": "edge-tts", "language": "English", "locale": "en-GB", "gender": "Female", "style": "warm", "category": "neural", "quality_label": "Premium", "accent": "British", "use_case": "Audiobook", "tags": '["Premium", "British"]', "description": "Warm British female voice."},
    {"name": "Sonia", "voice_id": "en-GB-SoniaNeural", "engine": "edge-tts", "language": "English", "locale": "en-GB", "gender": "Female", "style": "professional", "category": "neural", "quality_label": "Premium", "accent": "British", "use_case": "Narration", "tags": '["Premium", "British", "Narration"]', "description": "Professional British female voice."},
    {"name": "Ryan", "voice_id": "en-GB-RyanNeural", "engine": "edge-tts", "language": "English", "locale": "en-GB", "gender": "Male", "style": "professional", "category": "neural", "quality_label": "Premium", "accent": "British", "use_case": "Documentary", "tags": '["Premium", "British", "Documentary"]', "description": "Refined British male voice."},

    # Arabic (Egyptian & Saudi & UAE)
    {"name": "Salma", "voice_id": "ar-EG-SalmaNeural", "engine": "edge-tts", "language": "Arabic", "locale": "ar-EG", "gender": "Female", "style": "professional", "category": "neural", "quality_label": "Premium", "accent": "Egyptian", "use_case": "Narration", "tags": '["Premium", "Arabic", "Female"]', "description": "Clear Egyptian Arabic female voice."},
    {"name": "Zariyah", "voice_id": "ar-SA-ZariyahNeural", "engine": "edge-tts", "language": "Arabic", "locale": "ar-SA", "gender": "Female", "style": "formal", "category": "neural", "quality_label": "Premium", "accent": "Saudi", "use_case": "News", "tags": '["Premium", "Arabic", "Female"]', "description": "Formal Saudi Arabic female voice."},
    {"name": "Shakir", "voice_id": "ar-EG-ShakirNeural", "engine": "edge-tts", "language": "Arabic", "locale": "ar-EG", "gender": "Male", "style": "warm", "category": "neural", "quality_label": "Premium", "accent": "Egyptian", "use_case": "Storytelling", "tags": '["Premium", "Arabic", "Male"]', "description": "Warm Egyptian Arabic male voice."},
    {"name": "Hamed", "voice_id": "ar-SA-HamedNeural", "engine": "edge-tts", "language": "Arabic", "locale": "ar-SA", "gender": "Male", "style": "professional", "category": "neural", "quality_label": "Premium", "accent": "Saudi", "use_case": "Corporate", "tags": '["Premium", "Arabic", "Male"]', "description": "Professional Saudi Arabic male voice."},
    {"name": "Fatima", "voice_id": "ar-AE-FatimaNeural", "engine": "edge-tts", "language": "Arabic", "locale": "ar-AE", "gender": "Female", "style": "conversational", "category": "neural", "quality_label": "Premium", "accent": "Emirati", "use_case": "Conversational", "tags": '["Premium", "Arabic", "Female"]', "description": "Conversational Emirati Arabic female voice."},
    {"name": "Hamdan", "voice_id": "ar-AE-HamdanNeural", "engine": "edge-tts", "language": "Arabic", "locale": "ar-AE", "gender": "Male", "style": "narration", "category": "neural", "quality_label": "Premium", "accent": "Emirati", "use_case": "Narration", "tags": '["Premium", "Arabic", "Male"]', "description": "Narration Emirati Arabic male voice."},

    # Spanish
    {"name": "Elvira", "voice_id": "es-ES-ElviraNeural", "engine": "edge-tts", "language": "Spanish", "locale": "es-ES", "gender": "Female", "style": "professional", "category": "neural", "quality_label": "Premium", "accent": "Castilian", "use_case": "Narration", "tags": '["Premium", "Spanish"]', "description": "Elegant Castilian Spanish female voice."},
    {"name": "Alvaro", "voice_id": "es-ES-AlvaroNeural", "engine": "edge-tts", "language": "Spanish", "locale": "es-ES", "gender": "Male", "style": "professional", "category": "neural", "quality_label": "Premium", "accent": "Castilian", "use_case": "Documentary", "tags": '["Premium", "Spanish"]', "description": "Professional Castilian Spanish male voice."},
    {"name": "Dalia", "voice_id": "es-MX-DaliaNeural", "engine": "edge-tts", "language": "Spanish", "locale": "es-MX", "gender": "Female", "style": "warm", "category": "neural", "quality_label": "Premium", "accent": "Mexican", "use_case": "Conversational", "tags": '["Premium", "Spanish"]', "description": "Warm Mexican Spanish female voice."},
    {"name": "Jorge", "voice_id": "es-MX-JorgeNeural", "engine": "edge-tts", "language": "Spanish", "locale": "es-MX", "gender": "Male", "style": "professional", "category": "neural", "quality_label": "Premium", "accent": "Mexican", "use_case": "Corporate", "tags": '["Premium", "Spanish"]', "description": "Professional Mexican Spanish male voice."},

    # French
    {"name": "Denise", "voice_id": "fr-FR-DeniseNeural", "engine": "edge-tts", "language": "French", "locale": "fr-FR", "gender": "Female", "style": "elegant", "category": "neural", "quality_label": "Premium", "accent": "French", "use_case": "Elegant", "tags": '["Premium", "French"]', "description": "Elegant French female voice."},
    {"name": "Henri", "voice_id": "fr-FR-HenriNeural", "engine": "edge-tts", "language": "French", "locale": "fr-FR", "gender": "Male", "style": "professional", "category": "neural", "quality_label": "Premium", "accent": "French", "use_case": "Narration", "tags": '["Premium", "French"]', "description": "Professional French male voice."},

    # German
    {"name": "Katja", "voice_id": "de-DE-KatjaNeural", "engine": "edge-tts", "language": "German", "locale": "de-DE", "gender": "Female", "style": "professional", "category": "neural", "quality_label": "Premium", "accent": "German", "use_case": "Corporate", "tags": '["Premium", "German"]', "description": "Professional German female voice."},
    {"name": "Conrad", "voice_id": "de-DE-ConradNeural", "engine": "edge-tts", "language": "German", "locale": "de-DE", "gender": "Male", "style": "professional", "category": "neural", "quality_label": "Premium", "accent": "German", "use_case": "Documentary", "tags": '["Premium", "German"]', "description": "Professional German male voice."},
    
    # Italian
    {"name": "Elsa", "voice_id": "it-IT-ElsaNeural", "engine": "edge-tts", "language": "Italian", "locale": "it-IT", "gender": "Female", "style": "warm", "category": "neural", "quality_label": "Premium", "accent": "Italian", "use_case": "Warm", "tags": '["Premium", "Italian"]', "description": "Warm Italian female voice."},
    {"name": "Diego", "voice_id": "it-IT-DiegoNeural", "engine": "edge-tts", "language": "Italian", "locale": "it-IT", "gender": "Male", "style": "professional", "category": "neural", "quality_label": "Premium", "accent": "Italian", "use_case": "Narration", "tags": '["Premium", "Italian"]', "description": "Professional Italian male voice."}
]

async def update_voices():
    db = SessionLocal()
    try:
        print("Checking Edge-TTS support for curated voices...")
        edge = engine_manager.get_engine("edge-tts")
        available = await edge.is_available()
        if not available:
            print("Edge-TTS engine is not available on this machine!")
            return
            
        print("Deleting old built-in voices from database...")
        db.query(Voice).filter(Voice.is_builtin == True).delete()
        db.commit()
        
        print("Inserting validated curated voices...")
        for v in CURATED_VOICES:
            voice = Voice(
                **v,
                is_builtin=True,
                is_active=True,
                is_cloned=False
            )
            db.add(voice)
        db.commit()
        print(f"Successfully seeded {len(CURATED_VOICES)} validated voices!")
        
    except Exception as e:
        print("Error updating voices:", str(e))
    finally:
        db.close()

if __name__ == '__main__':
    asyncio.run(update_voices())
