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
        
    if "uploads" in request.categories:
        clear_dir(settings.UPLOAD_DIR)
        cleared.append("uploads")
        
    if "temp" in request.categories:
        clear_dir(settings.TEMP_CHUNK_DIR)
        cleared.append("temp")
        
    return {"message": "Storage cleared successfully", "cleared": cleared}

class StorageClearFilesRequest(BaseModel):
    files: List[str]

@router.get("/{category}/files")
async def get_category_files(category: str, current_user = Depends(get_current_user)):
    path = ""
    if category == "history":
        path = settings.OUTPUT_DIR
    elif category == "uploads":
        path = settings.UPLOAD_DIR
    elif category == "temp":
        path = settings.TEMP_CHUNK_DIR
    else:
        return {"files": []}

    files_list = []
    if os.path.exists(path):
        for root, _, filenames in os.walk(path):
            for f in filenames:
                fp = os.path.join(root, f)
                if not os.path.islink(fp):
                    try:
                        stat = os.stat(fp)
                        rel_path = os.path.relpath(fp, path)
                        # Replace backslashes with forward slashes for safety
                        rel_path = rel_path.replace("\\", "/")
                        files_list.append({
                            "id": rel_path,
                            "name": f,
                            "size_bytes": stat.st_size,
                            "modified_at": stat.st_mtime
                        })
                    except Exception:
                        pass
    return {"files": files_list}

@router.post("/{category}/clear_files")
async def clear_category_files(category: str, request: StorageClearFilesRequest, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    base_path = ""
    if category == "history":
        base_path = settings.OUTPUT_DIR
    elif category == "uploads":
        base_path = settings.UPLOAD_DIR
    elif category == "temp":
        base_path = settings.TEMP_CHUNK_DIR
    else:
        return {"message": "Invalid category"}

    if not os.path.exists(base_path):
        return {"message": "Nothing to clear"}

    deleted = 0
    for file_id in request.files:
        if ".." in file_id or file_id.startswith("/") or file_id.startswith("\\"):
            continue
        
        target_path = os.path.join(base_path, file_id)
        if os.path.exists(target_path) and os.path.isfile(target_path):
            try:
                os.unlink(target_path)
                deleted += 1
                
                if category == "history":
                    filename = os.path.basename(target_path)
                    db.query(Generation).filter(Generation.file_path.endswith(filename)).delete(synchronize_session=False)
            except Exception:
                pass
    
    if category == "history" and deleted > 0:
        db.commit()
        
    return {"message": f"Deleted {deleted} files"}
