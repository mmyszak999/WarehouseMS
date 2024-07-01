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


class RackLevel(Base):
    __tablename__ = "rack_level"
    id = Column(
        String,
        primary_key=True,
        unique=True,
        nullable=False,
        index=True,
        default=generate_uuid,
    )
    rack_level_number = Column(Integer, nullable=False)
    description = Column(String(length=400), nullable=True)

    max_weight = Column(DECIMAL, nullable=False)
    available_weight = Column(
        DECIMAL, nullable=False, default=default_available_rack_level_weight
    )
    occupied_weight = Column(DECIMAL, nullable=False, default=0)

    max_slots = Column(Integer, nullable=False)
    available_slots = Column(
        Integer, nullable=False, default=default_available_rack_level_slots
    )
    occupied_slots = Column(Integer, nullable=False, default=0)

    rack_id = Column(
        String,
        ForeignKey("rack.id", onupdate="SET NULL"),
        nullable=False,
    )
    rack = relationship("Rack", back_populates="rack_levels", lazy="joined")
