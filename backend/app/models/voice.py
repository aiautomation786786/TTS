from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from datetime import datetime, timezone
from ..database import Base

def utcnow():
    return datetime.now(timezone.utc)

class Voice(Base):
    __tablename__ = "voices"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    voice_id = Column(String(200), index=True, nullable=False)
    engine = Column(String(50), default="edge-tts")
    language = Column(String(50), nullable=False)
    locale = Column(String(20), nullable=False)
    gender = Column(String(20), nullable=False)
    style = Column(String(50), nullable=True)
    category = Column(String(50), default="neural")
    quality_label = Column(String(50), default="Premium")
    is_builtin = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    is_cloned = Column(Boolean, default=False)
    preview_url = Column(String(500), nullable=True)
    sample_path = Column(String(500), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    description = Column(Text, nullable=True)
    tags = Column(String(500), nullable=True)
    accent = Column(String(50), nullable=True)
    use_case = Column(String(200), nullable=True) # Legacy
    use_case_tags = Column(String(500), default="[]")
    tone_tags = Column(String(500), default="[]")
    recommended_for = Column(String(500), default="[]")
    preview_status = Column(String(20), default="pending")
    generation_status = Column(String(20), default="pending")
    created_at = Column(DateTime, default=utcnow)
