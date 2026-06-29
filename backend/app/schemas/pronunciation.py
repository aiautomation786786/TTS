from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class PronunciationCreate(BaseModel):
    original_text: str
    replacement_text: str
    is_active: Optional[bool] = True

class PronunciationUpdate(BaseModel):
    original_text: Optional[str] = None
    replacement_text: Optional[str] = None
    is_active: Optional[bool] = None

class PronunciationResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    original_text: str
    replacement_text: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
