import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from .config import get_settings
from .core.security import hash_password

settings = get_settings()

engine = create_engine(
    settings.DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    from .models.user import User
    from .models.voice import Voice
    from .models.generation import Generation, SystemSettings
    from .models.preset import VoicePreset
    from .models.pronunciation import PronunciationRule
    from .models.batch import BatchJob, BatchItem
    from .models.notification import Notification
    from .models.favorite import FavoriteVoice
    
    # Create directories
    for directory in [settings.UPLOAD_DIR, settings.OUTPUT_DIR, settings.CLONE_DIR, settings.PREVIEW_DIR, "./data/db", "./data/temp_chunks", "./data/outputs/long_form"]:
        os.makedirs(directory, exist_ok=True)
        
    Base.metadata.create_all(bind=engine)
    
    # Auto-migration for SQLite adding long-form fields
    db = SessionLocal()
    try:
        from sqlalchemy import text
        cursor = db.connection()
        # Safe migration for generations table
        try:
            cursor.execute(text("ALTER TABLE generations ADD COLUMN mode VARCHAR(20) DEFAULT 'short_form'"))
            cursor.execute(text("ALTER TABLE generations ADD COLUMN total_chunks INTEGER DEFAULT 1"))
            cursor.execute(text("ALTER TABLE generations ADD COLUMN completed_chunks INTEGER DEFAULT 0"))
            cursor.execute(text("ALTER TABLE generations ADD COLUMN progress FLOAT DEFAULT 100.0"))
            cursor.execute(text("ALTER TABLE generations ADD COLUMN error_message TEXT"))
        except Exception:
            pass # Columns likely already exist
            
        try:
            cursor.execute(text("ALTER TABLE generations ADD COLUMN project_id INTEGER"))
            cursor.execute(text("ALTER TABLE generations ADD COLUMN batch_id INTEGER"))
            cursor.execute(text("ALTER TABLE generations ADD COLUMN is_favorite BOOLEAN DEFAULT 0"))
        except Exception:
            pass # Columns likely already exist
        except Exception:
            pass # Columns likely already exist
            
        # Safe migration for voices table
        try:
            cursor.execute(text("ALTER TABLE voices ADD COLUMN use_case_tags VARCHAR(500) DEFAULT '[]'"))
            cursor.execute(text("ALTER TABLE voices ADD COLUMN tone_tags VARCHAR(500) DEFAULT '[]'"))
            cursor.execute(text("ALTER TABLE voices ADD COLUMN recommended_for VARCHAR(500) DEFAULT '[]'"))
            cursor.execute(text("ALTER TABLE voices ADD COLUMN preview_status VARCHAR(20) DEFAULT 'pending'"))
            cursor.execute(text("ALTER TABLE voices ADD COLUMN generation_status VARCHAR(20) DEFAULT 'pending'"))
        except Exception:
            pass # Columns likely already exist
            
        db.commit()
    except Exception as e:
        print(f"Migration error: {e}")
        db.rollback()
    finally:
        db.close()
    
    db = SessionLocal()
    try:
        # Seed Admin User
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            admin = User(
                username="admin",
                email="admin@voxforge.local",
                password_hash=hash_password("admin123"),
                role="admin",
                char_quota=500000
            )
            db.add(admin)
            
        # Seed Demo User
        demo = db.query(User).filter(User.username == "demo").first()
        if not demo:
            demo = User(
                username="demo",
                email="demo@voxforge.local",
                password_hash=hash_password("demo123"),
                role="user",
                char_quota=50000
            )
            db.add(demo)
            
        # Seed Settings
        if db.query(SystemSettings).count() == 0:
            db.add(SystemSettings(key="default_char_quota", value=str(settings.DEFAULT_CHAR_QUOTA), category="quota"))
            db.add(SystemSettings(key="max_text_length", value=str(settings.MAX_TEXT_LENGTH), category="limits"))
            db.add(SystemSettings(key="max_upload_size", value=str(settings.MAX_UPLOAD_SIZE), category="limits"))
            
        # Seed Curated Voices using safe repair system
        from .utils.voice_validation import seed_or_repair_voices
        seed_or_repair_voices(db)
        
        db.commit()
    finally:
        db.close()

def seed_voices(db):
    from .models.voice import Voice
    if db.query(Voice).filter(Voice.is_builtin == True).count() > 0:
        return
        
    CURATED_VOICES = [
        {"name": "Aria", "voice_id": "en-US-AriaNeural", "engine": "edge-tts", "language": "English", "locale": "en-US", "gender": "Female", "style": "conversational", "category": "neural", "quality_label": "Premium", "accent": "American", "use_case": "Conversational, YouTube", "tags": '["Premium", "Conversational"]', "description": "Warm and engaging female voice."},
        {"name": "Jenny", "voice_id": "en-US-JennyNeural", "engine": "edge-tts", "language": "English", "locale": "en-US", "gender": "Female", "style": "narration", "category": "neural", "quality_label": "Premium", "accent": "American", "use_case": "Narration, Commercial", "tags": '["Premium", "Narration"]', "description": "Clear and professional female voice."},
        {"name": "Ana", "voice_id": "en-US-AnaNeural", "engine": "edge-tts", "language": "English", "locale": "en-US", "gender": "Female", "style": "friendly", "category": "neural", "quality_label": "Standard", "accent": "American", "use_case": "Friendly, Casual", "tags": '["Friendly", "Casual"]', "description": "Friendly and approachable female voice."},
        {"name": "Ava", "voice_id": "en-US-AvaNeural", "engine": "edge-tts", "language": "English", "locale": "en-US", "gender": "Female", "style": "professional", "category": "neural", "quality_label": "Standard", "accent": "American", "use_case": "Professional, Business", "tags": '["Professional", "Business"]', "description": "Professional female voice."},
        {"name": "Emma", "voice_id": "en-US-EmmaNeural", "engine": "edge-tts", "language": "English", "locale": "en-US", "gender": "Female", "style": "clear", "category": "neural", "quality_label": "Premium", "accent": "American", "use_case": "Presentations, Clear", "tags": '["Premium", "Clear"]', "description": "Crystal clear female voice."},
        {"name": "Michelle", "voice_id": "en-US-MichelleNeural", "engine": "edge-tts", "language": "English", "locale": "en-US", "gender": "Female", "style": "warm", "category": "neural", "quality_label": "Premium", "accent": "American", "use_case": "Podcast, Warm", "tags": '["Premium", "Warm"]', "description": "Warm conversational female voice."},
        
        {"name": "Guy", "voice_id": "en-US-GuyNeural", "engine": "edge-tts", "language": "English", "locale": "en-US", "gender": "Male", "style": "narration", "category": "neural", "quality_label": "Premium", "accent": "American", "use_case": "News, Documentary", "tags": '["Premium", "Documentary"]', "description": "Authoritative male voice."},
        {"name": "Andrew", "voice_id": "en-US-AndrewNeural", "engine": "edge-tts", "language": "English", "locale": "en-US", "gender": "Male", "style": "warm", "category": "neural", "quality_label": "Premium", "accent": "American", "use_case": "Storytelling, Warm", "tags": '["Premium", "Storytelling"]', "description": "Warm male narrator voice."},
        {"name": "Brian", "voice_id": "en-US-BrianNeural", "engine": "edge-tts", "language": "English", "locale": "en-US", "gender": "Male", "style": "deep", "category": "neural", "quality_label": "Premium", "accent": "American", "use_case": "YouTube, Deep", "tags": '["Premium", "Deep"]', "description": "Rich deep male voice."},
        {"name": "Christopher", "voice_id": "en-US-ChristopherNeural", "engine": "edge-tts", "language": "English", "locale": "en-US", "gender": "Male", "style": "professional", "category": "neural", "quality_label": "Standard", "accent": "American", "use_case": "Business, Professional", "tags": '["Professional", "Business"]', "description": "Professional male voice."},
        {"name": "Eric", "voice_id": "en-US-EricNeural", "engine": "edge-tts", "language": "English", "locale": "en-US", "gender": "Male", "style": "energetic", "category": "neural", "quality_label": "Standard", "accent": "American", "use_case": "Energetic, Marketing", "tags": '["Energetic", "Marketing"]', "description": "Energetic male voice."},
        {"name": "Roger", "voice_id": "en-US-RogerNeural", "engine": "edge-tts", "language": "English", "locale": "en-US", "gender": "Male", "style": "formal", "category": "neural", "quality_label": "Premium", "accent": "American", "use_case": "Formal, News", "tags": '["Premium", "Formal"]', "description": "Formal male voice."},
        {"name": "Steffan", "voice_id": "en-US-SteffanNeural", "engine": "edge-tts", "language": "English", "locale": "en-US", "gender": "Male", "style": "cinematic", "category": "neural", "quality_label": "Premium", "accent": "American", "use_case": "Cinematic, Trailer", "tags": '["Premium", "Cinematic"]', "description": "Cinematic male voice."},

        {"name": "Libby", "voice_id": "en-GB-LibbyNeural", "engine": "edge-tts", "language": "English", "locale": "en-GB", "gender": "Female", "style": "warm", "category": "neural", "quality_label": "Premium", "accent": "British", "use_case": "Audiobook, Warm", "tags": '["Premium", "British"]', "description": "Warm British female voice."},
        {"name": "Sonia", "voice_id": "en-GB-SoniaNeural", "engine": "edge-tts", "language": "English", "locale": "en-GB", "gender": "Female", "style": "professional", "category": "neural", "quality_label": "Premium", "accent": "British", "use_case": "Narration, Professional", "tags": '["Premium", "British"]', "description": "Professional British female voice."},
        {"name": "Ryan", "voice_id": "en-GB-RyanNeural", "engine": "edge-tts", "language": "English", "locale": "en-GB", "gender": "Male", "style": "professional", "category": "neural", "quality_label": "Premium", "accent": "British", "use_case": "Documentary, Professional", "tags": '["Premium", "British"]', "description": "Refined British male voice."},

        {"name": "Salma", "voice_id": "ar-EG-SalmaNeural", "engine": "edge-tts", "language": "Arabic", "locale": "ar-EG", "gender": "Female", "style": "professional", "category": "neural", "quality_label": "Premium", "accent": "Egyptian", "use_case": "Narration, Professional", "tags": '["Premium", "Arabic"]', "description": "Clear Egyptian Arabic female voice."},
        {"name": "Zariyah", "voice_id": "ar-SA-ZariyahNeural", "engine": "edge-tts", "language": "Arabic", "locale": "ar-SA", "gender": "Female", "style": "formal", "category": "neural", "quality_label": "Premium", "accent": "Saudi", "use_case": "News, Formal", "tags": '["Premium", "Arabic"]', "description": "Formal Saudi Arabic female voice."},
        {"name": "Shakir", "voice_id": "ar-EG-ShakirNeural", "engine": "edge-tts", "language": "Arabic", "locale": "ar-EG", "gender": "Male", "style": "warm", "category": "neural", "quality_label": "Premium", "accent": "Egyptian", "use_case": "Storytelling, Warm", "tags": '["Premium", "Arabic"]', "description": "Warm Egyptian Arabic male voice."},
        {"name": "Hamed", "voice_id": "ar-SA-HamedNeural", "engine": "edge-tts", "language": "Arabic", "locale": "ar-SA", "gender": "Male", "style": "professional", "category": "neural", "quality_label": "Premium", "accent": "Saudi", "use_case": "Corporate, Professional", "tags": '["Premium", "Arabic"]', "description": "Professional Saudi Arabic male voice."},

        {"name": "Elvira", "voice_id": "es-ES-ElviraNeural", "engine": "edge-tts", "language": "Spanish", "locale": "es-ES", "gender": "Female", "style": "professional", "category": "neural", "quality_label": "Premium", "accent": "Castilian", "use_case": "Narration", "tags": '["Premium", "Spanish"]', "description": "Elegant Castilian Spanish female voice."},
        {"name": "Alvaro", "voice_id": "es-ES-AlvaroNeural", "engine": "edge-tts", "language": "Spanish", "locale": "es-ES", "gender": "Male", "style": "professional", "category": "neural", "quality_label": "Premium", "accent": "Castilian", "use_case": "Documentary", "tags": '["Premium", "Spanish"]', "description": "Professional Castilian Spanish male voice."},
        {"name": "Dalia", "voice_id": "es-MX-DaliaNeural", "engine": "edge-tts", "language": "Spanish", "locale": "es-MX", "gender": "Female", "style": "warm", "category": "neural", "quality_label": "Premium", "accent": "Mexican", "use_case": "Conversational", "tags": '["Premium", "Spanish"]', "description": "Warm Mexican Spanish female voice."},
        {"name": "Jorge", "voice_id": "es-MX-JorgeNeural", "engine": "edge-tts", "language": "Spanish", "locale": "es-MX", "gender": "Male", "style": "professional", "category": "neural", "quality_label": "Premium", "accent": "Mexican", "use_case": "Corporate", "tags": '["Premium", "Spanish"]', "description": "Professional Mexican Spanish male voice."},

        {"name": "Denise", "voice_id": "fr-FR-DeniseNeural", "engine": "edge-tts", "language": "French", "locale": "fr-FR", "gender": "Female", "style": "elegant", "category": "neural", "quality_label": "Premium", "accent": "French", "use_case": "Elegant", "tags": '["Premium", "French"]', "description": "Elegant French female voice."},
        {"name": "Henri", "voice_id": "fr-FR-HenriNeural", "engine": "edge-tts", "language": "French", "locale": "fr-FR", "gender": "Male", "style": "professional", "category": "neural", "quality_label": "Premium", "accent": "French", "use_case": "Narration", "tags": '["Premium", "French"]', "description": "Professional French male voice."},

        {"name": "Katja", "voice_id": "de-DE-KatjaNeural", "engine": "edge-tts", "language": "German", "locale": "de-DE", "gender": "Female", "style": "professional", "category": "neural", "quality_label": "Premium", "accent": "German", "use_case": "Corporate", "tags": '["Premium", "German"]', "description": "Professional German female voice."},
        {"name": "Conrad", "voice_id": "de-DE-ConradNeural", "engine": "edge-tts", "language": "German", "locale": "de-DE", "gender": "Male", "style": "professional", "category": "neural", "quality_label": "Premium", "accent": "German", "use_case": "Documentary", "tags": '["Premium", "German"]', "description": "Professional German male voice."},
        
        {"name": "Elsa", "voice_id": "it-IT-ElsaNeural", "engine": "edge-tts", "language": "Italian", "locale": "it-IT", "gender": "Female", "style": "warm", "category": "neural", "quality_label": "Premium", "accent": "Italian", "use_case": "Warm", "tags": '["Premium", "Italian"]', "description": "Warm Italian female voice."},
        {"name": "Diego", "voice_id": "it-IT-DiegoNeural", "engine": "edge-tts", "language": "Italian", "locale": "it-IT", "gender": "Male", "style": "professional", "category": "neural", "quality_label": "Premium", "accent": "Italian", "use_case": "Narration", "tags": '["Premium", "Italian"]', "description": "Professional Italian male voice."}
    ]

    for v in CURATED_VOICES:
        voice = Voice(
            **v,
            is_builtin=True,
            is_active=True,
            is_cloned=False
        )
        db.add(voice)
