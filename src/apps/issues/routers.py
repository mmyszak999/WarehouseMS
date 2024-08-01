from fastapi import Depends, Request, Response, status
from fastapi.routing import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.issues.models import Issue
from src.apps.issues.schemas import (
    IssueBasicOutputSchema,
    IssueInputSchema,
    IssueOutputSchema,
    IssueUpdateSchema,
)
from src.apps.issues.services import (
    create_issue,
    get_all_issues,
    get_single_issue,
    update_single_issue,
)
from src.apps.users.models import User
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.permissions import check_if_staff_or_has_permission
from src.dependencies.get_db import get_db
from src.dependencies.user import authenticate_user

issue_router = APIRouter(prefix="/issues", tags=["issue"])


@issue_router.post(
    "/",
    response_model=IssueOutputSchema,
    status_code=status.HTTP_201_CREATED,
)
async def post_issue(
    issue_input: IssueInputSchema,
    session: AsyncSession = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> IssueOutputSchema:
    await check_if_staff_or_has_permission(request_user, "can_issue_stocks")
    return await create_issue(session, issue_input, request_user.id)


@issue_router.get(
    "/",
    response_model=PagedResponseSchema[IssueBasicOutputSchema],
    status_code=status.HTTP_200_OK,
)
async def get_issues(
    request: Request,
    session: AsyncSession = Depends(get_db),
    page_params: PageParams = Depends(),
    request_user: User = Depends(authenticate_user),
) -> PagedResponseSchema[IssueBasicOutputSchema]:
    await check_if_staff_or_has_permission(request_user, "can_issue_stocks")
    return await get_all_issues(session, page_params, query_params=request.query_params.multi_items())


@issue_router.get(
    "/{issue_id}",
    response_model=IssueOutputSchema,
    status_code=status.HTTP_200_OK,
)
async def get_issue(
    issue_id: str,
    session: AsyncSession = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> IssueOutputSchema:
    await check_if_staff_or_has_permission(request_user, "can_issue_stocks")
    return await get_single_issue(session, issue_id)


@issue_router.patch(
    "/{issue_id}",
    response_model=IssueOutputSchema,
    status_code=status.HTTP_200_OK,
)
async def update_issue(
    issue_id: str,
    issue_input: IssueUpdateSchema,
    session: AsyncSession = Depends(get_db),
    request_user: User = Depends(authenticate_user),
) -> IssueOutputSchema:
    await check_if_staff_or_has_permission(request_user, "can_issue_stocks")
    return await update_single_issue(session, issue_input, issue_id)
