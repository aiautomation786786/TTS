from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..core.dependencies import get_db, get_current_user
from ..schemas.preset import PresetCreate, PresetUpdate, PresetResponse
from ..models.preset import VoicePreset
from ..models.user import User

router = APIRouter(prefix="/api/presets", tags=["Presets"])

@router.post("/", response_model=PresetResponse)
async def create_preset(preset: PresetCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if preset.is_default:
        db.query(VoicePreset).filter(VoicePreset.user_id == current_user.id).update({"is_default": False})
        
    db_preset = VoicePreset(
        user_id=current_user.id,
        **preset.model_dump()
    )
    db.add(db_preset)
    db.commit()
    db.refresh(db_preset)
    return db_preset

@router.get("/", response_model=List[PresetResponse])
async def get_presets(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(VoicePreset).filter(VoicePreset.user_id == current_user.id).order_by(VoicePreset.created_at.desc()).all()

@router.put("/{preset_id}", response_model=PresetResponse)
async def update_preset(preset_id: int, update_data: PresetUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    preset = db.query(VoicePreset).filter(VoicePreset.id == preset_id, VoicePreset.user_id == current_user.id).first()
    if not preset:
        raise HTTPException(status_code=404, detail="Preset not found")
        
    if update_data.is_default:
        db.query(VoicePreset).filter(VoicePreset.user_id == current_user.id).update({"is_default": False})
        
    for key, value in update_data.model_dump(exclude_unset=True).items():
        setattr(preset, key, value)
        
    db.commit()
    db.refresh(preset)
    return preset

@router.delete("/{preset_id}")
async def delete_preset(preset_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    preset = db.query(VoicePreset).filter(VoicePreset.id == preset_id, VoicePreset.user_id == current_user.id).first()
    if not preset:
        raise HTTPException(status_code=404, detail="Preset not found")
    
    db.delete(preset)
    db.commit()
    return {"message": "Preset deleted"}
