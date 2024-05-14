from typing import Any

from fastapi import BackgroundTasks
from fastapi_jwt_auth import AuthJWT
from pydantic import BaseModel
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.users.models import User
from src.apps.users.schemas import (
    UserOutputSchema,
    UserLoginInputSchema,
    UserInputSchema,
    UserInfoOutputSchema,
    UserUpdateSchema
)
from src.apps.jwt.schemas import AccessTokenOutputSchema
from src.core.utils.crypt import passwd_context, hash_user_password
from src.core.pagination.models import PageParams
from src.core.pagination.schemas import PagedResponseSchema
from src.core.pagination.services import paginate
from src.core.exceptions import (
    AuthenticationException,
    AlreadyExists,
    DoesNotExist,
    ServiceException,
    AccountAlreadyDeactivatedException,
    AccountNotActivatedException,
    AccountAlreadyActivatedException
)
from src.core.utils.orm import if_exists
from src.apps.emails.services import send_activation_email


async def create_user_base(session: AsyncSession, user_input: UserInputSchema) -> User:
    user_data = user_input.dict()
    
    email_check = await session.scalar(
        select(User).filter(User.email == user_data["email"]).limit(1)
    )
    if email_check:
        raise AlreadyExists(User.__name__, "email", user_data["email"])
    
    new_user = User(**user_data)
    return new_user


async def create_single_user(
    session: AsyncSession, user_input: UserInputSchema, background_tasks: BackgroundTasks
) -> UserOutputSchema:
    new_user = await create_user_base(session, user_input)

    session.add(new_user)
    await session.commit()

    await send_activation_email(new_user.email, session, background_tasks)

    return UserOutputSchema.from_orm(new_user)


async def authenticate(user_login_schema: UserLoginInputSchema, session: AsyncSession) -> User:
    login_data = user_login_schema.dict()
    user = await session.scalar(
        select(User).filter(User.email == login_data["email"]).limit(1)
    )
    if not (user or passwd_context.verify(login_data["password"], user.password)):
        raise AuthenticationException("Invalid Credentials")
    if not user.is_active:
        raise AccountNotActivatedException("email", login_data["email"])
    return user


async def get_access_token_schema(
    user_login_schema: UserLoginInputSchema, session: AsyncSession, auth_jwt: AuthJWT
) -> AccessTokenOutputSchema:
    user = await authenticate(user_login_schema, session=session)
    email = user.email
    access_token = auth_jwt.create_access_token(subject=email, algorithm="HS256")

    return AccessTokenOutputSchema(access_token=access_token)


async def get_single_user(
    session: AsyncSession, user_id: str, output_schema: BaseModel = UserOutputSchema
) -> BaseModel:
    if not (user_object := await if_exists(User, "id", user_id, session)):
        raise DoesNotExist(User.__name__, "id", user_id)

    return output_schema.from_orm(user_object)


async def get_all_users(
    session: AsyncSession, page_params: PageParams) -> PagedResponseSchema[UserOutputSchema]:
    query = select(User)
    return await paginate(
        query=query,
        response_schema=UserOutputSchema,
        table=User,
        page_params=page_params,
        session=session,
    )

async def update_single_user(
    session: AsyncSession, user_input: UserUpdateSchema, user_id: str
) -> UserOutputSchema:
    if not (await if_exists(User, "id", user_id, session)):
        raise DoesNotExist(User.__name__, "id", user_id)

    user_data = user_input.dict(exclude_unset=True, exclude_none=True)
    
    if user_data:
        statement = update(User).filter(User.id == user_id).values(**user_data)

        await session.execute(statement)
        await session.commit()

    return await get_single_user(session, user_id=user_id)


async def delete_single_user(session: AsyncSession, user_id: str):
    if not (user_object := (await if_exists(User, "id", user_id, session))):
        raise DoesNotExist(User.__name__, "id", user_id)
    
    statement = delete(User).filter(User.id == user_id)
    result = await session.execute(statement)
    await session.commit()

    return result
