from typing import Union

from fastapi import Depends, Request, Response, status
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.sections.schemas import (
    SectionInputSchema,
    SectionOutputSchema,
    SectionUpdateSchema,
    SectionBaseOutputSchema
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
    response_model=PagedResponseSchema[SectionBaseOutputSchema],
    status_code=status.HTTP_200_OK,
)
async def get_sections(
    session: AsyncSession = Depends(get_db),
    page_params: PageParams = Depends(),
    request_user: User = Depends(authenticate_user),
) -> PagedResponseSchema[SectionBaseOutputSchema]:
    return await get_all_sections(session, page_params)


@section_router.get(
    "/{section_id}",
    response_model=Union[SectionBaseOutputSchema, SectionOutputSchema],
    status_code=status.HTTP_200_OK,
)
async def get_section(
    section_id: str,
    session: AsyncSession = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> Union[SectionBaseOutputSchema, SectionOutputSchema]:
    if request_user.is_staff or request_user.can_move_stocks:
        return await get_single_section(session, section_id)
    return await get_single_section(session, section_id, output_schema=SectionBaseOutputSchema)


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
