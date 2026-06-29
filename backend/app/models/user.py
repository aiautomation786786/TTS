from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float
from datetime import datetime, timezone
from ..database import Base

def utcnow():
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="user")
    is_active = Column(Boolean, default=True)
    avatar_url = Column(String(500), nullable=True)
    char_quota = Column(Integer, default=50000)
    chars_used = Column(Integer, default=0)
    generation_count = Column(Integer, default=0)
    clone_count = Column(Integer, default=0)
    preferred_voice_id = Column(String(200), nullable=True)
    preferred_language = Column(String(20), default="en-US")
    preferred_speed = Column(Float, default=1.0)
    preferred_pitch = Column(String(20), default="+0Hz")
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)
