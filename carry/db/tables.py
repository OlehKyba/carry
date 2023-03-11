from sqlalchemy import Table, Column, Integer, String

from carry.db.core import Base


users = Table(
    'users',
    Base.metadata,
    Column('id', Integer, primary_key=True),
    Column('first_name', String(120), nullable=False),
    Column('last_name', String(120), nullable=True),
    Column('username', String(120), nullable=True),
    Column('bonuses', Integer, default=0, nullable=False),
)
