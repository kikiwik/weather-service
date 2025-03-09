# app/dao/databases.py
from sqlalchemy.ext.asyncio import create_async_engine,AsyncSession
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator

DATABASE_URL = "mysql+asyncmy://root:Fkiwi191954@localhost/weatherweb"#配置文件
'''def get_db():
    db = Session(bind=engine)
    try:
        yield db
    finally:
        db.close()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)'''

async_engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    pool_size=20,
    max_overflow=10,
    pool_recycle=3600
)

AsyncSessionLocal=sessionmaker(
    expire_on_commit=False,
    class_=AsyncSession,
    bind=async_engine
)

async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session