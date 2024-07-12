import datetime as dt

from sqlalchemy import (
    DECIMAL,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import DateTime

from src.core.utils.time import get_current_time
from src.core.utils.utils import generate_uuid
from src.database.db_connection import Base


class Issue(Base):
    __tablename__ = "issue"
    id = Column(
        String,
        primary_key=True,
        unique=True,
        nullable=False,
        index=True,
        default=generate_uuid,
    )
    issue_date = Column(DateTime, nullable=False, default=get_current_time)
    description = Column(String(length=400), nullable=True)
    user_id = Column(
        String,
        ForeignKey("user.id", ondelete="SET NULL", onupdate="cascade"),
        nullable=True,
    )
    user = relationship("User", back_populates="issues", lazy="joined")
    stocks = relationship("Stock", back_populates="issue", lazy="joined")
    stock_user_history = relationship(
        "UserStock",
        back_populates="issue",
        foreign_keys="UserStock.issue_id",
        lazy="joined",
    )
    created_at = Column(DateTime, default=dt.datetime.now, nullable=True)
