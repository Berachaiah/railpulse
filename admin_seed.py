import os
from passlib.hash import bcrypt
from sqlalchemy.orm import Session
from models import User

def ensure_admin_seed(db: Session) -> None:
    email = os.environ.get("ADMIN_EMAIL")
    password = os.environ.get("ADMIN_PASSWORD")
    if not email or not password:
        return

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        user = User(email=email, is_admin=True)
        db.add(user)

    user.is_admin = True

    needs_hash_update = (
        not user.admin_password_hash
        or not bcrypt.verify(password, user.admin_password_hash)
    )
    if needs_hash_update:
        user.admin_password_hash = bcrypt.hash(password)

    db.commit()
