from typing import TYPE_CHECKING, AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy.orm import registry, sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm.decl_api import DeclarativeMeta

from carry.config import settings

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncConnection

    from carry.context import Context

mapper_registry = registry()
metadata = mapper_registry.metadata
engine = create_async_engine(
    settings.db.uri,
    pool_pre_ping=True,
)
session_factory = sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


class Base(metaclass=DeclarativeMeta):
    __abstract__ = True

    registry = mapper_registry
    metadata = metadata

    __init__ = mapper_registry.constructor


async def create_connection() -> "AsyncConnection":
    conn = await engine.connect()
    return conn


@asynccontextmanager
async def db_session_ctx(ctx: "Context") -> AsyncIterator[AsyncSession]:
    async with session_factory() as session:
        token = ctx.ctx_db.set(session)
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            ctx.ctx_db.reset(token)
