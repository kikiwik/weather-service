# app/crud.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import asyncio
import bcrypt
from datetime import datetime, timezone, timedelta
import uuid
from .models import User
from .schemas import UserCreate

async def get_user_by_email(db: AsyncSession, email: str):
    stmt = select(User).filter(User.email == email)
    result = await db.execute(stmt)
    return result.scalars().first()

async def create_user(db: AsyncSession, user: UserCreate):
    hashed_password = await asyncio.to_thread(bcrypt.hashpw, user.password.encode('utf-8'), bcrypt.gensalt())
    db_user = User(
        email=user.email,
        nickname=user.nickname,
        password=hashed_password.decode('utf-8'),
        user_id=uuid.uuid4()
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user