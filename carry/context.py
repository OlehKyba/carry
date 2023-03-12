from typing import TYPE_CHECKING, TypeVar, Callable, Awaitable, ParamSpec
from functools import wraps
from contextlib import AsyncExitStack
from contextvars import ContextVar

from carry.db.core import db_session_ctx
from carry.core.repositories import UserRepository

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

P = ParamSpec("P")
RT = TypeVar("RT")


class Context:
    ctx_db: ContextVar["AsyncSession"] = ContextVar("db_session")

    @property
    def db_session(self) -> "AsyncSession":
        return self.ctx_db.get()

    @property
    def user_repository(self) -> UserRepository:
        return UserRepository(self.db_session)

    def with_request_context(
        self,
        func: Callable[P, Awaitable[RT]],
    ) -> Callable[P, Awaitable[RT]]:
        @wraps(func)
        async def decorator(
            *args: P.args, **kwargs: P.kwargs
        ) -> Awaitable[RT]:
            async with AsyncExitStack() as exit_stack:
                await exit_stack.enter_async_context(db_session_ctx(self))
                result = await func(*args, **kwargs)
                return result

        return decorator


ctx = Context()
