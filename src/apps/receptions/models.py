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


class Reception(Base):
    __tablename__ = "reception"
    id = Column(
        String, primary_key=True, unique=True, nullable=False, default=generate_uuid
    )
    reception_date = Column(
        DateTime, nullable=False, default=get_current_time
    )
    user_id = Column(
        String,
        ForeignKey("user.id", ondelete="SET NULL", onupdate="cascade"),
        nullable=True,
    )
    user = relationship("User", back_populates="receptions", lazy="joined")
    stocks = relationship("Stock", back_populates="reception", lazy="joined")