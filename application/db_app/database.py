from typing import AsyncGenerator

from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from application.db_app.settings import settings

SQLALCHEMY_DATABASE_URL = f'postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}:5432/{settings.POSTGRES_DB}'
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True, poolclass=NullPool)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, class_=AsyncSession, bind=engine)


async def connect_db() -> AsyncGenerator:
    async with SessionLocal() as session:
        yield session
