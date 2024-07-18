from typing import Union

from fastapi import Depends, Request, Response, status
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.sections.schemas import (
    SectionBaseOutputSchema,
    SectionInputSchema,
    SectionOutputSchema,
    SectionUpdateSchema,
)
from src.apps.racks.schemas import (
    RackBaseOutputSchema,
    RackOutputSchema,
)
from src.apps.racks.services import (
    get_all_racks,
    get_single_rack,
)
from src.apps.sections.services import (
    create_section,
    delete_single_section,
    get_all_sections,
    get_single_section,
    update_single_section,
)
from src.apps.users.models import User
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.permissions import check_if_staff
from src.dependencies.get_db import get_db
from src.dependencies.user import authenticate_user

section_router = APIRouter(prefix="/sections", tags=["section"])


@section_router.post(
    "/",
    response_model=SectionInputSchema,
    status_code=status.HTTP_201_CREATED,
)
async def post_section(
    section: SectionInputSchema,
    session: AsyncSession = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> SectionOutputSchema:
    await check_if_staff(request_user)
    return await create_section(session, section)


@section_router.get(
    "/",
    response_model=Union[
        PagedResponseSchema[SectionBaseOutputSchema],
        PagedResponseSchema[SectionOutputSchema],
    ],
    status_code=status.HTTP_200_OK,
)
async def get_sections(
    request: Request,
    session: AsyncSession = Depends(get_db),
    page_params: PageParams = Depends(),
    request_user: User = Depends(authenticate_user),
) -> Union[
    PagedResponseSchema[SectionOutputSchema],
    PagedResponseSchema[SectionBaseOutputSchema],
]:
    return await get_all_sections(session, page_params, query_params=request.query_params.multi_items())


@section_router.get(
    "/{section_id}",
    response_model=Union[SectionOutputSchema, SectionBaseOutputSchema],
    status_code=status.HTTP_200_OK,
)
async def get_section(
    section_id: str,
    session: AsyncSession = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> Union[SectionOutputSchema, SectionBaseOutputSchema]:
    if request_user.is_staff or request_user.can_move_stocks:
        return await get_single_section(session, section_id)
    return await get_single_section(
        session, section_id, output_schema=SectionBaseOutputSchema
    )

@section_router.get(
    "/{section_id}/racks",
    response_model=Union[
        PagedResponseSchema[RackBaseOutputSchema],
        PagedResponseSchema[RackOutputSchema],
    ],
    status_code=status.HTTP_200_OK,
)
async def get_section_racks(
    section_id: str,
    session: AsyncSession = Depends(get_db),
    page_params: PageParams = Depends(),
    request_user: User = Depends(authenticate_user),
) -> Union[
    PagedResponseSchema[RackBaseOutputSchema],
    PagedResponseSchema[RackOutputSchema],
]:
    return await get_all_racks(session, page_params, section_id=section_id)


@section_router.get(
    "/{section_id}/racks/{rack_id}",
    response_model=Union[RackOutputSchema, RackBaseOutputSchema],
    status_code=status.HTTP_200_OK,
)
async def get_section_rack(
    section_id: str,
    rack_id: str,
    session: AsyncSession = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> Union[RackBaseOutputSchema, RackOutputSchema]:
    if request_user.is_staff or request_user.can_move_stocks:
        return await get_single_rack(session, rack_id, section_id=section_id)
    return await get_single_rack(
        session, rack_id, output_schema=RackBaseOutputSchema, section_id=section_id
    )


@section_router.patch(
    "/{section_id}",
    response_model=SectionOutputSchema,
    status_code=status.HTTP_200_OK,
)
async def update_section(
    section_id: str,
    section_input: SectionUpdateSchema,
    session: AsyncSession = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> SectionOutputSchema:
    await check_if_staff(request_user)
    return await update_single_section(session, section_input, section_id)


@section_router.delete(
    "/{section_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_section(
    section_id: str,
    session: AsyncSession = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> Response:
    await check_if_staff(request_user)
    await delete_single_section(session, section_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
