import logging

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from carry.config import settings

logging.basicConfig(level=logging.INFO)


async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Hello {update.effective_user.first_name}')


app = ApplicationBuilder().token(settings.telegram.token).build()

app.add_handler(CommandHandler('hello', hello))

app.run_polling()
