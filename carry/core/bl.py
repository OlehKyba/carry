from io import BytesIO

import qrcode
from qrcode.image.pure import PyPNGImage

from carry.config import settings


def is_admin(user_id: int) -> bool:
    return user_id in settings.admin_ids


def create_qr_code(url: str) -> BytesIO:
    qr_code = qrcode.make(url, image_factory=PyPNGImage)
    buffer = BytesIO()
    qr_code.save(buffer)
    buffer.seek(0)
    return buffer
