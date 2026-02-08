from typing import Optional

from sqlalchemy import select, insert, literal
from sqlalchemy.ext.asyncio import AsyncSession

import src.resources.database.models as models


async def create_planet(
    session: AsyncSession,
    planet_name: str,
    sector_name: str,
    scarce_cargo_name: str = None,
) -> Optional[models.Planet]:

    select_stmt = select(
        literal(planet_name),
        models.Sector.sector_id,
        select(models.CargoType.cargo_type_id).where(models.CargoType.name == scarce_cargo_name).scalar_subquery(),
    ).where(models.Sector.name == sector_name)

    insert_stmt = insert(models.Planet).from_select(["name", "sector_id", "scarce_cargo_type_id"], select_stmt).returning(models.Planet)

    result = await session.scalar(insert_stmt)

    return result
