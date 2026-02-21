from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.sync import update

import src.resources.database.models as models


async def move_starship_to_planet(session: AsyncSession, starship_id: int, planet_id: int) -> models.StarShip:
    stmt = (
        update(models.StarShip)
        .where(
            models.StarShip.starship_id == starship_id,
            models.StarShip.planet_id != planet_id,
        )
        .values(planet_id=planet_id)
        .returning(models.StarShip)
    )

    result = await session.execute(stmt)
    starship = result.scalar_one_or_none()
    if starship:
        await session.commit()
    return starship
