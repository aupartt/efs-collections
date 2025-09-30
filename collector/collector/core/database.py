import asyncio
import contextlib

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from collector.core.settings import settings

db_samaphore = asyncio.Semaphore(20)
engine = None
AsyncSessionLocal = None


@contextlib.asynccontextmanager
async def get_db():
    """Dependency to get database session"""
    global engine, AsyncSessionLocal

    if engine is None:
        engine = create_async_engine(settings.POSTGRES_URL, pool_size=10, max_overflow=20)
    if AsyncSessionLocal is None:
        AsyncSessionLocal = async_sessionmaker(bind=engine, autocommit=False, autoflush=False)

    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
