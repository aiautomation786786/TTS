from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..core.dependencies import get_db, get_current_user
from ..schemas.user import UserResponse, UserUpdateRequest, PasswordChangeRequest
from ..services.user_service import update_user_profile, change_password, get_user_stats

router = APIRouter(prefix="/api/users", tags=["Users"])

@router.get("/profile", response_model=UserResponse)
async def get_profile(current_user = Depends(get_current_user)):
    return current_user

@router.put("/profile", response_model=UserResponse)
async def update_profile(request: UserUpdateRequest, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return update_user_profile(db, current_user.id, request.model_dump(exclude_unset=True))

@router.put("/password")
async def update_password(request: PasswordChangeRequest, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    success = change_password(db, current_user.id, request.current_password, request.new_password)
    if not success:
        raise HTTPException(status_code=400, detail="Incorrect current password")
    return {"message": "Password updated successfully"}

@router.get("/stats")
async def get_stats(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return get_user_stats(db, current_user.id)
