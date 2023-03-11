from typing import TYPE_CHECKING

from telegram.ext import ApplicationBuilder

from carry.config import settings
from carry.telegram_bot.commands import COMMAND_HANDLERS

if TYPE_CHECKING:
    from telegram.ext import Application


def create_bot() -> "Application":
    bot = ApplicationBuilder().token(settings.telegram.token).build()
    bot.add_handlers(COMMAND_HANDLERS)
    return bot
