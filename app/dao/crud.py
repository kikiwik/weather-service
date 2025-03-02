# app/crud.py
from sqlalchemy.orm import Session
from models import User
from schmas import UserCreate
import bcrypt
from datetime import datetime, timezone, timedelta
import uuid

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user: UserCreate):
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
    db_user = User(email=user.email,nickname=user.nickname, password=hashed_password.decode('utf-8'),user_id=str(uuid.uuid4())[:8])
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user