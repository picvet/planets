import pytest
from grpclib.testing import ChannelFor

from src.generated.co.za.planet import CreateSectorRequest, PlanetAdminStub, StatusCode, CreatePlanetRequest


@pytest.mark.asyncio
async def test_create_planet(planets_service):
    async with ChannelFor([planets_service]) as channel:
        stub = PlanetAdminStub(channel)
        sector_name = "Orion Nebula"
        request = CreateSectorRequest(sector_name=sector_name)
        response = await stub.create_sector(request)
        assert response.message.status_code == StatusCode.SUCCESS

        create_empty_planet_response = await stub.create_planet(CreatePlanetRequest())
        assert create_empty_planet_response.message.status_code == StatusCode.VALIDATION_ERROR

        create_planet_response_success = await stub.create_planet(
            CreatePlanetRequest(
                planet_name="Planet 1",
                sector_name=sector_name,
            )
        )
        assert create_planet_response_success.message.status_code == StatusCode.SUCCESS

        create_planet_response_error = await stub.create_planet(
            CreatePlanetRequest(
                planet_name="Planet 1",
                sector_name="Not found",
            )
        )
        assert create_planet_response_error.message.status_code == StatusCode.INTERNAL_ERROR
