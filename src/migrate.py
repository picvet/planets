import os

from alembic import config, command


def migrate():
    """Alembic upgrade"""
    alembic_cfg = config.Config("alembic.ini")
    alembic_cfg.set_main_option("script_location", "alembic")
    alembic_cfg.set_main_option("sqlalchemy.url", str(os.getenv("DATABASE_URL")))
    command.upgrade(alembic_cfg, "head")
    print("Alembic migration success.")
