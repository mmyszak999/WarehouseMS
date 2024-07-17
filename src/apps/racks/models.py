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
    default_available_rack_levels,
    default_available_rack_weight,
)
from src.core.utils.time import get_current_time
from src.core.utils.utils import generate_uuid
from src.database.db_connection import Base


class Rack(Base):
    __tablename__ = "rack"
    id = Column(
        String,
        primary_key=True,
        unique=True,
        nullable=False,
        index=True,
        default=generate_uuid,
    )
    rack_name = Column(String(length=400), nullable=False)

    max_weight = Column(DECIMAL, nullable=False)
    available_weight = Column(
        DECIMAL, nullable=False, default=default_available_rack_weight
    )
    occupied_weight = Column(DECIMAL, nullable=False, default=0)

    max_levels = Column(Integer, nullable=False)
    available_levels = Column(
        Integer, nullable=False, default=default_available_rack_levels
    )
    occupied_levels = Column(Integer, nullable=False, default=0)

    reserved_weight = Column(DECIMAL, nullable=False, default=0)
    weight_to_reserve = Column(
        DECIMAL, nullable=False, default=default_available_rack_weight
    )

    section_id = Column(
        String,
        ForeignKey("section.id", onupdate="SET NULL"),
        nullable=False,
    )
    section = relationship("Section", back_populates="racks", lazy="selectin")
    rack_levels = relationship("RackLevel", back_populates="rack", lazy="selectin")
    created_at = Column(DateTime, default=dt.datetime.now, nullable=True)
