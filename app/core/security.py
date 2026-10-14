import base64
import hmac
import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Any
import jwt
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from app.core.config import settings

logger = logging.getLogger(__name__)


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    derived = Scrypt(salt=salt, length=64, n=2**14, r=8, p=1).derive(password.encode("utf-8"))
    return "scrypt$16384$8$1$" + base64.urlsafe_b64encode(salt).decode() + "$" + base64.urlsafe_b64encode(derived).decode()


def verify_password(password: str, encoded: str) -> bool:
    try:
        algorithm, n, r, p, salt_b64, hash_b64 = encoded.split("$", 5)
        if algorithm != "scrypt":
            return False
        salt = base64.urlsafe_b64decode(salt_b64.encode())
        expected = base64.urlsafe_b64decode(hash_b64.encode())
        actual = Scrypt(salt=salt, length=len(expected), n=int(n), r=int(r), p=int(p)).derive(password.encode("utf-8"))
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False


def create_token(subject: int, token_type: str, expires_delta: timedelta) -> str:
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {"sub": str(subject), "type": token_type, "iat": now, "exp": now + expires_delta}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def create_access_token(subject: int) -> str:
    return create_token(subject, "access", timedelta(minutes=settings.access_token_expire_minutes))


def create_refresh_token(subject: int) -> str:
    return create_token(subject, "refresh", timedelta(days=settings.refresh_token_expire_days))


def decode_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
