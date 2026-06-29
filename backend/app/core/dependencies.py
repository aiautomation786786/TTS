from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..models.user import User
from .security import decode_access_token, verify_password
from fastapi import Header
from ..config import get_settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(db: Session = Depends(get_db)) -> User:
    # Bypass auth and return the global system user (id=1)
    user = db.query(User).filter(User.id == 1).first()
    if not user:
        # Create global user if it doesn't exist
        user = User(
            id=1,
            email="global@voxforge.local",
            username="SystemUser",
            hashed_password="bypass",
            role="admin",
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user

def require_admin(current_user: User = Depends(get_current_user)) -> User:
    # All users are admin in the open system
    return current_user

def require_admin_gate(current_user: User = Depends(require_admin)) -> User:
    # Bypass admin gate entirely
    return current_user
