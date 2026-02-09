from typing import Optional

from sqlalchemy import select, insert, literal
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

import src.resources.database.models as models


async def create_planet_db(
    session: AsyncSession,
    planet_name: str,
    sector_id: int,
    scarce_cargo_id: int = None,
) -> Optional[models.Planet]:

    select_stmt = select(
        literal(planet_name).label("name"),
        models.Sector.sector_id.label("sector_id"),
        select(models.CargoType.cargo_type_id)
        .where(
            models.CargoType.cargo_type_id == scarce_cargo_id,
        )
        .scalar_subquery()
        .label("scarce_cargo_type_id"),
    ).where(models.Sector.sector_id == sector_id)

    insert_stmt = (
        insert(models.Planet)
        .from_select(
            ["name", "sector_id", "scarce_cargo_type_id"],
            select_stmt,
        )
        .returning(models.Planet)
    )

    result = await session.scalar(insert_stmt)
    await session.commit()
    return result


async def create_sector_db(
    session: AsyncSession,
    sector_name: str,
) -> models.Sector:

    insert_sector = (
        pg_insert(models.Sector)
        .values(name=sector_name)
        .on_conflict_do_update(
            index_elements=[models.Sector.name],
            set_={"name": sector_name},
        )
        .returning(models.Sector)
    )

    result = await session.execute(insert_sector)
    await session.commit()
    return result.scalar_one()


async def create_cargo_db(
    session: AsyncSession,
    cargo_name: str,
) -> models.CargoType:

    insert_stmt = (
        pg_insert(models.CargoType)
        .values(name=cargo_name)
        .on_conflict_do_update(
            index_elements=[models.CargoType.name],
            set_={"name": cargo_name},
        )
        .returning(models.CargoType)
    )

    result = await session.execute(insert_stmt)
    await session.commit()
    return result.scalar_one()


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
    await session.commit()
    return result.scalar_one_or_none()


async def create_manifest_db(
    session: AsyncSession,
    quantity: int,
    starship_id: int,
    cargo_type_id: int,
) -> Optional[models.Manifest]:

    exists_cte = (
        select(
            literal(starship_id).label("starship_id"),
            literal(cargo_type_id).label("cargo_type_id"),
            literal(quantity).label("quantity"),
        )
        .where(
            select(models.StarShip).where(models.StarShip.starship_id == starship_id).exists(),
            select(models.CargoType).where(models.CargoType.cargo_type_id == cargo_type_id).exists(),
        )
        .cte("exists_cte")
    )

    insert_stmt = (
        pg_insert(models.Manifest)
        .from_select(
            ["starship_id", "cargo_type_id", "quantity"],
            select(
                exists_cte.c.starship_id,
                exists_cte.c.cargo_type_id,
                exists_cte.c.quantity,
            ),
        )
        .on_conflict_do_update(
            constraint="uq_manifest_starship_cargo",
            set_={
                "quantity": models.Manifest.quantity + quantity,
            },
        )
        .returning(models.Manifest)
    )

    result = await session.execute(insert_stmt)
    await session.commit()

    return result.scalar_one_or_none()
