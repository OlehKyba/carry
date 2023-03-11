import logging

from carry.telegram_bot.factories import create_bot

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
bot = create_bot()
bot.run_polling()
