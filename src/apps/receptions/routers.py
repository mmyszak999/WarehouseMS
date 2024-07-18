from fastapi import Depends, Request, Response, status
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.receptions.models import Reception
from src.apps.receptions.schemas import (
    ReceptionBasicOutputSchema,
    ReceptionInputSchema,
    ReceptionOutputSchema,
    ReceptionUpdateSchema,
)
from src.apps.receptions.services import (
    create_reception,
    get_all_receptions,
    get_single_reception,
    update_single_reception,
)
from src.apps.users.models import User
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.permissions import check_if_staff_or_has_permission
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
    await check_if_staff_or_has_permission(request_user, "can_recept_stocks")
    return await create_reception(session, reception_input, request_user.id)


@reception_router.get(
    "/",
    response_model=PagedResponseSchema[ReceptionBasicOutputSchema],
    status_code=status.HTTP_200_OK,
)
async def get_receptions(
    request: Request,
    session: AsyncSession = Depends(get_db),
    page_params: PageParams = Depends(),
    request_user: User = Depends(authenticate_user),
) -> PagedResponseSchema[ReceptionBasicOutputSchema]:
    await check_if_staff_or_has_permission(request_user, "can_recept_stocks")
    return await get_all_receptions(session, page_params, query_params=request.query_params.multi_items())


@reception_router.get(
    "/{reception_id}",
    response_model=ReceptionOutputSchema,
    status_code=status.HTTP_200_OK,
)
async def get_reception(
    reception_id: str,
    session: AsyncSession = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> ReceptionOutputSchema:
    await check_if_staff_or_has_permission(request_user, "can_recept_stocks")
    return await get_single_reception(session, reception_id)


@reception_router.patch(
    "/{reception_id}",
    response_model=ReceptionOutputSchema,
    status_code=status.HTTP_200_OK,
)
async def update_reception(
    reception_id: str,
    reception_input: ReceptionUpdateSchema,
    session: AsyncSession = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> ReceptionOutputSchema:
    await check_if_staff_or_has_permission(request_user, "can_recept_stocks")
    return await update_single_reception(session, reception_input, reception_id)
