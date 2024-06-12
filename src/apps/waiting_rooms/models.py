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

from src.core.utils.orm import default_available_slots, default_available_stock_weight
from src.core.utils.time import get_current_time
from src.core.utils.utils import generate_uuid
from src.database.db_connection import Base


class WaitingRoom(Base):
    __tablename__ = "waiting_room"
    id = Column(
        String,
        primary_key=True,
        unique=True,
        nullable=False,
        index=True,
        default=generate_uuid,
    )
    max_stocks = Column(Integer, nullable=False)
    max_weight = Column(DECIMAL, nullable=False)
    occupied_slots = Column(Integer, nullable=False, default=0)
    available_slots = Column(Integer, nullable=False, default=default_available_slots)
    current_stock_weight = Column(DECIMAL, nullable=False, default=0)
    available_stock_weight = Column(
        DECIMAL, nullable=False, default=default_available_stock_weight
    )
    stocks = relationship("Stock", back_populates="waiting_room", lazy="joined")
