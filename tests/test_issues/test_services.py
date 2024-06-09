import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.issues.schemas import IssueOutputSchema
from src.apps.issues.services import (
    base_create_issue,
    create_issue,
    get_all_issues,
    get_single_issue,
    update_single_issue,
)
from src.apps.stocks.schemas.stock_schemas import StockIssueInputSchema, StockOutputSchema
from src.apps.stocks.services.stock_services import issue_stocks
from src.apps.users.schemas import UserOutputSchema
from src.core.exceptions import (
    AlreadyExists,
    DoesNotExist,
    IsOccupied,
    MissingIssueDataException,
    ServiceException,
)
from src.core.factory.issue_factory import (
    IssueInputSchemaFactory,
    IssueUpdateSchemaFactory,
)
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.utils.utils import generate_uuid
from tests.test_stocks.conftest import db_stocks
from tests.test_users.conftest import (
    auth_headers,
    db_staff_user,
    db_user,
    staff_auth_headers,
)


@pytest.mark.asyncio
async def test_if_issue_was_created_correctly(
    async_session: AsyncSession,
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_issues: PagedResponseSchema[IssueOutputSchema],
    db_staff_user: UserOutputSchema,
):
    issue_input = IssueInputSchemaFactory().generate(
        stock_ids=[
            StockIssueInputSchema(id=db_stocks.results[0].id),
            StockIssueInputSchema(id=db_stocks.results[1].id),
        ],
        description="descr",
    )
    issue = await base_create_issue(
        async_session, db_staff_user.id, issue_input, testing=True
    )
    assert issue.user_id == db_staff_user.id


@pytest.mark.asyncio
async def test_raise_exception_when_issue_data_is_missing(
    async_session: AsyncSession,
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_issues: PagedResponseSchema[IssueOutputSchema],
    db_staff_user: UserOutputSchema,
):
    with pytest.raises(MissingIssueDataException):
        await base_create_issue(async_session, db_staff_user.id)


@pytest.mark.asyncio
async def test_if_only_one_issue_was_returned(
    async_session: AsyncSession,
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_issues: PagedResponseSchema[IssueOutputSchema],
    db_staff_user: UserOutputSchema,
):
    issue = await get_single_issue(async_session, db_issues.results[0].id)

    assert issue.id == db_issues.results[0].id


@pytest.mark.asyncio
async def test_raise_exception_while_getting_nonexistent_issue(
    async_session: AsyncSession,
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_issues: PagedResponseSchema[IssueOutputSchema],
    db_staff_user: UserOutputSchema,
):
    with pytest.raises(DoesNotExist):
        await get_single_issue(async_session, generate_uuid())


@pytest.mark.asyncio
async def test_if_multiple_issues_were_returned(
    async_session: AsyncSession,
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_issues: PagedResponseSchema[IssueOutputSchema],
    db_staff_user: UserOutputSchema,
):
    issues = await get_all_issues(async_session, PageParams(page=1, size=5))
    assert issues.total == db_issues.total


@pytest.mark.asyncio
async def test_raise_exception_while_updating_nonexistent_issue(
    async_session: AsyncSession,
    db_stocks: PagedResponseSchema[StockOutputSchema],
    db_issues: PagedResponseSchema[IssueOutputSchema],
    db_staff_user: UserOutputSchema,
):
    update_data = IssueUpdateSchemaFactory().generate()
    with pytest.raises(DoesNotExist):
        await update_single_issue(async_session, update_data, generate_uuid())
