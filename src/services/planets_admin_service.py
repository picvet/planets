from src.generated.co.za.planet import (
    PlanetAdminBase,
    CreateSectorRequest,
    CreateSectorResponse,
    ResponseMessage,
    StatusCode,
    CreatePlanetRequest,
    CreatePlanetResponse,
)
from src.resources.database.config import Session

import src.resources.database.models as models
from src.resources.database.planets_admin_queries import create_planet
from src.strings import en_za as strings


class PlanetsService(PlanetAdminBase):

    async def create_sector(self, create_sector_request: CreateSectorRequest) -> CreateSectorResponse:
        try:
            async with Session() as session:
                if not create_sector_request.sector_name:
                    return CreateSectorResponse(
                        message=ResponseMessage(
                            status_code=StatusCode.VALIDATION_ERROR,
                            error_fields={"sector_name": strings.validation_error_required_field},
                        )
                    )

                sector = models.Sector(name=create_sector_request.sector_name)
                session.add(sector)
                await session.flush()
                await session.commit()

                return CreateSectorResponse(
                    message=ResponseMessage(status_code=StatusCode.SUCCESS),
                    sector_id=sector.sector_id,
                )

        except Exception:
            import traceback

            traceback.print_exc()
            raise

    async def create_planet(self, create_planet_request: "CreatePlanetRequest") -> "CreatePlanetResponse":
        async with Session() as session:
            errors = {}

            if not create_planet_request.planet_name:
                errors["planet_name"] = strings.validation_error_required_field
            if not create_planet_request.sector_name:
                errors["sector_name"] = strings.validation_error_required_field

            if errors:
                return CreatePlanetResponse(message=ResponseMessage(status_code=StatusCode.VALIDATION_ERROR, error_fields=errors))

            planet = await create_planet(session, create_planet_request.planet_name, create_planet_request.sector_name, create_planet_request.scarce_cargo_name)

            if not planet:
                return CreatePlanetResponse(message=ResponseMessage(status_code=StatusCode.INTERNAL_ERROR))

            return CreatePlanetResponse(message=ResponseMessage(status_code=StatusCode.SUCCESS), planet_id=planet.planet_id)
