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

from src.core.utils.orm import (
    default_available_rack_level_slots,
    default_available_rack_level_weight,
)
from src.core.utils.time import get_current_time
from src.core.utils.utils import generate_uuid
from src.database.db_connection import Base


class RackLevelSlot(Base):
    __tablename__ = "rack_level_slot"
    id = Column(
        String,
        primary_key=True,
        unique=True,
        nullable=False,
        index=True,
        default=generate_uuid,
    )
    rack_level_slot_number = Column(Integer, nullable=False)
    description = Column(String(length=200), nullable=True)
    is_active = Column(Boolean, nullable=False, server_default="true")

    rack_level_id = Column(
        String,
        ForeignKey("rack_level.id", onupdate="SET NULL", ondelete="CASCADE"),
        nullable=False,
    )
    rack_level = relationship(
        "RackLevel", back_populates="rack_level_slots", lazy="joined"
    )
    stock = relationship(
        "Stock", uselist=False, back_populates="rack_level_slot", lazy="selectin"
    )
    created_at = Column(DateTime, default=dt.datetime.now, nullable=True)
