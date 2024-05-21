from fastapi import APIRouter, FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi_jwt_auth.exceptions import AuthJWTException

from src.apps.emails.routers import email_router
from src.apps.users.routers import user_router
from src.apps.products.routers.category_routers import category_router
from src.core.exceptions import (
    AccountAlreadyActivatedException,
    AccountAlreadyDeactivatedException,
    AccountNotActivatedException,
    AlreadyExists,
    AuthenticationException,
    AuthorizationException,
    DoesNotExist,
    IsOccupied,
    PasswordAlreadySetException,
    PasswordNotSetException,
    ServiceException,
    UserCantActivateTheirAccountException,
    UserCantDeactivateTheirAccountException,
)

app = FastAPI(
    title="WarehouseMS", description="Warehouse Management System", version="1.0"
)


root_router = APIRouter(prefix="/api")

root_router.include_router(user_router)
root_router.include_router(email_router)
root_router.include_router(category_router)

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
