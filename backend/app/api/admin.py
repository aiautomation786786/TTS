from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..core.dependencies import get_db
from ..models.user import User
from ..models.voice import Voice
from ..models.generation import Generation
from ..services.tts_engines import engine_manager
from ..services.clone_service import clone_service
import os

router = APIRouter(prefix="/api/admin", tags=["Dashboard Engine Status"])

@router.get("/dashboard")
async def get_dashboard(db: Session = Depends(get_db)):
    total_chars_tuple = db.query(func.sum(Generation.char_count)).first()
    total_chars = total_chars_tuple[0] if total_chars_tuple and total_chars_tuple[0] else 0

    return {
        "total_generations": db.query(Generation).count(),
        "short_form_generations": db.query(Generation).filter(Generation.mode == "short_form").count(),
        "long_form_generations": db.query(Generation).filter(Generation.mode == "long_form").count(),
        "total_characters": total_chars,
        "total_duration": db.query(func.sum(Generation.audio_duration)).first()[0] or 0.0,
        "total_storage": db.query(func.sum(Generation.file_size)).first()[0] or 0,
        "total_clones": db.query(Voice).filter(Voice.is_cloned == True).count(),
        "total_voices": db.query(Voice).count(),
        "active_voices": db.query(Voice).filter(Voice.is_active == True).count(),
        "broken_voices": db.query(Voice).filter(Voice.is_active == False).count(),
        "long_form_success_rate": calculate_success_rate(db, "long_form")
    }

def calculate_success_rate(db: Session, mode: str):
    total = db.query(Generation).filter(Generation.mode == mode).count()
    if total == 0: return 100.0
    failed = db.query(Generation).filter(Generation.mode == mode, Generation.status == "failed").count()
    return round(((total - failed) / total) * 100, 2)

@router.get("/engine-status")
async def get_engine_status():
    engines = await engine_manager.get_all_status()
    clone_info = await clone_service.check_availability()
    from ..config import get_settings
    settings = get_settings()
    
    preview_write = os.access(settings.PREVIEW_DIR, os.W_OK)
    output_write = os.access(settings.OUTPUT_DIR, os.W_OK)
    
    return {
        "coqui_status": clone_info,
        "preview_storage_path": os.path.abspath(settings.PREVIEW_DIR),
        "output_storage_path": os.path.abspath(settings.OUTPUT_DIR),
        "preview_folder_writable": preview_write,
        "output_folder_writable": output_write,
        "static_serving_active": True,
        "engines": engines
    }
