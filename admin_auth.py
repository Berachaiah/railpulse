import os
import time
from fastapi import Request, HTTPException, status, Depends
from jose import jwt, JWTError
from passlib.hash import bcrypt
from sqlalchemy.orm import Session
from database import get_db
from models import User

ADMIN_SESSION_COOKIE = "admin_session"
ADMIN_JWT_SECRET = os.environ["ADMIN_JWT_SECRET"]
ADMIN_JWT_ALG = "HS256"
ADMIN_SESSION_TTL = 60 * 60 * 8

def verify_admin_credentials(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email, User.is_admin == True).first()
    if not user or not user.admin_password_hash:
        return None
    if not bcrypt.verify(password, user.admin_password_hash):
        return None
    return user

def create_admin_session_token(user: User) -> str:
    payload = {"sub": str(user.id), "exp": int(time.time()) + ADMIN_SESSION_TTL}
    return jwt.encode(payload, ADMIN_JWT_SECRET, algorithm=ADMIN_JWT_ALG)

def get_current_admin(request: Request, db: Session = Depends(get_db)) -> User:
    token = request.cookies.get(ADMIN_SESSION_COOKIE)
    if not token:
        raise HTTPException(status_code=status.HTTP_303_SEE_OTHER, headers={"Location": "/admin/login"})
    try:
        payload = jwt.decode(token, ADMIN_JWT_SECRET, algorithms=[ADMIN_JWT_ALG])
    except JWTError:
        raise HTTPException(status_code=status.HTTP_303_SEE_OTHER, headers={"Location": "/admin/login"})

    user = db.query(User).filter(User.id == payload["sub"], User.is_admin == True).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_303_SEE_OTHER, headers={"Location": "/admin/login"})
    return user
