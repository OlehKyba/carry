from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert

from carry.db import users
from carry.core.entities import User


class UserRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def upsert_user(self, user: User) -> None:
        set_values = {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "username": user.username,
        }
        query = (
            insert(users)
            .values(
                id=user.id,
                **set_values,
            )
            .on_conflict_do_update(
                "users_pkey",
                set_=set_values,
            )
        )
        await self.db_session.execute(query)

    async def fetch_balance(self, user_id: int) -> int:
        query = select(users.c.bonuses).where(users.c.id == user_id)
        result = await self.db_session.execute(query)
        return result.scalar_one()

    async def fetch_user_by_username(self, username: str) -> User:
        query = select(users).where(users.c.username == username)
        result = await self.db_session.execute(query)
        return
