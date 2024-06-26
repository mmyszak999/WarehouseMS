from fastapi import APIRouter, FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi_jwt_auth.exceptions import AuthJWTException

from src.apps.emails.routers import email_router
from src.apps.issues.routers import issue_router
from src.apps.products.routers.category_routers import category_router
from src.apps.products.routers.product_routers import product_router
from src.apps.racks.routers import rack_router
from src.apps.receptions.routers import reception_router
from src.apps.sections.routers import section_router
from src.apps.stocks.routers.stock_routers import stock_router
from src.apps.stocks.routers.user_stock_routers import user_stock_router
from src.apps.users.routers import user_router
from src.apps.waiting_rooms.routers import waiting_room_router
from src.apps.warehouse.routers import warehouse_router
from src.core.exceptions import (
    AccountAlreadyActivatedException,
    AccountAlreadyDeactivatedException,
    AccountNotActivatedException,
    AlreadyExists,
    AuthenticationException,
    AuthorizationException,
    CannotMoveIssuedStockException,
    CannotRetrieveIssuedStockException,
    DoesNotExist,
    IsOccupied,
    LegacyProductException,
    MissingIssueDataException,
    MissingProductDataException,
    MissingReceptionDataException,
    NoAvailableSlotsInWaitingRoomException,
    NoAvailableWaitingRoomsException,
    NoAvailableWeightInWaitingRoomException,
    NotEnoughSectionResourcesException,
    NotEnoughWarehouseResourcesException,
    PasswordAlreadySetException,
    PasswordNotSetException,
    ProductIsAlreadyLegacyException,
    RackIsNotEmptyException,
    SectionIsNotEmptyException,
    ServiceException,
    StockAlreadyInWaitingRoomException,
    TooLittleRackLevelsAmountException,
    TooLittleRacksAmountException,
    TooLittleSectionAmountException,
    TooLittleWaitingRoomAmountException,
    TooLittleWaitingRoomSpaceException,
    TooLittleWaitingRoomWeightException,
    TooLittleWeightAmountException,
    UserCantActivateTheirAccountException,
    UserCantDeactivateTheirAccountException,
    WaitingRoomIsNotEmptyException,
    WarehouseAlreadyExistsException,
    WarehouseDoesNotExistException,
    WarehouseIsNotEmptyException,
    WeightLimitExceededException,
)

app = FastAPI(
    title="WarehouseMS", description="Warehouse Management System", version="1.0"
)


root_router = APIRouter(prefix="/api")

root_router.include_router(user_router)
root_router.include_router(email_router)
root_router.include_router(category_router)
root_router.include_router(product_router)
root_router.include_router(rack_router)
root_router.include_router(reception_router)
root_router.include_router(stock_router)
root_router.include_router(user_stock_router)
root_router.include_router(issue_router)
root_router.include_router(waiting_room_router)
root_router.include_router(warehouse_router)
root_router.include_router(section_router)

app.include_router(root_router)


@app.exception_handler(AuthJWTException)
async def handle_auth_jwt_exception(
    request: Request, exception: AuthJWTException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": exception.message}
    )


@app.exception_handler(DoesNotExist)
async def handle_does_not_exist(
    request: Request, exception: DoesNotExist
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(exception)}
    )


@app.exception_handler(AlreadyExists)
async def handle_already_exists(
    request: Request, exception: AlreadyExists
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exception)}
    )


@app.exception_handler(IsOccupied)
async def handle_is_occupied(request: Request, exception: IsOccupied) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exception)}
    )


@app.exception_handler(ServiceException)
async def handle_service_exception(
    request: Request, exception: ServiceException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exception)}
    )


@app.exception_handler(AuthenticationException)
async def handle_authentication_exception(
    request: Request, exception: AuthenticationException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": str(exception)}
    )


@app.exception_handler(AuthorizationException)
async def handle_authorization_exception(
    request: Request, exception: AuthorizationException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN, content={"detail": str(exception)}
    )


@app.exception_handler(AccountNotActivatedException)
async def handle_account_not_activated_exception(
    request: Request, exception: AccountNotActivatedException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exception)}
    )


@app.exception_handler(AccountAlreadyDeactivatedException)
async def handle_account_already_deactivated_exception(
    request: Request, exception: AccountAlreadyDeactivatedException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exception)}
    )


@app.exception_handler(AccountAlreadyActivatedException)
async def handle_account_already_activated_exception(
    request: Request, exception: AccountAlreadyActivatedException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exception)}
    )


@app.exception_handler(UserCantDeactivateTheirAccountException)
async def handle_user_cant_deactivate_their_account_exception(
    request: Request, exception: UserCantDeactivateTheirAccountException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exception)}
    )


@app.exception_handler(UserCantActivateTheirAccountException)
async def handle_user_cant_activate_their_account_exception(
    request: Request, exception: UserCantActivateTheirAccountException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exception)}
    )


@app.exception_handler(PasswordAlreadySetException)
async def handle_password_already_set_exception(
    request: Request, exception: PasswordAlreadySetException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exception)}
    )


