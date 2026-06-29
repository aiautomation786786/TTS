from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..core.dependencies import get_db, get_current_user
from ..schemas.notification import NotificationResponse
from ..models.notification import Notification
from ..models.user import User

router = APIRouter(prefix="/api/notifications", tags=["Notifications"])

@router.get("/", response_model=List[NotificationResponse])
async def get_notifications(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Get user notifications and global notifications
    return db.query(Notification).filter(
        (Notification.user_id == current_user.id) | (Notification.user_id == None)
    ).order_by(Notification.created_at.desc()).limit(50).all()

@router.put("/{notification_id}/read")
async def mark_as_read(notification_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    notification = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
        
    if notification.user_id and notification.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    notification.is_read = True
    db.commit()
    return {"message": "Marked as read"}

@router.put("/read-all")
async def mark_all_as_read(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db.query(Notification).filter(Notification.user_id == current_user.id, Notification.is_read == False).update({"is_read": True})
    db.commit()
    return {"message": "All marked as read"}
