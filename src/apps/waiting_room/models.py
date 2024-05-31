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


class WaitingRoom(Base):
    __tablename__ = "waiting_room"
    id = Column(
        String, primary_key=True, unique=True, nullable=False, default=generate_uuid
    )
    max_stocks = Column(Integer, nullable=False)
    max_weight = Column(DECIMAL, nullable=False)
    stocks = relationship("Stocks", back_populates="waiting_room", lazy="joined")
    occupied_slots = Column(Integer, nullable=False, default=0)
    