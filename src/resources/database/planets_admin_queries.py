import src.resources.database.models as models
from src.resources.database.config import Session


async def create_sector(
    session: Session,
    sector_name: str,
) -> models.Sector:
    sector = models.Sector(name=sector_name)
    session.add(sector)
    await session.commit()
    await session.refresh(sector)
    return sector
