from typing import Optional

from sqlalchemy import select, insert, literal
from sqlalchemy.ext.asyncio import AsyncSession

import src.resources.database.models as models


async def create_planet_db(
    session: AsyncSession,
    planet_name: str,
    sector_id: str,
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
