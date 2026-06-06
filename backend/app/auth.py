import hashlib
import hmac
import os

from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from .database import get_db
from .models.user import User


SECRET_KEY = os.getenv("APP_SECRET_KEY", "dev-secret-change-me")


def hash_password(password: str):
    return hashlib.sha256(f"{SECRET_KEY}:{password}".encode("utf-8")).hexdigest()


def verify_password(password: str, password_hash: str):
    return hmac.compare_digest(hash_password(password), password_hash)


def make_token(user: User):
    signature = hashlib.sha256(
        f"{SECRET_KEY}:{user.username}:{user.password_hash}".encode("utf-8")
    ).hexdigest()
    return f"{user.id}:{user.username}:{signature}"


def get_current_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Login required")

    token = authorization.removeprefix("Bearer ").strip()
    parts = token.split(":", 2)
    if len(parts) != 3:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id, username, signature = parts
    user = db.get(User, int(user_id)) if user_id.isdigit() else None
    if user is None or user.username != username:
        raise HTTPException(status_code=401, detail="Invalid token")

    expected = make_token(user).split(":", 2)[2]
    if not hmac.compare_digest(signature, expected):
        raise HTTPException(status_code=401, detail="Invalid token")

    return user
