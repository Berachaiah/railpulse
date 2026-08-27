import os
import secrets
from datetime import timedelta

import firebase_admin
from fastapi import Request
from firebase_admin import credentials
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from models import User

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)

_firebase_cred = credentials.Certificate(os.environ["FIREBASE_SERVICE_ACCOUNT_PATH"])
firebase_admin.initialize_app(_firebase_cred)

SESSION_COOKIE_NAME = "railpulse_session"
SESSION_MAX_AGE = int(timedelta(days=30).total_seconds())

# Dev-only in-memory session store.
# Replace with Redis or a database-backed session store in production.
_sessions: dict[str, str] = {}


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)


def create_session_token(user_id) -> str:
    token = secrets.token_urlsafe(32)
    _sessions[token] = str(user_id)
    return token


def get_current_user(request: Request, db: Session):
    token = request.cookies.get(SESSION_COOKIE_NAME)

    if not token:
        return None

    user_id = _sessions.get(token)

    if not user_id:
        return None

    return db.query(User).filter(User.id == user_id).first()
