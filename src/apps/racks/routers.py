from typing import Union

from fastapi import Depends, Request, Response, status
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.racks.schemas import (
    RackBaseOutputSchema,
    RackInputSchema,
    RackOutputSchema,
    RackUpdateSchema,
)
from src.apps.racks.services import (
    create_rack,
    delete_single_rack,
    get_all_racks,
    get_single_rack,
    update_single_rack,
)
from src.apps.users.models import User
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.permissions import check_if_staff
from src.dependencies.get_db import get_db
from src.dependencies.user import authenticate_user

rack_router = APIRouter(prefix="/racks", tags=["rack"])


@rack_router.post(
    "/",
    response_model=RackBaseOutputSchema,
    status_code=status.HTTP_201_CREATED,
)
async def post_rack(
    rack: RackInputSchema,
    session: AsyncSession = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> RackBaseOutputSchema:
    await check_if_staff(request_user)
    return await create_rack(session, rack)


@rack_router.get(
    "/",
    response_model=Union[
        PagedResponseSchema[RackBaseOutputSchema],
        PagedResponseSchema[RackOutputSchema],
    ],
    status_code=status.HTTP_200_OK,
)
async def get_racks(
    session: AsyncSession = Depends(get_db),
    page_params: PageParams = Depends(),
    request_user: User = Depends(authenticate_user),
) -> Union[
    PagedResponseSchema[RackBaseOutputSchema],
    PagedResponseSchema[RackOutputSchema],
]:
    return await get_all_racks(session, page_params)


@rack_router.get(
    "/{rack_id}",
    response_model=Union[RackOutputSchema, RackBaseOutputSchema],
    status_code=status.HTTP_200_OK,
)
async def get_rack(
    rack_id: str,
    session: AsyncSession = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> Union[RackBaseOutputSchema, RackOutputSchema]:
    if request_user.is_staff or request_user.can_move_stocks:
        return await get_single_rack(session, rack_id)
    return await get_single_rack(session, rack_id, output_schema=RackBaseOutputSchema)


@rack_router.patch(
    "/{rack_id}",
    response_model=RackOutputSchema,
    status_code=status.HTTP_200_OK,
)
async def update_rack(
    rack_id: str,
    rack_input: RackUpdateSchema,
    session: AsyncSession = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> RackOutputSchema:
    await check_if_staff(request_user)
    return await update_single_rack(session, rack_input, rack_id)


@rack_router.delete(
    "/{rack_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_rack(
    rack_id: str,
    session: AsyncSession = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> Response:
    await check_if_staff(request_user)
    await delete_single_rack(session, rack_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