@app.exception_handler(PasswordNotSetException)
async def handle_password_not_set_exception(
    request: Request, exception: PasswordNotSetException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exception)}
    )


@app.exception_handler(LegacyProductException)
async def handle_legacy_product_exception(
    request: Request, exception: LegacyProductException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exception)}
    )


@app.exception_handler(ProductIsAlreadyLegacyException)
async def handle_product_is_already_legacy_exception(
    request: Request, exception: ProductIsAlreadyLegacyException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exception)}
    )


@app.exception_handler(CannotRetrieveIssuedStockException)
async def handle_cannot_retrieve_issued_stock_exception(
    request: Request, exception: CannotRetrieveIssuedStockException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exception)}
    )


@app.exception_handler(MissingProductDataException)
async def missing_product_data_exception(
    request: Request, exception: MissingProductDataException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exception)}
    )


@app.exception_handler(MissingIssueDataException)
async def missing_issue_data_exception(
    request: Request, exception: MissingIssueDataException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exception)}
    )


@app.exception_handler(MissingReceptionDataException)
async def missing_reception_data_exception(
    request: Request, exception: MissingReceptionDataException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exception)}
    )


@app.exception_handler(TooLittleWaitingRoomSpaceException)
async def too_little_waiting_room_space_exception(
    request: Request, exception: TooLittleWaitingRoomSpaceException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exception)}
    )


@app.exception_handler(TooLittleWaitingRoomWeightException)
async def too_little_waiting_room_weight_exception(
    request: Request, exception: TooLittleWaitingRoomWeightException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exception)}
    )


@app.exception_handler(WaitingRoomIsNotEmptyException)
async def waiting_room_is_not_empty_exception(
    request: Request, exception: WaitingRoomIsNotEmptyException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exception)}
    )


@app.exception_handler(CannotMoveIssuedStockException)
async def cannot_move_issued_stock_exception(
    request: Request, exception: CannotMoveIssuedStockException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exception)}
    )


@app.exception_handler(StockAlreadyInWaitingRoomException)
async def stock_already_in_waiting_room_exception(
    request: Request, exception: StockAlreadyInWaitingRoomException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exception)}
    )


@app.exception_handler(NoAvailableSlotsInWaitingRoomException)
async def no_available_slots_in_waiting_room_exception(
    request: Request, exception: NoAvailableSlotsInWaitingRoomException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exception)}
    )


@app.exception_handler(NoAvailableWeightInWaitingRoomException)
async def no_available_weight_in_waiting_room_exception(
    request: Request, exception: NoAvailableWeightInWaitingRoomException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exception)}
    )


@app.exception_handler(NoAvailableWaitingRoomsException)
async def no_available_waiting_rooms_exception(
    request: Request, exception: NoAvailableWaitingRoomsException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exception)}
    )


@app.exception_handler(WarehouseAlreadyExistsException)
async def warehouse_already_exists_exception(
    request: Request, exception: WarehouseAlreadyExistsException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exception)}
    )


@app.exception_handler(TooLittleWaitingRoomAmountException)
async def too_little_waiting_room_amount_exception_exception(
    request: Request, exception: TooLittleWaitingRoomAmountException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exception)}
    )


@app.exception_handler(TooLittleSectionAmountException)
async def too_little_section_amount_exception_exception(
    request: Request, exception: TooLittleSectionAmountException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exception)}
    )


@app.exception_handler(WarehouseIsNotEmptyException)
async def warehouse_is_not_empty_exception(
    request: Request, exception: WarehouseIsNotEmptyException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exception)}
    )


@app.exception_handler(WarehouseDoesNotExistException)
async def warehouse_does_not_exist_exception(
    request: Request, exception: WarehouseDoesNotExistException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exception)}
    )


@app.exception_handler(SectionIsNotEmptyException)
async def section_is_not_empty_exception(
    request: Request, exception: SectionIsNotEmptyException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exception)}
    )


@app.exception_handler(NotEnoughWarehouseResourcesException)
async def not_enough_warehouse_resources_exception(
    request: Request, exception: NotEnoughWarehouseResourcesException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exception)}
    )


@app.exception_handler(TooLittleRacksAmountException)
async def too_little_racks_amount_exception(
    request: Request, exception: TooLittleRacksAmountException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exception)}
    )


@app.exception_handler(TooLittleWeightAmountException)
async def too_little_weight_amount_exception(
    request: Request, exception: TooLittleWeightAmountException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exception)}
    )


@app.exception_handler(TooLittleRackLevelsAmountException)
async def too_little_rack_levels_amount_exception(
    request: Request, exception: TooLittleRackLevelsAmountException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exception)}
    )


@app.exception_handler(RackIsNotEmptyException)
async def rack_is_not_empty_exception(
    request: Request, exception: RackIsNotEmptyException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exception)}
    )


@app.exception_handler(NotEnoughSectionResourcesException)
async def not_enough_section_resources_exception(
    request: Request, exception: NotEnoughSectionResourcesException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exception)}
    )


@app.exception_handler(WeightLimitExceededException)
async def weight_limit_exceeded_exception(
    request: Request, exception: WeightLimitExceededException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exception)}
    )
