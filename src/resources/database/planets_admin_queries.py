from typing import Optional, Sequence

from sqlalchemy import select, insert, literal
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

import src.resources.database.models as models
import src.generated.co.za.planet as proto


async def create_planet_db(
    session: AsyncSession,
    planet_name: str,
    sector_id: int,
) -> Optional[models.Planet]:

    select_stmt = select(
        literal(planet_name).label("name"),
        models.Sector.sector_id.label("sector_id"),
    ).where(models.Sector.sector_id == sector_id)

    insert_stmt = (
        insert(models.Planet)
        .from_select(
            ["name", "sector_id"],
            select_stmt,
        )
        .returning(models.Planet)
    )

    result = await session.scalar(insert_stmt)
    await session.commit()
    return result


async def get_or_create_sector_db(
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


async def bulk_create_cargo_type(
    session: AsyncSession,
    cargo_names: list[str],
) -> Sequence[models.CargoType]:
    names_to_insert = [{"name": name} for name in cargo_names]

    insert_stmt = pg_insert(models.CargoType).values(names_to_insert)

    upsert_stmt = insert_stmt.on_conflict_do_nothing(
        index_elements=[models.CargoType.name],
    ).returning(models.CargoType)

    result = await session.execute(upsert_stmt)
    await session.commit()
    return result.scalars().all()


async def create_starship_db(
    session: AsyncSession,
    starship_name: str,
    starship_model: str,
    planet_id: int,
) -> Optional[models.StarShip]:
    select_stmt = select(
        literal(starship_name).label("name"),
        literal(starship_model).label("model"),
        models.Planet.planet_id.label("planet_id"),
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


async def bulk_create_manifest(
    session: AsyncSession,
    manifests: list[proto.ManifestObject],
) -> Sequence[models.Manifest]:

    values = [
        {
            "starship_id": m.starship_id,
            "cargo_type_id": m.cargo_type_id,
            "quantity": m.quantity,
        }
        for m in manifests
    ]

    if not values:
        return []

    insert_stmt = pg_insert(models.Manifest).values(values)

    upsert_stmt = insert_stmt.on_conflict_do_update(
        constraint="uq_manifest_starship_cargo",
        set_={"quantity": models.Manifest.quantity + insert_stmt.excluded.quantity},
    ).returning(models.Manifest)

    try:
        result = await session.execute(upsert_stmt)
        await session.commit()
    except IntegrityError:
        await session.rollback()
        return []

    return result.scalars().all()
