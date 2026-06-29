from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class NotificationResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    title: str
    message: Optional[str] = None
    type: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True
