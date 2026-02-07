from src.generated.co.za.planet import (
    PlanetAdminBase,
    CreateSectorRequest,
    CreateSectorResponse,
    ResponseMessage,
    StatusCode,
)
from src.resources.database.config import Session
from src.resources.database.planets_admin_queries import create_sector

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

                sector = await create_sector(session, create_sector_request.sector_name)

                return CreateSectorResponse(
                    message=ResponseMessage(status_code=StatusCode.SUCCESS),
                    sector_id=sector.sector_id,
                )

        except Exception:
            import traceback

            traceback.print_exc()
            raise
