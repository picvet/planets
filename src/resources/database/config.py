import os
from asyncio import current_task

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import async_sessionmaker, async_scoped_session, create_async_engine

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_async_engine(DATABASE_URL)
session_factory = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

Session = async_scoped_session(session_factory, scopefunc=current_task)
