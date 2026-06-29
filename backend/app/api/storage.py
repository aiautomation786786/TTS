from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
import os

from ..core.dependencies import get_db, get_current_user
from ..config import get_settings
from ..models.generation import Generation

router = APIRouter(prefix="/api/storage", tags=["Storage"])
settings = get_settings()

def get_dir_size(path: str):
    total_size = 0
    file_count = 0
    if not os.path.exists(path):
        return 0, 0
    for dirpath, _, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)
                file_count += 1
    return total_size, file_count

def clear_dir(path: str):
    if not os.path.exists(path):
        return
    for root, dirs, files in os.walk(path):
        for f in files:
            try:
                os.unlink(os.path.join(root, f))
            except Exception:
                pass

class StorageClearRequest(BaseModel):
    categories: List[str]

@router.get("/")
async def get_storage_stats(current_user = Depends(get_current_user)):
    stats = {}
    
    # History
    history_size, history_count = get_dir_size(settings.OUTPUT_DIR)
    stats["history"] = {"size_bytes": history_size, "file_count": history_count, "label": "Audio History", "desc": "Generated audio files (.wav)"}
    
    # Models
    models_path = "./models/piper"
    models_size, models_count = get_dir_size(models_path)
    stats["models"] = {"size_bytes": models_size, "file_count": models_count, "label": "Voice Models", "desc": "Downloaded standard voices"}
    
    # Uploads (Clone References)
    uploads_size, uploads_count = get_dir_size(settings.UPLOAD_DIR)
    stats["uploads"] = {"size_bytes": uploads_size, "file_count": uploads_count, "label": "Clone Uploads", "desc": "Reference audio used for cloning"}
    
    # Temp Cache
    temp_size, temp_count = get_dir_size(settings.TEMP_CHUNK_DIR)
    stats["temp"] = {"size_bytes": temp_size, "file_count": temp_count, "label": "Temp Cache", "desc": "Temporary processing chunks"}
    
    return stats

@router.post("/clear")
async def clear_storage(request: StorageClearRequest, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    cleared = []
    
    if "history" in request.categories:
        clear_dir(settings.OUTPUT_DIR)
        db.query(Generation).filter(Generation.user_id == current_user.id).delete()
        db.commit()
        cleared.append("history")
        
    if "models" in request.categories:
        clear_dir("./models/piper")
        cleared.append("models")
        
    if "uploads" in request.categories:
        clear_dir(settings.UPLOAD_DIR)
        cleared.append("uploads")
        
    if "temp" in request.categories:
        clear_dir(settings.TEMP_CHUNK_DIR)
        cleared.append("temp")
        
    return {"message": "Storage cleared successfully", "cleared": cleared}
