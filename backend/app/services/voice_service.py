from sqlalchemy.orm import Session
import os
from ..models.voice import Voice
from ..config import get_settings
from ..utils.audio import generate_output_filename
from .tts_engines import engine_manager

def get_voices(db: Session, filters: dict, skip: int = 0, limit: int = 100):
    query = db.query(Voice).filter(Voice.is_active == True)
    
    if filters.get("language"):
        query = query.filter(Voice.language == filters["language"])
    if filters.get("gender"):
        query = query.filter(Voice.gender == filters["gender"])
    if filters.get("engine"):
        query = query.filter(Voice.engine == filters["engine"])
    if filters.get("category"):
        query = query.filter(Voice.category == filters["category"])
    if filters.get("use_case"):
        uc = filters["use_case"]
        # use_case_tags is a JSON string array e.g. '["Documentary", "News"]'
        # Using LIKE to find the use case inside the JSON string
        query = query.filter(Voice.use_case_tags.like(f'%"{uc}"%'))
    if filters.get("is_cloned") is not None:
        query = query.filter(Voice.is_cloned == filters["is_cloned"])
    if filters.get("search"):
        search = f"%{filters['search']}%"
        query = query.filter(Voice.name.like(search) | Voice.description.like(search))
        
    total = query.count()
    voices = query.offset(skip).limit(limit).all()
    return voices, total

def get_voice_by_id(db: Session, voice_id: int) -> Voice | None:
    return db.query(Voice).filter(Voice.id == voice_id).first()

def get_user_voices(db: Session, user_id: int) -> list[Voice]:
    return db.query(Voice).filter(Voice.user_id == user_id, Voice.is_cloned == True).all()

def toggle_voice_active(db: Session, voice_id: int) -> Voice | None:
    voice = db.query(Voice).filter(Voice.id == voice_id).first()
    if voice:
        voice.is_active = not voice.is_active
        db.commit()
        db.refresh(voice)
    return voice

def delete_voice(db: Session, voice_id: int) -> bool:
    voice = db.query(Voice).filter(Voice.id == voice_id).first()
    if voice:
        db.delete(voice)
        db.commit()
        return True
    return False

async def get_voice_preview(db: Session, voice_id: int) -> dict | None:
    voice = db.query(Voice).filter(Voice.id == voice_id).first()
    if not voice:
        return None
        
    settings = get_settings()
    preview_dir = settings.PREVIEW_DIR
    
    expected_filename = f"preview_{voice.id}.mp3"
    expected_path = os.path.join(preview_dir, expected_filename)
    
    import time
    timestamp = int(time.time())
    
    # Check if a preview file exists locally
    if os.path.exists(expected_path):
        if not voice.preview_url or '?' not in voice.preview_url:
            voice.preview_url = f"/api/audio/previews/{expected_filename}?t={timestamp}"
            db.commit()
        return {
            "preview_url": voice.preview_url,
        }
        
    # We need to generate a preview
    previews = {
        "Spanish": "Hola, esta es una prueba de mi voz. Puedes usarla para narraciones y audios profesionales.",
        "French": "Bonjour, ceci est un aperçu de ma voix. Vous pouvez l'utiliser pour des narrations et des vidéos.",
        "German": "Hallo, das ist eine Hörprobe meiner Stimme. Sie können sie für Videos und professionelle Audios verwenden.",
        "Arabic": "مرحباً، هذه عينة من صوتي. يمكنك استخدامها في مقاطع الفيديو والتعليقات الصوتية الاحترافية.",
        "Italian": "Ciao, questa è un'anteprima della mia voce. Puoi usarla per narrazioni e video.",
        "Portuguese": "Olá, esta é uma amostra da minha voz. Você pode usá-la para narrações e vídeos.",
        "Russian": "Здравствуйте, это пример моего голоса. Вы можете использовать его для озвучки.",
        "Chinese": "你好，这是我声音的预览。您可以将其用于旁白、视频和专业的音频制作。",
        "Japanese": "こんにちは、これは私の声のサンプルです。ナレーションやビデオに使用できます。",
        "Korean": "안녕하세요, 제 목소리의 미리보기입니다. 내레이션과 비디오에 사용할 수 있습니다.",
        "Hindi": "नमस्ते, यह मेरी आवाज़ का एक नमूना है। आप इसका उपयोग वॉयसओवर और वीडियो के लिए कर सकते हैं।",
        "Turkish": "Merhaba, bu sesimin bir önizlemesi. Bunu videolar ve profesyonel seslendirmeler için kullanabilirsiniz.",
        "Polish": "Cześć, to jest próbka mojego głosu. Możesz jej użyć do narracji i filmów.",
        "Dutch": "Hallo, dit is een voorbeeld van mijn stem. Je kunt het gebruiken voor video's en audio.",
        "Swedish": "Hej, det här är ett smakprov på min röst. Du kan använda den för berättelser och videor.",
        "Urdu": "ہیلو، یہ میری آواز کا ایک نمونہ ہے۔ آپ اسے ویڈیوز اور آڈیو کے لیے استعمال کر سکتے ہیں.",
        "English": "Testing the audio clone. This is a quick voice check to ensure the accent and tone sound completely natural and human."
    }
    
    preview_text = previews.get(voice.language, previews["English"])
        
    if voice.is_cloned and voice.engine == "coqui":
        from .clone_service import clone_service
        try:
            await clone_service.generate_with_clone(preview_text, voice.voice_id, expected_path)
            voice.preview_status = "ready"
        except Exception:
            voice.preview_status = "failed"
            db.commit()
            return None
    elif voice.engine == "edge-tts":
        engine = engine_manager.get_engine("edge-tts")
        if engine:
            await engine.generate(preview_text, voice.voice_id, speed=1.0, pitch="+0Hz", output_path=expected_path)
            voice.preview_status = "ready"
    else:
        try:
            engine = engine_manager.get_engine(voice.engine)
            if not await engine.is_available():
                return None
            await engine.generate(preview_text, voice.voice_id, speed=1.0, pitch="+0Hz", output_path=expected_path)
        except Exception:
            return None
            
    if os.path.exists(expected_path):
        voice.preview_url = f"/api/audio/previews/{expected_filename}?t={timestamp}"
        db.commit()
        return {
            "preview_url": voice.preview_url,
            "cached": False,
            "engine": voice.engine,
            "voice_id": voice.voice_id
        }
        
    return None
