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
    DoesNotExist,
    ServiceException,
    AccountAlreadyDeactivatedException,
    AccountNotActivatedException 
)
from src.core.utils.orm import if_exists


async def create_user_base(session: AsyncSession, user_input: UserInputSchema) -> tuple[Any]:
    user_data = user_input.dict()
    new_user = User(**user_data)

    return new_user


async def create_single_user(
    session: AsyncSession, user_input: UserInputSchema, background_tasks: BackgroundTasks
) -> UserOutputSchema:
    new_user = await create_user_base(session, user_input)
    new_user.is_active = True #temporary

    session.add(new_user)
    await session.commit()

    #send_activation_email(new_user.email, session, background_tasks)

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
    session: AsyncSession, user_input: UserUpdateSchema, user_id: int
) -> UserOutputSchema:
    if not (await if_exists(User, "id", user_id, session)):
        raise DoesNotExist(User.__name__, "id", user_id)

    user_data = user.dict(exclude_unset=True, exclude_none=True)
    
    if user_data:
        statement = update(User).filter(User.id == user_id).values(**user_data)

        await session.execute(statement)
        await session.commit()

    return await get_single_user(session, user_id=user_id)


async def deactivate_single_user(session: AsyncSession, user_id: int) -> None:
    if not (user_object := (await if_exists(User, "id", user_id, session))):
        raise DoesNotExist(User.__name__, "id", user_id)
    
    if not user_object.is_active:
        raise AccountAlreadyDeactivatedException("email", user_object.email)
    
    user_object.is_active = True
    session.add(user_object)
    
    await session.commit()


async def delete_single_user(session: AsyncSession, user_id: int):
    if not (user_object := (await if_exists(User, "id", user_id, session))):
        raise DoesNotExist(User.__name__, "id", user_id)
    
    statement = delete(User).filter(User.id == user_id)
    result = await session.execute(statement)
    await session.commit()

    return result
