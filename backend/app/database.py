"""
Async SQLAlchemy database engine and session management.
Uses asyncpg driver for non-blocking database operations.
"""

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from app.config import get_settings

settings = get_settings()

# Create async engine with connection pooling
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.APP_ENV == "development",  # SQL logging in dev mode
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Verify connections before use
)

# Session factory
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncSession:
    """
    Dependency injection for database sessions.
    Usage in FastAPI routes:
        @router.get("/")
        async def endpoint(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
