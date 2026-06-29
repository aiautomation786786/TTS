from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from ..core.dependencies import get_db, get_current_user
from ..core.security import create_access_token
from ..schemas.auth import RegisterRequest, TokenResponse
from ..schemas.user import UserResponse
from ..services.auth_service import authenticate_user, create_user, get_user_by_username, get_user_by_email

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/register", response_model=TokenResponse)
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    if get_user_by_username(db, request.username):
        raise HTTPException(status_code=400, detail="Username already registered")
    if get_user_by_email(db, request.email):
        raise HTTPException(status_code=400, detail="Email already registered")
        
    user = create_user(db, request.username, request.email, request.password)
    access_token = create_access_token(data={"user_id": user.id})
    return {"access_token": access_token, "token_type": "bearer", "user": user}

@router.post("/login", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username/email or password")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Account disabled")
        
    access_token = create_access_token(data={"user_id": user.id})
    return {"access_token": access_token, "token_type": "bearer", "user": user}

@router.get("/me", response_model=UserResponse)
async def get_me(current_user = Depends(get_current_user)):
    return current_user
