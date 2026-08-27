import json
import os
import secrets
from datetime import datetime, timedelta, timezone

import firebase_admin
import jwt
from fastapi import Request
from firebase_admin import credentials
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from models import User

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)

if not firebase_admin._apps:
    _firebase_cred = credentials.Certificate(
        json.loads(os.environ["FIREBASE_SERVICE_ACCOUNT_JSON"])
    )
    firebase_admin.initialize_app(_firebase_cred)

SESSION_COOKIE_NAME = "railpulse_session"
SESSION_MAX_AGE = int(timedelta(days=30).total_seconds())
JWT_SECRET = os.environ["SESSION_SECRET_KEY"]
JWT_ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)


def create_session_token(user_id) -> str:
    payload = {
        "sub": str(user_id),
        "exp": datetime.now(timezone.utc) + timedelta(seconds=SESSION_MAX_AGE),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def get_current_user(request: Request, db: Session):
    token = request.cookies.get(SESSION_COOKIE_NAME)

    if not token:
        return None

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.PyJWTError:
        return None

    user_id = payload.get("sub")

    if not user_id:
        return None

    return db.query(User).filter(User.id == user_id).first()
