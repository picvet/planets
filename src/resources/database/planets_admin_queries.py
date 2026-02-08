from typing import Optional

from sqlalchemy import select, insert, literal, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert as pg_insert

import src.resources.database.models as models


async def create_planet_db(
    session: AsyncSession,
    planet_name: str,
    sector_id: int,
    scarce_cargo_id: int = None,
) -> Optional[models.Planet]:

    select_stmt = select(
        literal(planet_name),
        models.Sector.sector_id,
        select(models.CargoType.cargo_type_id).where(models.CargoType.cargo_type_id == scarce_cargo_id).scalar_subquery(),
    ).where(models.Sector.sector_id == sector_id)

    insert_stmt = (
        insert(models.Planet)
        .from_select(
            ["name", "sector_id", "scarce_cargo_type_id"],
            select_stmt,
        )
        .returning(models.Planet)
    )

    return await session.scalar(insert_stmt)


async def create_starship_db(
    session: AsyncSession,
    starship_name: str,
    starship_model: str,
    planet_id: int,
) -> Optional[models.StarShip]:
    select_stmt = select(
        literal(starship_name),
        literal(starship_model),
        models.Planet.planet_id,
    ).where(models.Planet.planet_id == planet_id)

    insert_stmt = (
        insert(models.StarShip)
        .from_select(
            ["name", "model", "planet_id"],
            select_stmt,
        )
        .returning(models.StarShip)
    )

    result = await session.execute(insert_stmt)
    return result.scalar_one_or_none()


async def create_manifest_db(
    session: AsyncSession,
    quantity: int,
    starship_id: int,
    cargo_type_id: int,
) -> Optional[models.Manifest]:

    select_stmt = select(
        literal(starship_id).label("starship_id"),
        literal(cargo_type_id).label("cargo_type_id"),
        literal(quantity).label("quantity"),
    ).where(
        and_(
            select(models.StarShip.starship_id).where(models.StarShip.starship_id == starship_id).exists(),
            select(models.CargoType.cargo_type_id).where(models.CargoType.cargo_type_id == cargo_type_id).exists(),
        )
    )

    stmt = pg_insert(models.Manifest).from_select(
        ["starship_id", "cargo_type_id", "quantity"],
        select_stmt,
    )

    upsert_stmt = stmt.on_conflict_do_update(
        constraint="uq_manifest_starship_cargo",
        set_={"quantity": quantity},
    ).returning(models.Manifest)

    return (await session.execute(upsert_stmt)).scalar_one_or_none()
