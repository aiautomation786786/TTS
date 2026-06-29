from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import json

class VoiceResponse(BaseModel):
    id: int
    name: str
    voice_id: str
    engine: str
    language: str
    locale: str
    gender: str
    style: Optional[str] = None
    category: str
    quality_label: str
    is_builtin: bool
    is_active: bool
    is_cloned: bool
    preview_url: Optional[str] = None
    user_id: Optional[int] = None
    description: Optional[str] = None
    tags: Optional[str] = None
    accent: Optional[str] = None
    use_case: Optional[str] = None
    use_case_tags: Optional[str] = "[]"
    tone_tags: Optional[str] = "[]"
    recommended_for: Optional[str] = "[]"
    preview_status: Optional[str] = "pending"
    generation_status: Optional[str] = "pending"
    created_at: datetime

    class Config:
        from_attributes = True

class VoiceListResponse(BaseModel):
    voices: List[VoiceResponse]
    total: int

class CloneVoiceRequest(BaseModel):
    name: str
    description: Optional[str] = None

class VoiceFilterParams(BaseModel):
    language: Optional[str] = None
    gender: Optional[str] = None
    engine: Optional[str] = None
    category: Optional[str] = None
    is_cloned: Optional[bool] = None
    search: Optional[str] = None
