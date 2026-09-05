"""
Database Async Engine and Session Management
Supports both PostgreSQL (asyncpg) and SQLite (aiosqlite) with automated table initialization.
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from backend.app.core.config import settings


class Base(DeclarativeBase):
    pass


# SQLite-specific connect args if using SQLite
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    connect_args=connect_args,
    future=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for injecting async DB sessions into FastAPI routes."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Create all tables on application startup."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
