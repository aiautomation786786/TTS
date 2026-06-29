from sqlalchemy.orm import Session
from ..models.user import User
from ..core.security import verify_password, hash_password

def authenticate_user(db: Session, identifier: str, password: str) -> User | None:
    user = db.query(User).filter((User.username == identifier) | (User.email == identifier)).first()
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user

def create_user(db: Session, username: str, email: str, password: str, role: str = "user") -> User:
    hashed_password = hash_password(password)
    db_user = User(
        username=username,
        email=email,
        password_hash=hashed_password,
        role=role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_username(db: Session, username: str) -> User | None:
    return db.query(User).filter(User.username == username).first()

def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()
