import pytest
from grpclib.testing import ChannelFor

from src.generated.co.za.planet import (
    CreateSectorRequest,
    PlanetAdminStub,
    StatusCode,
    CreatePlanetRequest,
    CreateCargoTypeRequest,
)

from src.strings import en_za as strings


@pytest.mark.asyncio
async def test_create_planet(planets_service):
    async with ChannelFor([planets_service]) as channel:
        stub = PlanetAdminStub(channel)
        planet_1 = "Planet 1"
        planet_2 = "Planet 2"
        sector_name = "Sector 1"
        cargo_name = "Cargo 1"

        create_sector_empty = await stub.create_sector(CreateSectorRequest())
        assert create_sector_empty.message.status_code == StatusCode.VALIDATION_ERROR
        assert create_sector_empty.message.error_fields == {"sector_name": strings.validation_error_required_field}

        create_sector_success = await stub.create_sector(CreateSectorRequest(sector_name=sector_name))
        assert create_sector_success.message.status_code == StatusCode.SUCCESS

        create_empty_cargo_response = await stub.create_cargo_type(CreateCargoTypeRequest())
        assert create_empty_cargo_response.message.status_code == StatusCode.VALIDATION_ERROR

        create_cargo_type_success = await stub.create_cargo_type(CreateCargoTypeRequest(cargo_name=cargo_name))
        assert create_cargo_type_success.message.status_code == StatusCode.SUCCESS

        create_empty_planet_response = await stub.create_planet(CreatePlanetRequest())
        assert create_empty_planet_response.message.status_code == StatusCode.VALIDATION_ERROR

        # planet with not cargo type
        create_planet_success_response = await stub.create_planet(
            CreatePlanetRequest(
                planet_name=planet_1,
                sector_name=sector_name,
            )
        )
        assert create_planet_success_response.message.status_code == StatusCode.SUCCESS

        # planet with nonexisting sector
        create_planet_response_error = await stub.create_planet(
            CreatePlanetRequest(
                planet_name=planet_1,
                sector_name="Not found",
            )
        )
        assert create_planet_response_error.message.status_code == StatusCode.INTERNAL_ERROR

        # planet with a scarce cargo
        create_planet_success_response_1 = await stub.create_planet(
            CreatePlanetRequest(
                planet_name=planet_2,
                sector_name=sector_name,
                scarce_cargo_name=cargo_name,
            )
        )
        assert create_planet_success_response_1.message.status_code == StatusCode.SUCCESS
