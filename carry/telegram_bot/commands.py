from enum import IntEnum, StrEnum
from typing import TYPE_CHECKING, Final

from telegram import (
    Update,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ContextTypes,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    filters,
)
from telegram.helpers import create_deep_linked_url
from telegram.constants import ParseMode

from carry.config import settings
from carry.context import ctx
from carry.core.bl import is_admin, create_qr_code
from carry.core.entities import User
from carry.core.templates import render_template

if TYPE_CHECKING:
    from telegram.ext import BaseHandler


class UserConversationChoices(IntEnum):
    AFTER_START = 1
    SHOW_BALANCE = 2
    CREATE_QR = 3


class UserConversationText(StrEnum):
    SHOW_BALANCE = "Баланс 💰"
    CREATE_QR = "QR-код 👩‍💻"


class AdminConversationChoices(IntEnum):
    AFTER_START = 1
    ASK_USER_NICKNAME = 2
    SHOW_USERS = 3
    FIND_USER = 4
    SHOW_ALL_USERS = 5
    INCREASE_USER_BALANCE = 6
    DECREASE_USER_BALANCE = 7


class AdminConversationText(StrEnum):
    FIND_USER = "Знайти користувача"
    SHOW_ALL_USERS = "Список користувачів"
    INCREASE_USER_BALANCE = "Додати бонуси ⬆️"
    DECREASE_USER_BALANCE = "Зняти бонуси ⬇️"


USER_KEYBOARD = ReplyKeyboardMarkup(
    [
        [
            KeyboardButton(UserConversationText.SHOW_BALANCE),
            KeyboardButton(UserConversationText.CREATE_QR),
        ],
    ],
    resize_keyboard=True,
)

ADMIN_KEYBOARD = ReplyKeyboardMarkup(
    [
        [
            KeyboardButton(
                AdminConversationText.FIND_USER,
            ),
            KeyboardButton(
                AdminConversationText.SHOW_ALL_USERS,
            ),
        ],
    ],
    resize_keyboard=True,
)

DEEP_LINK_KEYBOARD = ReplyKeyboardMarkup(
    [
        [
            KeyboardButton(
                AdminConversationText.INCREASE_USER_BALANCE,
            ),
            KeyboardButton(
                AdminConversationText.DECREASE_USER_BALANCE,
            ),
        ],
    ],
    resize_keyboard=True,
)

LINKS_KEYBOARD = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(
                'Instagram 📷',
                url=settings.usefull_links.instagram,
            ),
            InlineKeyboardButton(
                'Записатися 💅',
                url=settings.usefull_links.easyweek,
            ),
        ],
    ],
)


@ctx.with_request_context
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = User.from_telegram(update.message.from_user)
    await ctx.user_repository.upsert_user(user)
    keyboard = ADMIN_KEYBOARD if is_admin(user.id) else USER_KEYBOARD
    first_message = await update.message.reply_text(
        render_template("telegram/help.jinja2"),
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML,
    )
    await update.message.reply_text(
        '*Корисні посилання* 🔗',
        reply_markup=LINKS_KEYBOARD,
        parse_mode=ParseMode.MARKDOWN,
        reply_to_message_id=first_message.id,
    )
    return UserConversationChoices.AFTER_START


async def help_(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        render_template("telegram/help.jinja2"),
        reply_markup=LINKS_KEYBOARD,
    )
    return UserConversationChoices.AFTER_START


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Дякую! Гарного дня.", reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


