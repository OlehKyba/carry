from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.engine.row import Row
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert

from carry.db import users
from carry.core.entities import User


class UserRepositoryError(Exception):
    pass


class NegativeBonusesError(UserRepositoryError):
    pass


class UserRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    @staticmethod
    def _map_user(row: Row | None) -> User | None:
        return (
            User(
                id=row[0],
                chat_id=row[1],
                first_name=row[2],
                last_name=row[3],
                username=row[4],
                bonuses=row[5],
            )
            if row
            else None
        )

    async def upsert_user(self, user: User) -> None:
        set_values = {
            "chat_id": user.chat_id,
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

    async def fetch_user_by_username(self, username: str) -> User | None:
        query = select(
            users.c.id,
            users.c.chat_id,
            users.c.first_name,
            users.c.last_name,
            users.c.username,
            users.c.bonuses,
        ).where(users.c.username == username)
        result = await self.db_session.execute(query)
        return self._map_user(result.one_or_none())

    async def fetch_user_by_id(self, user_id: int) -> User:
        query = select(
            users.c.id,
            users.c.chat_id,
            users.c.first_name,
            users.c.last_name,
            users.c.username,
            users.c.bonuses,
        ).where(users.c.id == user_id)
        result = await self.db_session.execute(query)
        return self._map_user(result.one())

    async def increase_user_balance(self, user_id: int, bonuses: int) -> User:
        query = (
            update(users)
            .where(users.c.id == user_id)
            .values(bonuses=users.c.bonuses + bonuses)
            .returning(
                users.c.id,
                users.c.chat_id,
                users.c.first_name,
                users.c.last_name,
                users.c.username,
                users.c.bonuses,
            )
        )
        result = await self.db_session.execute(query)
        return self._map_user(result.one_or_none())

    async def decrease_user_balance(self, user_id: int, bonuses: int) -> User:
        query = (
            update(users)
            .where(users.c.id == user_id)
            .values(bonuses=users.c.bonuses - bonuses)
            .returning(
                users.c.id,
                users.c.chat_id,
                users.c.first_name,
                users.c.last_name,
                users.c.username,
                users.c.bonuses,
            )
        )

        try:
            result = await self.db_session.execute(query)
        except IntegrityError:
            raise NegativeBonusesError

        return self._map_user(result.one_or_none())
