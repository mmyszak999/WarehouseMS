from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.issues.models import Issue
from src.apps.issues.schemas import (
    IssueBasicOutputSchema,
    IssueInputSchema,
    IssueOutputSchema,
    IssueUpdateSchema,
)
from src.apps.products.models import Product
from src.apps.users.models import User
from src.apps.stocks.models import Stock
from src.apps.stocks.services.stock_services import issue_stocks
from src.core.exceptions import (
    AlreadyExists,
    DoesNotExist,
    IsOccupied,
    MissingIssueDataException,
    ServiceException,
)
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.pagination.services import paginate
from src.core.utils.filter import filter_and_sort_instances
from src.core.utils.orm import if_exists


async def base_create_issue(
    session: AsyncSession,
    user_id: str,
    issue_input: IssueInputSchema = None,
    testing: bool = False,
) -> Issue:

    if (
        (issue_input is None)
        or not (issue_input := issue_input.dict(exclude_none=True, exclude_unset=True))
    ) and not testing:
        raise MissingIssueDataException

    if testing:
        new_issue = Issue(user_id=user_id)
        session.add(new_issue)
        await session.commit()
        return new_issue

    stocks_data = issue_input.get("stock_ids")
    if stock_ids := [stock.pop("id") for stock in stocks_data]:
        stocks = await session.scalars(
            select(Stock).where(Stock.id.in_(stock_ids), Stock.is_issued == False)
        )
        stocks = stocks.unique().all()
        if not len(set(stock_ids)) == len(stocks):
            raise ServiceException(
                "Wrong stocks! Check if all requested stock are not issued!"
            )

    new_issue = Issue(user_id=user_id, description=issue_input.get("description"))

    session.add(new_issue)
    await session.flush()

    return stocks, new_issue


async def create_issue(
    session: AsyncSession, issue_input: IssueInputSchema, user_id: str
) -> IssueOutputSchema:
    stocks, new_issue = await base_create_issue(session, user_id, issue_input)
    await issue_stocks(session, stocks, new_issue.id, user_id)

    await session.commit()
    await session.refresh(new_issue)

    return IssueOutputSchema.from_orm(new_issue)


async def get_single_issue(session: AsyncSession, issue_id: int) -> IssueOutputSchema:
    if not (issue_object := await if_exists(Issue, "id", issue_id, session)):
        raise DoesNotExist(Issue.__name__, "id", issue_id)

    return IssueOutputSchema.from_orm(issue_object)


async def get_all_issues(
    session: AsyncSession, page_params: PageParams, query_params: list[tuple] = None
) -> PagedResponseSchema[IssueBasicOutputSchema]:
    query = select(Issue).join(User, Issue.user_id == User.id)

    if query_params:
        query = filter_and_sort_instances(query_params, query, Issue)

    return await paginate(
        query=query,
        response_schema=IssueBasicOutputSchema,
        table=Issue,
        page_params=page_params,
        session=session,
    )


async def update_single_issue(
    session: AsyncSession, issue_input: IssueUpdateSchema, issue_id: int
) -> IssueOutputSchema:
    if not (issue_object := await if_exists(Issue, "id", issue_id, session)):
        raise DoesNotExist(Issue.__name__, "id", issue_id)

    issue_data = issue_input.dict(exclude_unset=True)

    if issue_data:
        statement = update(Issue).filter(Issue.id == issue_id).values(**issue_data)

        await session.execute(statement)
        await session.commit()
        await session.refresh(issue_object)

    return await get_single_issue(session, issue_id=issue_id)
