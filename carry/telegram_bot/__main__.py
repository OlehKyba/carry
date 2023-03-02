import logging

from carry.telegram_bot.factories import create_bot

logging.basicConfig(level=logging.INFO)
bot = create_bot()
bot.run_polling()
