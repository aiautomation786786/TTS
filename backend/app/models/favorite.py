from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime, timezone
from ..database import Base

def utcnow():
    return datetime.now(timezone.utc)

class FavoriteVoice(Base):
    __tablename__ = "favorite_voices"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    voice_id = Column(String(200), nullable=False) # database voice id
    created_at = Column(DateTime, default=utcnow)