@ctx.with_request_context
async def show_balance(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    balance = await ctx.user_repository.fetch_balance(
        update.message.from_user.id
    )
    await update.message.reply_text(
        f"На вашому балансі *{balance} бонусів* 💵",
        reply_to_message_id=update.message.id,
        parse_mode=ParseMode.MARKDOWN,
    )
    return UserConversationChoices.AFTER_START


async def generate_qr_code(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    url = create_deep_linked_url(
        context.bot.username, payload=str(update.message.from_user.id)
    )
    qr_code = create_qr_code(url)
    await update.message.reply_photo(
        qr_code, caption="Це QR-код, який ви маєте показати @kerry_queen 🤝"
    )


async def ask_user_nickname(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    await update.message.reply_text(
        f"Напишіть нікнейм користувача",
        reply_markup=ReplyKeyboardRemove(),
    )
    return AdminConversationChoices.ASK_USER_NICKNAME


async def find_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = 447647899
    context.user_data["user_id"] = user_id
    await update.message.reply_text(
        f"У користувача Oleh[{user_id}] на рахунку 50 бонусів.",
        reply_markup=DEEP_LINK_KEYBOARD,
    )
    return AdminConversationChoices.FIND_USER


async def deep_link_start(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    user_id = int(context.args[0])
    context.user_data["user_id"] = user_id
    await update.message.reply_text(
        f"У користувача Oleh[{user_id}] на рахунку 50 бонусів.",
        reply_markup=DEEP_LINK_KEYBOARD,
    )
    return AdminConversationChoices.FIND_USER


async def before_increase_user_balance(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    await update.message.reply_text(
        f"Напишіть скільки бонусів ви хочете додати.",
        reply_markup=ReplyKeyboardRemove(),
    )
    return AdminConversationChoices.INCREASE_USER_BALANCE


async def before_decrease_user_balance(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    await update.message.reply_text(
        f"Напишіть скільки бонусів ви хочете забрати.",
        reply_markup=ReplyKeyboardRemove(),
    )
    return AdminConversationChoices.DECREASE_USER_BALANCE


async def increase_user_balance(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    user_id = context.user_data["user_id"]
    await update.message.reply_text(
        f"Додали користувачу Oleh[{user_id}] 15 бонусів.\n"
        f"Поточний рахунок: 65 бонусів.",
        reply_markup=ADMIN_KEYBOARD,
    )
    context.user_data.clear()
    return ConversationHandler.END


async def decrease_user_balance(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    user_id = context.user_data["user_id"]
    await update.message.reply_text(
        f"Забрали у користувача Oleh[{user_id}] 15 бонусів.\n"
        f"Поточний рахунок: 35 бонусів.",
        reply_markup=ADMIN_KEYBOARD,
    )
    context.user_data.clear()
    return ConversationHandler.END


COMMAND_HANDLERS: Final[list["BaseHandler"]] = [
    CommandHandler('help', help_),
    ConversationHandler(
        entry_points=[
            CommandHandler(
                "start",
                deep_link_start,
                filters.User(settings.admin_ids)
                and filters.Regex(r"^/start \d+$"),
            ),
            CommandHandler("start", start),
        ],
        states={
            UserConversationChoices.AFTER_START: [
                MessageHandler(
                    filters.Text([UserConversationText.SHOW_BALANCE]),
                    show_balance,
                ),
                MessageHandler(
                    filters.Text([UserConversationText.CREATE_QR]),
                    generate_qr_code,
                ),
                MessageHandler(
                    filters.User(settings.admin_ids)
                    and filters.Text([AdminConversationText.FIND_USER]),
                    ask_user_nickname,
                ),
            ],
            AdminConversationChoices.ASK_USER_NICKNAME: [
                MessageHandler(
                    filters.User(settings.admin_ids),
                    find_user,
                ),
            ],
            AdminConversationChoices.FIND_USER: [
                MessageHandler(
                    filters.User(settings.admin_ids)
                    and filters.Text(
                        [AdminConversationText.INCREASE_USER_BALANCE]
                    ),
                    before_increase_user_balance,
                ),
                MessageHandler(
                    filters.User(settings.admin_ids)
                    and filters.Text(
                        [AdminConversationText.DECREASE_USER_BALANCE]
                    ),
                    before_decrease_user_balance,
                ),
            ],
            AdminConversationChoices.INCREASE_USER_BALANCE: [
                MessageHandler(
                    filters.User(settings.admin_ids)
                    and filters.Regex(r"^\d+$"),
                    increase_user_balance,
                ),
            ],
            AdminConversationChoices.DECREASE_USER_BALANCE: [
                MessageHandler(
                    filters.User(settings.admin_ids)
                    and filters.Regex(r"^\d+$"),
                    decrease_user_balance,
                ),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    ),
]
