from typing import Union

from fastapi import Depends, Request, Response, status
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.products.schemas.product_schemas import (
    ProductBasicOutputSchema,
    ProductInputSchema,
    ProductOutputSchema,
    ProductUpdateSchema,
    RemovedProductOutputSchema,
)
from src.apps.products.services.product_services import (
    create_product,
    get_all_available_products,
    get_all_products,
    get_available_single_product,
    get_single_product,
    make_single_product_legacy,
    update_single_product,
)
from src.apps.users.models import User
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.permissions import check_if_staff
from src.dependencies.get_db import get_db
from src.dependencies.user import authenticate_user

product_router = APIRouter(prefix="/products", tags=["product"])


@product_router.post(
    "/",
    response_model=ProductOutputSchema,
    status_code=status.HTTP_201_CREATED,
)
async def post_product(
    product_input: ProductInputSchema,
    session: AsyncSession = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> ProductOutputSchema:
    await check_if_staff(request_user)
    return await create_product(session, product_input)


@product_router.get(
    "/",
    response_model=PagedResponseSchema[ProductBasicOutputSchema],
    status_code=status.HTTP_200_OK,
)
async def get_available_products(
    request: Request,
    session: AsyncSession = Depends(get_db),
    request_user: User = Depends(authenticate_user),
    page_params: PageParams = Depends(),
) -> PagedResponseSchema[ProductBasicOutputSchema]:
    return await get_all_available_products(session, page_params, request.query_params.multi_items())


@product_router.get(
    "/all",
    response_model=PagedResponseSchema[ProductOutputSchema],
    status_code=status.HTTP_200_OK,
)
async def get_products(
    request: Request,
    session: AsyncSession = Depends(get_db),
    request_user: User = Depends(authenticate_user),
    page_params: PageParams = Depends(),
) -> PagedResponseSchema[ProductOutputSchema]:
    await check_if_staff(request_user)
    return await get_all_products(session, page_params, request.query_params.multi_items())


@product_router.get(
    "/all/{product_id}",
    response_model=ProductOutputSchema,
    status_code=status.HTTP_200_OK,
)
async def get_product_as_staff(
    product_id: str,
    session: AsyncSession = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> ProductOutputSchema:
    await check_if_staff(request_user)
    return await get_single_product(session, product_id)


@product_router.get(
    "/{product_id}",
    response_model=Union[ProductBasicOutputSchema, RemovedProductOutputSchema],
    status_code=status.HTTP_200_OK,
)
async def get_product(
    product_id: str,
    session: AsyncSession = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> Union[ProductBasicOutputSchema, RemovedProductOutputSchema]:
    return await get_available_single_product(session, product_id)


@product_router.patch(
    "/{product_id}",
    response_model=ProductOutputSchema,
    status_code=status.HTTP_200_OK,
)
async def update_product(
    product_id: str,
    product_input: ProductUpdateSchema,
    session: AsyncSession = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> ProductOutputSchema:
    await check_if_staff(request_user)
    return await update_single_product(session, product_input, product_id)


@product_router.patch(
    "/{product_id}/legacy",
    status_code=status.HTTP_200_OK,
)
async def make_product_legacy(
    product_id: str,
    session: AsyncSession = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> Response:
    await check_if_staff(request_user)
    result = await make_single_product_legacy(session, product_id)
    return JSONResponse(result)
