from fastapi import Depends, Request, Response, status
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.receptions.schemas import ReceptionInputSchema, ReceptionOutputSchema
from src.apps.receptions.services import create_reception
from src.apps.users.models import User
from src.apps.receptions.models import Reception
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.permissions import check_if_staff
from src.dependencies.get_db import get_db
from src.dependencies.user import authenticate_user

reception_router = APIRouter(prefix="/receptions", tags=["reception"])


@reception_router.post(
    "/",
    response_model=ReceptionOutputSchema,
    status_code=status.HTTP_201_CREATED,
)
async def post_reception(
    reception_input: ReceptionInputSchema,
    session: AsyncSession = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> ReceptionOutputSchema:
    await check_if_staff(request_user)
    return await create_reception(session, reception_input, request_user.id)