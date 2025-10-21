# app/models.py
from sqlalchemy import Column, String, Enum, TIMESTAMP, ForeignKey, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship,sessionmaker
from datetime import datetime, timezone, timedelta
from enum import Enum as PyEnum
import random
import string
from sqlalchemy.dialects.postgresql import UUID
import uuid

Base = declarative_base()

class UserStatus(PyEnum):
    banned = "banned"
    new = "new"
    believable = "believable"
    AD = "AD"


class User(Base):
    __tablename__ = 'users'
    
    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nickname = Column(String(12))
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    status = Column(Enum(UserStatus), default=UserStatus.new, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, server_default="CURRENT_TIMESTAMP")
    updated_at = Column(TIMESTAMP, nullable=False, server_default="CURRENT_TIMESTAMP", onupdate="CURRENT_TIMESTAMP")