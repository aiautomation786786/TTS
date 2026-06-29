from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from datetime import datetime, timezone
from ..database import Base

def utcnow():
    return datetime.now(timezone.utc)

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True) # null for global/admin
    title = Column(String(255), nullable=False)
    message = Column(String(500), nullable=True)
    type = Column(String(50), default="info") # info, success, warning, error
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=utcnow)
