from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from .config import settings

engine = create_async_engine(
    url=settings.resolved_database_url,
    pool_pre_ping=True,
    echo=False,
)

async_session_factory = async_sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession]:
    async with async_session_factory() as session:
        yield session


DbConn = Annotated[AsyncSession, Depends(get_db)]
