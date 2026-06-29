from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Boolean
from datetime import datetime, timezone
from ..database import Base

def utcnow():
    return datetime.now(timezone.utc)

class VoicePreset(Base):
    __tablename__ = "voice_presets"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    voice_id = Column(String(200), nullable=False) # database voice id, not display name
    speed = Column(Float, default=1.0)
    pitch = Column(String(20), default="+0Hz")
    volume = Column(String(20), default="default")
    language = Column(String(50), nullable=True)
    content_type = Column(String(100), nullable=True)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, default=utcnow)
