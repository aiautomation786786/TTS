from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..core.dependencies import get_db, get_current_user
from ..schemas.generation import GenerationListResponse, GenerationResponse
from ..models.generation import Generation
import os

router = APIRouter(prefix="/api/history", tags=["History"])

@router.get("/", response_model=GenerationListResponse)
async def list_history(
    page: int = 1, per_page: int = 50, search: str = None, 
    voice_id: int = None, mode: str = None, project_id: int = None,
    is_favorite: bool = None,
    db: Session = Depends(get_db), current_user = Depends(get_current_user)
):
    skip = (page - 1) * per_page
    query = db.query(Generation).filter(Generation.user_id == current_user.id)
    
    if search:
        query = query.filter(Generation.text.contains(search))
    if voice_id:
        query = query.filter(Generation.voice_id == voice_id)
    if mode:
        query = query.filter(Generation.mode == mode)
    if project_id is not None:
        query = query.filter(Generation.project_id == project_id)
    if is_favorite is not None:
        query = query.filter(Generation.is_favorite == is_favorite)
        
    query = query.order_by(Generation.created_at.desc())
    total = query.count()
    generations = query.offset(skip).limit(per_page).all()
    
    # Add URLs
    for g in generations:
        if g.audio_path:
            # Check if long_form or short_form based on directory
            if "long_form" in g.audio_path:
                g.audio_url = f"/api/audio/outputs/long_form/{os.path.basename(g.audio_path)}"
            else:
                g.audio_url = f"/api/audio/outputs/{os.path.basename(g.audio_path)}"
            
    return {"generations": generations, "total": total, "page": page, "per_page": per_page}

@router.get("/{generation_id}", response_model=GenerationResponse)
async def get_generation(generation_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    gen = db.query(Generation).filter(Generation.id == generation_id, Generation.user_id == current_user.id).first()
    if not gen:
        raise HTTPException(status_code=404, detail="Generation not found")
    if gen.audio_path:
        if "long_form" in gen.audio_path:
            gen.audio_url = f"/api/audio/outputs/long_form/{os.path.basename(gen.audio_path)}"
        else:
            gen.audio_url = f"/api/audio/outputs/{os.path.basename(gen.audio_path)}"
    return gen

@router.put("/{generation_id}/favorite")
async def toggle_favorite(generation_id: int, is_favorite: bool, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    gen = db.query(Generation).filter(Generation.id == generation_id, Generation.user_id == current_user.id).first()
    if not gen:
        raise HTTPException(status_code=404, detail="Generation not found")
    gen.is_favorite = is_favorite
    db.commit()
    return {"message": "Favorite updated"}

@router.delete("/{generation_id}")
async def delete_generation(generation_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    gen = db.query(Generation).filter(Generation.id == generation_id, Generation.user_id == current_user.id).first()
    if not gen:
        raise HTTPException(status_code=404, detail="Generation not found")
        
    if gen.audio_path and os.path.exists(gen.audio_path):
        os.remove(gen.audio_path)
        
    db.delete(gen)
    db.commit()
    return {"message": "Deleted successfully"}

from fastapi.responses import FileResponse
import subprocess

@router.get("/{generation_id}/download")
async def download_generation(
    generation_id: int, 
    format: str = Query("mp3", regex="^(mp3|wav)$"),
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_user)
):
    gen = db.query(Generation).filter(Generation.id == generation_id).first()
    if not gen:
        raise HTTPException(status_code=404, detail="Generation not found")
        
    # Only owner or admin can download
    if gen.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
        
    if gen.status != "completed" or not gen.audio_path or not os.path.exists(gen.audio_path):
        raise HTTPException(status_code=400, detail="Audio file not available or generation failed.")
        
    source_ext = os.path.splitext(gen.audio_path)[1].lower().strip(".")
    requested_ext = format.lower()
    
    if gen.mode == "long_form":
        filename = f"voxforge_longform_{gen.id}.{requested_ext}"
    elif gen.mode == "cloned":
        filename = f"voxforge_cloned_{gen.id}.{requested_ext}"
    else:
        filename = f"voxforge_shortform_{gen.id}.{requested_ext}"
        
    if source_ext == requested_ext:
        media_type = "audio/wav" if requested_ext == "wav" else "audio/mpeg"
        return FileResponse(gen.audio_path, media_type=media_type, filename=filename)
        
    # Conversion needed
    converted_path = f"{os.path.splitext(gen.audio_path)[0]}_converted.{requested_ext}"
    
    if not os.path.exists(converted_path):
        # Run FFmpeg
        try:
            result = subprocess.run(
                ["ffmpeg", "-y", "-i", gen.audio_path, converted_path],
                capture_output=True, text=True, check=True
            )
        except FileNotFoundError:
            raise HTTPException(status_code=500, detail="FFmpeg is not installed on the server.")
        except subprocess.CalledProcessError as e:
            raise HTTPException(status_code=500, detail=f"Conversion failed: {e.stderr}")
            
    media_type = "audio/wav" if requested_ext == "wav" else "audio/mpeg"
    return FileResponse(converted_path, media_type=media_type, filename=filename)
