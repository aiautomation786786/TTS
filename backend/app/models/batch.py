from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float
from datetime import datetime, timezone
from ..database import Base

def utcnow():
    return datetime.now(timezone.utc)

class BatchJob(Base):
    __tablename__ = "batch_jobs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    total_items = Column(Integer, default=0)
    completed_items = Column(Integer, default=0)
    failed_items = Column(Integer, default=0)
    status = Column(String(20), default="processing") # processing, completed, failed
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

class BatchItem(Base):
    __tablename__ = "batch_items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    batch_id = Column(Integer, ForeignKey("batch_jobs.id"), nullable=False)
    text = Column(Text, nullable=False)
    voice_id = Column(String(200), nullable=True)
    speed = Column(Float, default=1.0)
    pitch = Column(String(20), default="+0Hz")
    status = Column(String(20), default="pending") # pending, processing, completed, failed
    generation_id = Column(Integer, ForeignKey("generations.id"), nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utcnow)
