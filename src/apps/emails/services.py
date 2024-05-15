from fastapi import BackgroundTasks
from fastapi_mail import ConnectionConfig
from pydantic import BaseSettings, EmailStr
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.emails.schemas import EmailSchema
from src.apps.jwt.schemas import ConfirmationTokenSchema
from src.apps.users.models import User
from src.core.exceptions import DoesNotExist, IsOccupied, ServiceException
from src.core.utils.orm import (
   if_exists
)
from src.core.utils.email import (
    confirm_token,
    generate_confirm_token,
    send_email,
)
from src.settings.email_settings import EmailSettings



def email_config(settings: BaseSettings = EmailSettings):
    return ConnectionConfig(**settings().dict())


async def retrieve_email_from_token(session: AsyncSession, token: str) -> str:
    emails = await confirm_token(token)
    current_email = emails[0]
    return current_email


async def send_activation_email(
    email: EmailStr, session: AsyncSession, background_tasks: BackgroundTasks
) -> None:
    email_schema = EmailSchema(
        email_subject="Activate your account",
        receivers=(email,),
        template_name="account_activation_email.html",
    )
    token = await generate_confirm_token([email])
    body_schema = ConfirmationTokenSchema(token=token)
    await send_email(email_schema, body_schema, background_tasks, settings=email_config())