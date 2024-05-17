from fastapi import BackgroundTasks, Depends, status
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.users.models import User
from src.apps.users.schemas import UserPasswordSchema
from src.apps.users.services.activation_services import activate_account_service
from src.dependencies.get_db import get_db
from src.dependencies.user import authenticate_user

email_router = APIRouter(prefix="/email", tags=["emails"])


@email_router.post(
    "/confirm-account-activation/{token}",
    status_code=status.HTTP_200_OK,
)
async def confirm_account_activation(
    token: str,
    password_schema: UserPasswordSchema,
    session: AsyncSession = Depends(get_db),
    auth_jwt: AuthJWT = Depends(),
) -> JSONResponse:
    await activate_account_service(session, token, password_schema)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Your password was set and account was activated successfully!"
        },
    )
