from io import BytesIO

import qrcode
from qrcode.image.pure import PyPNGImage
from sqlalchemy.dialects.postgresql import insert

from carry.context import ctx
from carry.config import settings
from carry.db import users


def is_admin(user_id: int) -> bool:
    return user_id in settings.admin_ids


def create_qr_code(url: str) -> BytesIO:
    qr_code = qrcode.make(url, image_factory=PyPNGImage)
    buffer = BytesIO()
    qr_code.save(buffer)
    buffer.seek(0)
    return buffer


async def upsert_user(
    user_id: int,
    first_name: str,
    last_name: str | None,
    username: str | None,
) -> None:
    set_values = {
        'first_name': first_name,
        'last_name': last_name,
        'username': username,
    }
    query = (
        insert(users)
        .values(
            id=user_id,
            **set_values,
        ).on_conflict_do_update(
            'users_pkey',
            set_=set_values,
        )
    )
    await ctx.db_session.execute(query)
