# app/models.py
from sqlalchemy import Column, String, Enum, TIMESTAMP, ForeignKey, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship,sessionmaker
from datetime import datetime, timezone, timedelta
from enum import Enum as PyEnum
import random
import string
import uuid

Base = declarative_base()

class UserStatus(PyEnum):
    banned = "banned"
    new = "new"
    believable = "believable"
    AD = "AD"

def generate_uuid():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

class User(Base):
    __tablename__ = 'users'
    
    user_id = Column(String(8), primary_key=True, default=generate_uuid)
    nickname = Column(String(12))
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    status = Column(Enum(UserStatus), default=UserStatus.new, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default="CURRENT_TIMESTAMP")
    updated_at = Column(TIMESTAMP, nullable=False, server_default="CURRENT_TIMESTAMP", onupdate="CURRENT_TIMESTAMP")