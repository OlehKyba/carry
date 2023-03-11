import asyncio
from enum import IntEnum, StrEnum
from typing import TYPE_CHECKING, Final

from telegram import (
    Update,
    KeyboardButton,
    ReplyKeyboardMarkup,
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
from carry.core.repositories import NegativeBonusesError

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
    CANCEL_COMMAND = 2
    ASK_USER_NICKNAME = 3
    SHOW_USERS = 4
    FIND_USER = 5
    SHOW_ALL_USERS = 6
    INCREASE_USER_BALANCE = 7
    DECREASE_USER_BALANCE = 8


class AdminConversationText(StrEnum):
    CANCEL_COMMAND = "Зупинити команду ❌"
    FIND_USER = "Знайти користувача 🔍"
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

BALANCE_OPERATIONS_KEYBOARD = ReplyKeyboardMarkup(
    [
        [
            KeyboardButton(
                AdminConversationText.INCREASE_USER_BALANCE,
            ),
            KeyboardButton(
                AdminConversationText.DECREASE_USER_BALANCE,
            ),
        ],
        [
            KeyboardButton(
                AdminConversationText.CANCEL_COMMAND,
            ),
        ],
    ],
    resize_keyboard=True,
)
CANCEL_COMMAND_KEYBOARD = ReplyKeyboardMarkup(
    [
        [
            KeyboardButton(
                AdminConversationText.CANCEL_COMMAND,
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


def _choose_keyboard(user_id: int) -> ReplyKeyboardMarkup:
    return ADMIN_KEYBOARD if is_admin(user_id) else USER_KEYBOARD


def _create_params(user: User, bonuses: int) -> dict:
    return {
        'user_info': user.shor_info,
        'bonuses': bonuses,
        'total_bonuses': user.bonuses,
    }


@ctx.with_request_context
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = User.from_telegram(
        tg_user=update.message.from_user,
        chat_id=update.message.chat_id,
    )
    await ctx.user_repository.upsert_user(user)

    first_message = await update.message.reply_text(
        render_template("telegram/help.jinja2"),
        reply_markup=_choose_keyboard(user.id),
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
    context.user_data.clear()
    await update.message.reply_text(
        "Ви скасували команду 🙈",
        reply_markup=_choose_keyboard(update.message.from_user.id),
        reply_to_message_id=update.message.id,
    )
    return AdminConversationChoices.AFTER_START


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
        f"Напишіть нікнейм користувача ✍️",
        reply_markup=CANCEL_COMMAND_KEYBOARD,
    )
    return AdminConversationChoices.ASK_USER_NICKNAME


@ctx.with_request_context
async def find_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    username = update.message.text
    user = await ctx.user_repository.fetch_user_by_username(username)

    if not user:
        await update.message.reply_text(
            f'Користувача з нікнеймом *{username}* не знайдено! 😖',
            reply_markup=_choose_keyboard(update.message.from_user.id),
            parse_mode=ParseMode.MARKDOWN,
        )
        return AdminConversationChoices.AFTER_START

    context.user_data["user_id"] = user.id
    await update.message.reply_text(
        f"У користувача *{user.shor_info}* на рахунку *{user.bonuses}* бонусів ☺️",
        reply_markup=BALANCE_OPERATIONS_KEYBOARD,
        parse_mode=ParseMode.MARKDOWN,
    )
    return AdminConversationChoices.FIND_USER


@ctx.with_request_context
async def deep_link_start(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    user_id = int(context.args[0])

    user = await ctx.user_repository.fetch_user_by_id(user_id)
    context.user_data["user_id"] = user_id

    await update.message.reply_text(
        f"У користувача *{user.shor_info}* на рахунку *{user.bonuses}* бонусів ☺️",
        reply_markup=BALANCE_OPERATIONS_KEYBOARD,
        parse_mode=ParseMode.MARKDOWN,
    )
    return AdminConversationChoices.FIND_USER


async def before_increase_user_balance(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    await update.message.reply_text(
        "Напишіть скільки бонусів ви хочете додати ✍️",
        reply_markup=CANCEL_COMMAND_KEYBOARD,
    )
    return AdminConversationChoices.INCREASE_USER_BALANCE


async def before_decrease_user_balance(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    await update.message.reply_text(
        f"Напишіть скільки бонусів ви хочете забрати ✍️",
        reply_markup=CANCEL_COMMAND_KEYBOARD,
    )
    return AdminConversationChoices.DECREASE_USER_BALANCE


@ctx.with_request_context
async def increase_user_balance(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    user_id = context.user_data["user_id"]
    bonuses = int(update.message.text)
    bot = update.get_bot()

    user = await ctx.user_repository.increase_user_balance(
        user_id=user_id,
        bonuses=bonuses,
    )
    context.user_data.clear()

    params = _create_params(user, bonuses)
    await asyncio.gather(
        update.message.reply_text(
            render_template('telegram/increase_bonuses/admin.jinja2', params),
            reply_markup=ADMIN_KEYBOARD,
            parse_mode=ParseMode.HTML,
        ),
        bot.send_message(
            chat_id=user.chat_id,
            text=render_template(
                'telegram/increase_bonuses/user.jinja2', params
            ),
            parse_mode=ParseMode.HTML,
        ),
    )
    return AdminConversationChoices.AFTER_START


@ctx.with_request_context
async def decrease_user_balance(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    user_id = context.user_data["user_id"]
    bonuses = int(update.message.text)
    bot = update.get_bot()

    try:
        user = await ctx.user_repository.decrease_user_balance(
            user_id=user_id,
            bonuses=bonuses,
        )
    except NegativeBonusesError:
        await update.message.reply_text(
            text="Не можна зняти більше бонусів, ніж є у користувача 🤬",
            reply_markup=ADMIN_KEYBOARD,
            reply_to_message_id=update.message.id,
        )
    else:
        params = _create_params(user, bonuses)
        await asyncio.gather(
            update.message.reply_text(
                render_template(
                    'telegram/decrease_bonuses/admin.jinja2', params
                ),
                reply_markup=ADMIN_KEYBOARD,
                parse_mode=ParseMode.HTML,
            ),
            bot.send_message(
                chat_id=user.chat_id,
                text=render_template(
                    'telegram/decrease_bonuses/user.jinja2', params
                ),
                parse_mode=ParseMode.HTML,
            ),
        )

    context.user_data.clear()
    return AdminConversationChoices.AFTER_START


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
                    filters.Text([AdminConversationText.CANCEL_COMMAND]),
                    cancel,
                ),
                MessageHandler(
                    filters.User(settings.admin_ids)
                    and filters.Regex(
                        r'^[A-Za-z0-9]+([A-Za-z0-9]*|[._-]?[A-Za-z0-9]+)*$'
                    ),
                    find_user,
                ),
            ],
            AdminConversationChoices.FIND_USER: [
                MessageHandler(
                    filters.Text([AdminConversationText.CANCEL_COMMAND]),
                    cancel,
                ),
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
                    filters.Text([AdminConversationText.CANCEL_COMMAND]),
                    cancel,
                ),
                MessageHandler(
                    filters.User(settings.admin_ids)
                    and filters.Regex(r"^\d+$"),
                    increase_user_balance,
                ),
            ],
            AdminConversationChoices.DECREASE_USER_BALANCE: [
                MessageHandler(
                    filters.Text([AdminConversationText.CANCEL_COMMAND]),
                    cancel,
                ),
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
