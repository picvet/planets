from src.generated.co.za.planet import (
    PlanetAdminBase,
    ResponseMessage,
    StatusCode,
    CreatePlanetRequest,
    CreatePlanetResponse,
    CreateStarshipResponse,
    CreateStarshipRequest,
    GetOrCreateSectorRequest,
    GetOrCreateSectorResponse,
    BulkCreateCargoTypeResponse,
    BulkCreateCargoTypeRequest,
    BulkCreateManifestResponse,
    BulkCreateManifestRequest,
)
from src.resources.database.config import Session
from src.resources.database.planets_admin_queries import (
    create_planet_db,
    create_starship_db,
    bulk_create_manifest,
    bulk_create_cargo_type,
    get_or_create_sector_db,
)
from src.strings import en_za as strings


class PlanetsService(PlanetAdminBase):

    async def get_or_create_sector(self, create_sector_request: GetOrCreateSectorRequest) -> GetOrCreateSectorResponse:
        async with Session() as session:
            if not create_sector_request.sector_name:
                return GetOrCreateSectorResponse(
                    message=ResponseMessage(
                        status_code=StatusCode.VALIDATION_ERROR,
                        error_fields={"sector_name": strings.validation_error_required_field},
                    ),
                )

            sector = await get_or_create_sector_db(
                session=session,
                sector_name=create_sector_request.sector_name,
            )

            return GetOrCreateSectorResponse(
                message=ResponseMessage(status_code=StatusCode.SUCCESS),
                sector_id=sector.sector_id,
            )

    async def create_planet(self, create_planet_request: "CreatePlanetRequest") -> "CreatePlanetResponse":
        async with Session() as session:
            errors = {}

            if not create_planet_request.planet_name:
                errors["planet_name"] = strings.validation_error_required_field
            if not create_planet_request.sector_id:
                errors["sector_id"] = strings.validation_error_required_field

            if errors:
                return CreatePlanetResponse(
                    message=ResponseMessage(
                        status_code=StatusCode.VALIDATION_ERROR,
                        error_fields=errors,
                    ),
                )

            planet = await create_planet_db(
                session=session,
                planet_name=create_planet_request.planet_name,
                sector_id=create_planet_request.sector_id,
            )

            if not planet:
                return CreatePlanetResponse(message=ResponseMessage(status_code=StatusCode.INTERNAL_ERROR))

            return CreatePlanetResponse(
                message=ResponseMessage(status_code=StatusCode.SUCCESS),
                planet_id=planet.planet_id,
            )

    async def bulk_create_cargo_type(self, bulk_create_cargo_type_request: "BulkCreateCargoTypeRequest") -> "BulkCreateCargoTypeResponse":
        async with Session() as session:
            if not bulk_create_cargo_type_request.cargo_names:
                return BulkCreateCargoTypeResponse(
                    message=ResponseMessage(
                        status_code=StatusCode.VALIDATION_ERROR,
                        error_fields={"cargo_names": strings.validation_error_required_field},
                    ),
                )

            cargos = await bulk_create_cargo_type(
                session=session,
                cargo_names=bulk_create_cargo_type_request.cargo_names,
            )

            if not cargos:
                return BulkCreateCargoTypeResponse(message=ResponseMessage(status_code=StatusCode.ALREADY_EXISTS))

            return BulkCreateCargoTypeResponse(
                message=ResponseMessage(
                    status_code=StatusCode.SUCCESS,
                ),
                cargo_type_ids=[c.cargo_type_id for c in cargos],
            )

    async def create_starship(self, create_starship_request: "CreateStarshipRequest") -> "CreateStarshipResponse":
        async with Session() as session:
            errors = {}

            if not create_starship_request.starship_name:
                errors["starship_name"] = strings.validation_error_required_field
            if not create_starship_request.starship_model:
                errors["starship_model"] = strings.validation_error_required_field
            if not create_starship_request.planet_id:
                errors["planet_id"] = strings.validation_error_required_field

            if errors:
                return CreateStarshipResponse(
                    message=ResponseMessage(status_code=StatusCode.VALIDATION_ERROR, error_fields=errors),
                )

            starship = await create_starship_db(
                session=session,
                starship_name=create_starship_request.starship_name,
                starship_model=create_starship_request.starship_model,
                planet_id=create_starship_request.planet_id,
            )

            if not starship:
                return CreateStarshipResponse(
                    message=ResponseMessage(
                        status_code=StatusCode.NOT_FOUND,
                        status_message=strings.validation_error_planet_id_does_not_exist,
                    ),
                )

            return CreateStarshipResponse(
                message=ResponseMessage(status_code=StatusCode.SUCCESS),
                starship_id=starship.starship_id,
            )

    async def bulk_create_manifest(self, bulk_create_manifest_request: "BulkCreateManifestRequest") -> "BulkCreateManifestResponse":
        async with Session() as session:
            errors = {}
            if not bulk_create_manifest_request.manifests:
                errors["manifests"] = strings.validation_error_required_field

            if errors:
                return BulkCreateManifestResponse(
                    message=ResponseMessage(
                        status_code=StatusCode.VALIDATION_ERROR,
                        error_fields=errors,
                    ),
                )

            manifest = await bulk_create_manifest(
                session=session,
                manifests=bulk_create_manifest_request.manifests,
            )

            if not manifest:
                return BulkCreateManifestResponse(
                    message=ResponseMessage(
                        status_code=StatusCode.NOT_FOUND,
                        status_message=strings.validation_error_invalid_starship_or_cargo_type,
                    ),
                )

            return BulkCreateManifestResponse(
                message=ResponseMessage(status_code=StatusCode.SUCCESS),
                manifest_id=[m.manifest_id for m in manifest],
            )
