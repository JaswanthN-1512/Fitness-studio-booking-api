import logging
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.security import create_access_token, create_refresh_token, hash_password, verify_password, decode_token
from app.core.config import settings
from app.models import User

logger = logging.getLogger(__name__)


def register(db: Session, name: str, email: str, password: str) -> User:
    normalized_email = email.strip().lower()
    existing = db.scalar(select(User).where(User.email == normalized_email))
    if existing:
        raise ValueError("Email is already registered")
    user = User(name=name.strip(), email=normalized_email, password_hash=hash_password(password))
    db.add(user)
    db.commit()
    db.refresh(user)
    logger.info("User registered successfully: user_id=%s", user.id)
    return user


def authenticate(db: Session, email: str, password: str) -> User | None:
    user = db.scalar(select(User).where(User.email == email.strip().lower()))
    if not user or not verify_password(password, user.password_hash):
        logger.warning("Login failed for email=%s", email.strip().lower())
        return None
    logger.info("User logged in successfully: user_id=%s", user.id)
    return user


def tokens_for_user(user: User) -> tuple[str, str]:
    return create_access_token(user.id), create_refresh_token(user.id)


def refresh_access_token(db: Session, refresh_token: str) -> str:
    payload = decode_token(refresh_token)
    if payload.get("type") != "refresh":
        raise ValueError("Invalid token type")
    subject = payload.get("sub")
    if not subject:
        raise ValueError("Invalid refresh token")
    user = db.get(User, int(subject))
    if not user:
        raise ValueError("User not found")
    return create_access_token(user.id)
