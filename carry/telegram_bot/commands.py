from typing import TYPE_CHECKING, Final

from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

if TYPE_CHECKING:
    from telegram.ext import BaseHandler


async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Hello {update.effective_user.first_name}')


COMMAND_HANDLERS: Final[list['BaseHandler']] = [
    CommandHandler('hello', hello),
]
