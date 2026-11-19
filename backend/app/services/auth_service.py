"""Xác thực: hash mật khẩu (pbkdf2 stdlib) + JWT (PyJWT)."""
import base64
import hashlib
import os
from datetime import datetime, timedelta, timezone

import jwt

from ..config import SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100_000)
    return base64.b64encode(salt + dk).decode()


def verify_password(password: str, hashed: str) -> bool:
    try:
        raw = base64.b64decode(hashed.encode())
        salt, dk = raw[:16], raw[16:]
        return hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100_000) == dk
    except Exception:
        return False


def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode({"sub": str(user_id), "exp": expire}, SECRET_KEY, algorithm="HS256")


def decode_token(token: str) -> int:
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    return int(payload["sub"])
