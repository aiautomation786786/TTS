from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class PresetCreate(BaseModel):
    name: str
    voice_id: str
    speed: Optional[float] = 1.0
    pitch: Optional[str] = "+0Hz"
    volume: Optional[str] = "default"
    language: Optional[str] = None
    content_type: Optional[str] = None
    is_default: Optional[bool] = False

class PresetUpdate(BaseModel):
    name: Optional[str] = None
    voice_id: Optional[str] = None
    speed: Optional[float] = None
    pitch: Optional[str] = None
    volume: Optional[str] = None
    language: Optional[str] = None
    content_type: Optional[str] = None
    is_default: Optional[bool] = None

class PresetResponse(BaseModel):
    id: int
    user_id: int
    name: str
    voice_id: str
    speed: float
    pitch: str
    volume: str
    language: Optional[str] = None
    content_type: Optional[str] = None
    is_default: bool
    created_at: datetime

    class Config:
        from_attributes = True
