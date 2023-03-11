from sqlalchemy import Table, Column, String, Integer, CheckConstraint

from carry.db.core import metadata

users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("chat_id", Integer, nullable=False),
    Column("first_name", String(120), nullable=False),
    Column("last_name", String(120), nullable=True),
    Column("username", String(120), nullable=True),
    Column("bonuses", Integer, default=0, nullable=False),
    CheckConstraint("bonuses >= 0"),
)
