from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    is_active: bool
    avatar_url: Optional[str] = None
    char_quota: int
    chars_used: int
    generation_count: int
    clone_count: int
    preferred_voice_id: Optional[str] = None
    preferred_language: str
    preferred_speed: float
    preferred_pitch: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserUpdateRequest(BaseModel):
    email: Optional[EmailStr] = None
    avatar_url: Optional[str] = None
    preferred_voice_id: Optional[str] = None
    preferred_language: Optional[str] = None
    preferred_speed: Optional[float] = None
    preferred_pitch: Optional[str] = None

class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str

class UserListResponse(BaseModel):
    users: List[UserResponse]
    total: int
