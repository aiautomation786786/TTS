from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class BatchItemCreate(BaseModel):
    text: str
    voice_id: Optional[str] = None
    speed: Optional[float] = 1.0
    pitch: Optional[str] = "+0Hz"

class BatchCreate(BaseModel):
    title: str
    items: List[BatchItemCreate]

class BatchItemResponse(BaseModel):
    id: int
    batch_id: int
    text: str
    voice_id: Optional[str] = None
    speed: float
    pitch: str
    status: str
    generation_id: Optional[int] = None
    error_message: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class BatchJobResponse(BaseModel):
    id: int
    user_id: int
    title: str
    total_items: int
    completed_items: int
    failed_items: int
    status: str
    created_at: datetime
    updated_at: datetime
    items: Optional[List[BatchItemResponse]] = None

    class Config:
        from_attributes = True
