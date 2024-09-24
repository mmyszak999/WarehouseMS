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
    default_available_section_racks,
    default_available_section_weight,
)
from src.core.utils.time import get_current_time
from src.core.utils.utils import generate_uuid
from src.database.db_connection import Base


class Section(Base):
    __tablename__ = "section"
    id = Column(
        String,
        primary_key=True,
        unique=True,
        nullable=False,
        index=True,
        default=generate_uuid,
    )
    section_name = Column(String(length=400), nullable=False)

    max_weight = Column(DECIMAL, nullable=False)

    available_weight = Column(
        DECIMAL, nullable=False, default=default_available_section_weight
    )
    occupied_weight = Column(DECIMAL, nullable=False, default=0)

    reserved_weight = Column(DECIMAL, nullable=False, default=0)
    weight_to_reserve = Column(
        DECIMAL, nullable=False, default=default_available_section_weight
    )

    max_racks = Column(Integer, nullable=False)

    available_racks = Column(
        DECIMAL, nullable=False, default=default_available_section_racks
    )
    occupied_racks = Column(Integer, nullable=False, default=0)

    warehouse_id = Column(
        String,
        ForeignKey("warehouse.id", onupdate="SET NULL"),
        nullable=False,
    )
    warehouse = relationship("Warehouse", back_populates="sections", lazy="noload")
    racks = relationship("Rack", back_populates="section", lazy="selectin")
    created_at = Column(DateTime, default=dt.datetime.now, nullable=True)
