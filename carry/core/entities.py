from dataclasses import dataclass

from telegram import User as TelegramUser


@dataclass(frozen=True)
class User:
    id: int
    first_name: str
    last_name: str | None
    username: str | None
    bonuses: int

    @classmethod
    def from_telegram(cls, tg_user: TelegramUser, bonuses: int = 0) -> "User":
        return cls(
            id=tg_user.id,
            first_name=tg_user.first_name,
            last_name=tg_user.last_name,
            username=tg_user.username,
            bonuses=bonuses,
        )

    @property
    def full_name(self) -> str:
        return (
            self.first_name
            if not self.last_name
            else f"{self.first_name} {self.last_name}"
        )
