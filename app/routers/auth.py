from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from jwt import InvalidTokenError
JWTError = InvalidTokenError
from app.core.config import settings
from app.core.database import get_db
from app.core.security import decode_token
from app.schemas.auth import LoginRequest, RefreshRequest, RefreshResponse, TokenResponse
from app.schemas.user import UserCreate, UserResponse
from app.services import auth_service

router = APIRouter(tags=["Authentication"])


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED, summary="Register a user")
def signup(data: UserCreate, db: Session = Depends(get_db)):
    try:
        return auth_service.register(db, data.name, str(data.email), data.password)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.post("/login", response_model=TokenResponse, summary="Authenticate a user")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = auth_service.authenticate(db, data.email, data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    access_token, refresh_token = auth_service.tokens_for_user(user)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token, expires_in=settings.access_token_expire_minutes * 60)


@router.post("/refresh", response_model=RefreshResponse, summary="Create a new access token")
def refresh(data: RefreshRequest, db: Session = Depends(get_db)):
    try:
        access_token = auth_service.refresh_access_token(db, data.refresh_token)
    except (JWTError, ValueError, TypeError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token") from None
    return RefreshResponse(access_token=access_token, expires_in=settings.access_token_expire_minutes * 60)
