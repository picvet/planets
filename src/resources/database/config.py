import json
from asyncio import current_task
from decimal import Decimal

from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import async_sessionmaker, async_scoped_session, create_async_engine


def _default(val):
    if isinstance(val, Decimal):
        return str(val)
    raise TypeError()


def dumps(d):
    return json.dumps(d, default=_default)


session_maker = async_sessionmaker(expire_on_commit=False)
Session = async_scoped_session(session_maker, scopefunc=current_task)


def configure_database(connection_string: str | URL, database_pool_size: int = 10, database_overflow_size: int = 40):
    session_maker.configure(
        bind=create_async_engine(
            url=connection_string,
            pool_pre_ping=True,
            json_serializer=dumps,
            pool_recycle=600,
            pool_size=database_pool_size,
            max_overflow=database_overflow_size,
        )
    )
