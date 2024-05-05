from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from src.core.secrets import DB_URL

async_engine = create_async_engine(DB_URL, echo=False)

AsyncLocalSession = sessionmaker(
    async_engine,
    expire_on_commit=False,
    class_=AsyncSession
)


@asynccontextmanager
async def get_async_session():
    session = AsyncLocalSession()
    try:
        yield session
    except Exception as e:
        print(e)
        await session.rollback()
    finally:
        await session.close()
