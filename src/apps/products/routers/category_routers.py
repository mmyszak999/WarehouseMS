from fastapi import Depends, Request, Response, status
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.products.schemas.category_schemas import (
    CategoryInputSchema,
    CategoryOutputSchema,
    CategoryUpdateSchema,
    CategoryBaseSchema
)
from src.apps.products.services.category_services import (
    create_category,
    delete_single_category,
    get_all_categories,
    get_single_category,
    update_single_category,
)
from src.apps.users.models import User
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.permissions import check_if_staff
from src.dependencies.get_db import get_db
from src.dependencies.user import authenticate_user

category_router = APIRouter(prefix="/categories", tags=["category"])


@category_router.post(
    "/",
    response_model=CategoryInputSchema,
    status_code=status.HTTP_201_CREATED,
)
async def post_category(
    category: CategoryInputSchema,
    session: AsyncSession = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> CategoryOutputSchema:
    await check_if_staff(request_user)
    return await create_category(session, category)


@category_router.get(
    "/",
    response_model=PagedResponseSchema[CategoryOutputSchema],
    status_code=status.HTTP_200_OK,
)
async def get_categories(
    request: Request,
    session: AsyncSession = Depends(get_db),
    page_params: PageParams = Depends(),
    request_user: User = Depends(authenticate_user),
) -> PagedResponseSchema[CategoryOutputSchema]:
    return await get_all_categories(
        session, page_params, query_params=request.query_params.multi_items()
    )


@category_router.get(
    "/{category_id}",
    response_model=CategoryOutputSchema,
    status_code=status.HTTP_200_OK,
)
async def get_category(
    category_id: str,
    session: AsyncSession = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> CategoryOutputSchema:
    await check_if_staff(request_user)
    return await get_single_category(session, category_id)


@category_router.patch(
    "/{category_id}",
    response_model=CategoryOutputSchema,
    status_code=status.HTTP_200_OK,
)
async def update_category(
    category_id: str,
    category_input: CategoryUpdateSchema,
    session: AsyncSession = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> CategoryOutputSchema:
    await check_if_staff(request_user)
    return await update_single_category(session, category_input, category_id)


@category_router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_category(
    category_id: str,
    session: AsyncSession = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> Response:
    await check_if_staff(request_user)
    await delete_single_category(session, category_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
