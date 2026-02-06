from typing import Annotated

from sqlalchemy import MetaData, func, BigInteger
from sqlalchemy.orm import DeclarativeBase, declarative_mixin, Mapped, mapped_column
from datetime import datetime
from sqlalchemy_mixins.repr import ReprMixin

int_pk = Annotated[int, mapped_column(primary_key = True)]
big_int_pk = Annotated[int, mapped_column(BigInteger, primary_key = True)]
big_int = Annotated[int, mapped_column(BigInteger)]

base_metadata = MetaData(
    schema = "planet",
    naming_convention = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
        },
    )

@declarative_mixin
class DefaultMixin:
    """
    Declare common columns for all my tables.

    Documentation: https://docs.sqlalchemy.org/en/13/orm/extensions/declarative/mixins.html
    """
    date_created: Mapped[datetime] = mapped_column(server_default = func.now(), nullable = False)

class BaseModel(DefaultMixin, ReprMixin, DeclarativeBase):
    metadata = base_metadata

class Planet(BaseModel):
    __tablename__ = 'planet'


