from src.generated.co.za.planet import PlanetUserBase, MoveStarshipResponse, MoveStarshipRequest, ResponseMessage, StatusCode
from src.resources.database.config import Session
from src.resources.database.planets_user_queries import move_starship_to_planet

from src.strings import en_za as strings


class PlanetsUserService(PlanetUserBase):
    async def move_starship(self, move_starship_request: "MoveStarshipRequest") -> "MoveStarshipResponse":
        errors = {}

        if not move_starship_request.starship_id:
            errors["starship_id"] = strings.validation_error_required_field
        if not move_starship_request.planet_id:
            errors["planet_id"] = strings.validation_error_required_field

        if errors:
            return MoveStarshipResponse(message=ResponseMessage(status_code=StatusCode.VALIDATION_ERROR))

        async with Session() as session:
            starship = await move_starship_to_planet(
                session=session,
                starship_id=move_starship_request.starship_id,
                planet_id=move_starship_request.planet_id,
            )

            if not starship:
                return MoveStarshipResponse(message=ResponseMessage(status_code=StatusCode.NOT_FOUND))

            return MoveStarshipResponse(message=ResponseMessage(status_code=StatusCode.SUCCESS))
