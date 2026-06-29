from fastapi import APIRouter, Depends, Query, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from ..core.dependencies import get_db, get_current_user
from ..schemas.voice import VoiceListResponse, VoiceResponse
from ..services.voice_service import get_voices, get_voice_by_id, get_user_voices, delete_voice, get_voice_preview
from ..services.clone_service import clone_service
import os
from uuid import uuid4

router = APIRouter(prefix="/api/voices", tags=["Voice Library"])

@router.get("/", response_model=VoiceListResponse)
async def list_voices(
    language: str = None, gender: str = None, engine: str = None, category: str = None,
    is_cloned: bool = None, search: str = None, use_case: str = None, page: int = 1, per_page: int = 50,
    db: Session = Depends(get_db)
):
    skip = (page - 1) * per_page
    filters = {
        "language": language, "gender": gender, "engine": engine, 
        "category": category, "is_cloned": is_cloned, "search": search,
        "use_case": use_case
    }
    voices, total = get_voices(db, filters, skip, per_page)
    return {"voices": voices, "total": total}

@router.get("/cloned", response_model=list[VoiceResponse])
async def list_cloned_voices(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return get_user_voices(db, current_user.id)

@router.get("/clone/status")
async def get_clone_status():
    status = await clone_service.check_availability()
    return status

@router.post("/clone", response_model=VoiceResponse)
async def clone_new_voice(
    name: str = Form(...),
    description: str = Form(""),
    language: str = Form("English"),
    category: str = Form("cloned"),
    consent: bool = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if not consent:
        raise HTTPException(status_code=400, detail="Consent is required for voice cloning.")
    try:
        voice = await clone_service.clone_voice(db, current_user, file, name, description, language, category)
        return voice
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/cloned/{voice_id}")
async def delete_cloned_voice(voice_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    success = await clone_service.delete_clone(db, voice_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Cloned voice not found or not owned by user.")
    return {"message": "Deleted successfully"}

@router.get("/{voice_id}", response_model=VoiceResponse)
async def get_voice(voice_id: int, db: Session = Depends(get_db)):
    voice = get_voice_by_id(db, voice_id)
    if not voice:
        raise HTTPException(status_code=404, detail="Voice not found")
    return voice

@router.get("/{voice_id}/preview")
async def get_preview(voice_id: int, db: Session = Depends(get_db)):
    preview_data = await get_voice_preview(db, voice_id)
    if not preview_data:
        raise HTTPException(status_code=500, detail="Could not generate preview for this voice. Engine may be offline or missing.")
    return preview_data
