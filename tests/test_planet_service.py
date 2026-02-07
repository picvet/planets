import pytest
from grpclib.testing import ChannelFor

from src.generated.co.za.planet import CreateSectorRequest, PlanetAdminStub, StatusCode


@pytest.mark.asyncio
async def test_create_sector_success(planets_service):
    async with ChannelFor([planets_service]) as channel:
        stub = PlanetAdminStub(channel)
        sector_name = "Orion Nebula"
        request = CreateSectorRequest(sector_name=sector_name)
        response = await stub.create_sector(request)
        print(response)
        assert response.message.status_code == StatusCode.SUCCESS
