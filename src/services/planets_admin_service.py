from src.generated.co.za.planet import (
    PlanetAdminBase,
    CreateSectorRequest,
    CreateSectorResponse,
    ResponseMessage,
    StatusCode,
    CreatePlanetRequest,
    CreatePlanetResponse,
    CreateCargoTypeResponse,
    CreateCargoTypeRequest,
)
from src.resources.database.config import Session

import src.resources.database.models as models
from src.resources.database.planets_admin_queries import create_planet
from src.strings import en_za as strings


class PlanetsService(PlanetAdminBase):

    async def create_sector(self, create_sector_request: CreateSectorRequest) -> CreateSectorResponse:
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
            await session.commit()

            return CreateSectorResponse(
                message=ResponseMessage(status_code=StatusCode.SUCCESS),
                sector_id=sector.sector_id,
            )

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

    async def create_cargo_type(self, create_cargo_type_request: "CreateCargoTypeRequest") -> "CreateCargoTypeResponse":
        async with Session() as session:
            if not create_cargo_type_request.cargo_name:
                return CreateCargoTypeResponse(
                    message=ResponseMessage(
                        status_code=StatusCode.VALIDATION_ERROR,
                        error_fields={"cargo_name": strings.validation_error_required_field},
                    ),
                )

            cargo = models.CargoType(name=create_cargo_type_request.cargo_name)
            session.add(cargo)
            await session.commit()
            return CreateCargoTypeResponse(
                message=ResponseMessage(status_code=StatusCode.SUCCESS),
                cargo_type_id=cargo.cargo_type_id,
            )
