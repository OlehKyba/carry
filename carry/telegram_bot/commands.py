from typing import TYPE_CHECKING, Final

from telegram import KeyboardButton, ReplyKeyboardMarkup, Update
from telegram.ext import CommandHandler, ContextTypes

from carry.core.templates import render_template

if TYPE_CHECKING:
    from telegram.ext import BaseHandler


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        render_template('telegram/help.jinja2')
    )


async def help_(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        render_template('telegram/help.jinja2')
    )


async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [
            KeyboardButton("Option 1"),
            KeyboardButton("Option 2"),
        ],
        [KeyboardButton("Option 3")],
    ]

    reply_markup = ReplyKeyboardMarkup(keyboard)

    await update.message.reply_text("Please choose:", reply_markup=reply_markup)


COMMAND_HANDLERS: Final[list['BaseHandler']] = [
    CommandHandler('start', start),
    CommandHandler('help', help_),
]
