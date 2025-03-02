# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,Session
from contextlib import asynccontextmanager

DATABASE_URL = "mysql://root:Fkiwi191954@localhost/weatherweb"
def get_db():
    db = Session(bind=engine)
    try:
        yield db
    finally:
        db.close()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)