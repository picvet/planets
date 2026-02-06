from datetime import datetime
from typing import Annotated

from sqlalchemy import MetaData, func, BigInteger, String, ForeignKey, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import DeclarativeBase, declarative_mixin, Mapped, mapped_column, relationship
from sqlalchemy_mixins.repr import ReprMixin

big_int_pk = Annotated[int, mapped_column(BigInteger, primary_key=True)]
big_int = Annotated[int, mapped_column(BigInteger)]

base_metadata = MetaData(
    schema="planet",
    naming_convention={
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

    date_created: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)


class BaseModel(DefaultMixin, ReprMixin, DeclarativeBase):
    metadata = base_metadata


class Planet(BaseModel):
    __tablename__ = "planet"

    planet_id: Mapped[big_int_pk]
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    sector: Mapped[str] = mapped_column(String, nullable=False)

    scarce_cargo_type_id: Mapped[big_int | None] = mapped_column(ForeignKey("cargo_type.cargo_type_id"), nullable=True)

    r_starships: Mapped[list["StarShip"]] = relationship(back_populates="r_planet")
    r_scarce_cargo_type: Mapped["CargoType"] = relationship()


class CargoType(BaseModel):
    __tablename__ = "cargo_type"

    cargo_type_id: Mapped[big_int_pk]
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    r_manifests: Mapped[list["Manifest"]] = relationship(back_populates="r_cargo_type", cascade="all, delete-orphan")


class StarShip(BaseModel):
    __tablename__ = "starship"

    starship_id: Mapped[big_int_pk]
    name: Mapped[str] = mapped_column(String, nullable=False)
    model: Mapped[str] = mapped_column(String, nullable=False)

    planet_id: Mapped[big_int] = mapped_column(ForeignKey="planet.planet_id", nullable=False)

    r_planet: Mapped["Planet"] = relationship(back_populates="r_starships")
    r_manifests: Mapped[list["Manifest"]] = relationship(back_populates="r_starship", cascade="all, delete-orphan")


class Manifest(BaseModel):
    __tablename__ = "manifest"
    __table_args__ = (
        UniqueConstraint(
            "starship_id",
            "cargo_type_id",
            name="uq_manifest_starship_cargo",
        ),
        CheckConstraint(
            "quantity >= 0",
            name="ck_manifest_quantity_non_negative",
        ),
    )

    manifest_id: Mapped[big_int_pk]

    starship_id: Mapped[big_int] = mapped_column(ForeignKey="starship.starship_id", nullable=False)

    cargo_type_id: Mapped[big_int] = mapped_column(ForeignKey("cargo_type.cargo_type_id", nullable=False))

    quantity: Mapped[big_int] = mapped_column(nullable=False, default=0)

    r_starship: Mapped["StarShip"] = relationship(back_populates="r_manifests")
    r_cargo_type: Mapped["CargoType"] = relationship(back_populates="r_manifests")
