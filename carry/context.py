from typing import TYPE_CHECKING
from contextvars import ContextVar

from carry.core.repositories import UserRepository

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class Context:
    ctx_db: ContextVar['AsyncSession'] = ContextVar('db_session')

    @property
    def db_session(self) -> 'AsyncSession':
        return self.ctx_db.get()

    @property
    def user_repository(self) -> UserRepository:
        return UserRepository(self.db_session)


ctx = Context()
