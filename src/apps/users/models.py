import datetime as dt

from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import DateTime

from src.apps.issues.models import Issue
from src.apps.receptions.models import Reception
from src.core.utils.utils import generate_uuid
from src.database.db_connection import Base


class User(Base):
    __tablename__ = "user"
    id = Column(
        String,
        primary_key=True,
        unique=True,
        nullable=False,
        index=True,
        default=generate_uuid,
    )
    first_name = Column(String(length=50), nullable=False)
    last_name = Column(String(length=75), nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=True)
    birth_date = Column(Date, nullable=False)
    employment_date = Column(Date, nullable=True)
    is_active = Column(Boolean, nullable=False, server_default="false")
    is_superuser = Column(Boolean, nullable=False, server_default="false")
    is_staff = Column(Boolean, nullable=False, server_default="false")
    has_password_set = Column(Boolean, nullable=False, server_default="false")
    can_move_stocks = Column(Boolean, nullable=False, server_default="false")
    can_recept_stocks = Column(Boolean, nullable=False, server_default="false")
    can_issue_stocks = Column(Boolean, nullable=False, server_default="false")
    issues = relationship("Issue", back_populates="user", lazy="joined")
    receptions = relationship("Reception", back_populates="user", lazy="joined")
    stock_user_history = relationship(
        "UserStock",
        back_populates="user",
        foreign_keys="UserStock.user_id",
        lazy="joined",
    )
    created_at = Column(DateTime, default=dt.datetime.now, nullable=True)
