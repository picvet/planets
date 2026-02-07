import asyncio
import os
import signal

import pytest
import pytest_asyncio
from sqlalchemy import text
from testing.postgresql import Postgresql

from src.migrate import migrate as run_migrations
from src.resources.database.config import Session, configure_database
from src.resources.database.models import base_metadata


class PgTest(Postgresql):
    def terminate(self, *args):
        super(Postgresql, self).terminate(signal.SIGTERM)


@pytest.fixture(scope="session")
def event_loop_policy():
    """
    Returns the policy instead of the loop instance.
    Matches the working HR project strategy.
    """
    if os.name == "nt":
        return asyncio.WindowsSelectorEventLoopPolicy()
    else:
        return asyncio.get_event_loop_policy()


@pytest_asyncio.fixture(scope="session")
async def db_setup(event_loop_policy):
    """
    Sets up the ephemeral Postgres database, configures the engine, and runs migrations.
    """
    pg_database = PgTest()
    raw_url = pg_database.url()
    test_db_url = raw_url.replace("postgresql://", "postgresql+psycopg://", 1)

    configure_database(test_db_url)

    from src.resources.database.config import session_maker

    engine = session_maker.kw["bind"]

    try:
        async with engine.begin() as conn:
            await conn.execute(text("CREATE SCHEMA IF NOT EXISTS planet"))

            await conn.run_sync(base_metadata.create_all)

        run_migrations()

        yield test_db_url
    finally:
        await engine.dispose()
        if pg_database is not None:
            pg_database.stop(signal.SIGTERM)


@pytest_asyncio.fixture(scope="session")
async def planets_service(db_setup):
    """
    Provides the service instance once the DB is ready.
    """
    from src.services.planets import PlanetsService

    return PlanetsService()
