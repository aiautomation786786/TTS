from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float
from datetime import datetime, timezone
from ..database import Base

def utcnow():
    return datetime.now(timezone.utc)

class Generation(Base):
    __tablename__ = "generations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    text = Column(Text, nullable=False)
    voice_id = Column(Integer, ForeignKey("voices.id"), nullable=True)
    voice_name = Column(String(100))
    voice_engine = Column(String(50))
    audio_path = Column(String(500))
    audio_duration = Column(Float, nullable=True)
    char_count = Column(Integer)
    speed = Column(Float, default=1.0)
    pitch = Column(String(20), default="+0Hz")
    file_size = Column(Integer, nullable=True)
    file_format = Column(String(10), default="mp3")
    status = Column(String(20), default="completed")
    mode = Column(String(20), default="short_form")
    total_chunks = Column(Integer, default=1)
    completed_chunks = Column(Integer, default=0)
    progress = Column(Float, default=100.0)
    error_message = Column(Text, nullable=True)
    failed_chunk_index = Column(Integer, nullable=True)
    failed_chunk_text_preview = Column(Text, nullable=True)
    failed_engine_error = Column(Text, nullable=True)
    generation_time_seconds = Column(Float, nullable=True)
    project_id = Column(Integer, nullable=True)
    batch_id = Column(Integer, ForeignKey("batch_jobs.id"), nullable=True)
    is_favorite = Column(Integer, default=0) # using integer for boolean in SQLite
    created_at = Column(DateTime, default=utcnow)

class SystemSettings(Base):
    __tablename__ = "system_settings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(100), unique=True, index=True, nullable=False)
    value = Column(Text)
    category = Column(String(50), default="general")
    description = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)
