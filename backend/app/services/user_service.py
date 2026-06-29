from sqlalchemy.orm import Session
from ..models.user import User

from sqlalchemy import func
from ..models.generation import Generation

def get_user_stats(db: Session, user_id: int) -> dict:
    user = db.query(User).filter(User.id == user_id).first()
    
    # Aggregations
    total_duration = db.query(func.sum(Generation.audio_duration)).filter(Generation.user_id == user_id).first()[0] or 0.0
    short_form_count = db.query(Generation).filter(Generation.user_id == user_id, Generation.mode == "short_form").count()
    long_form_count = db.query(Generation).filter(Generation.user_id == user_id, Generation.mode == "long_form").count()
    
    # Most used voice
    most_used = db.query(
        Generation.voice_name, func.count(Generation.id)
    ).filter(Generation.user_id == user_id).group_by(Generation.voice_name).order_by(func.count(Generation.id).desc()).first()
    
    most_used_voice = most_used[0] if most_used else "None"
    
    return {
        "chars_used": user.chars_used,
        "char_quota": user.char_quota,
        "generation_count": user.generation_count,
        "clone_count": user.clone_count,
        "quota_percent": min((user.chars_used / user.char_quota) * 100, 100) if user.char_quota > 0 else 0,
        "total_duration": total_duration,
        "short_form_count": short_form_count,
        "long_form_count": long_form_count,
        "most_used_voice": most_used_voice
    }

def update_user_profile(db: Session, user_id: int, data: dict) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    for key, value in data.items():
        if value is not None:
            setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user

def change_password(db: Session, user_id: int, current_pw: str, new_pw: str) -> bool:
    from ..core.security import verify_password, hash_password
    user = db.query(User).filter(User.id == user_id).first()
    if not verify_password(current_pw, user.password_hash):
        return False
    user.password_hash = hash_password(new_pw)
    db.commit()
    return True

def get_all_users(db: Session, skip: int, limit: int, search: str = None):
    query = db.query(User)
    if search:
        query = query.filter(User.username.contains(search) | User.email.contains(search))
    total = query.count()
    users = query.offset(skip).limit(limit).all()
    return users, total

def toggle_user_active(db: Session, user_id: int) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    user.is_active = not user.is_active
    db.commit()
    db.refresh(user)
    return user

def update_user_quota(db: Session, user_id: int, new_quota: int) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    user.char_quota = new_quota
    db.commit()
    db.refresh(user)
    return user

def reset_user_usage(db: Session, user_id: int) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.chars_used = 0
        db.commit()
        db.refresh(user)
    return user

def change_user_role(db: Session, user_id: int, new_role: str) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.role = new_role
        db.commit()
        db.refresh(user)
    return user

def delete_user(db: Session, user_id: int) -> bool:
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        db.delete(user)
        db.commit()
        return True
    return False
