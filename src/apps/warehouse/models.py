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

from src.apps.sections.models import Section
from src.core.utils.orm import (
    default_available_sections,
    default_available_waiting_rooms,
)
from src.core.utils.time import get_current_time
from src.core.utils.utils import generate_uuid
from src.database.db_connection import Base


class Warehouse(Base):
    __tablename__ = "warehouse"
    id = Column(
        String,
        primary_key=True,
        unique=True,
        nullable=False,
        index=True,
        default=generate_uuid,
    )
    warehouse_name = Column(String(length=400), nullable=False)
    max_sections = Column(Integer, nullable=False)
    available_sections = Column(
        Integer, nullable=False, default=default_available_sections
    )
    occupied_sections = Column(Integer, nullable=False, default=0)
    max_waiting_rooms = Column(Integer, nullable=False)
    available_waiting_rooms = Column(
        Integer, nullable=False, default=default_available_waiting_rooms
    )
    occupied_waiting_rooms = Column(Integer, nullable=False, default=0)
    sections = relationship("Section", back_populates="warehouse", lazy="selectin")
    waiting_rooms = relationship(
        "WaitingRoom", back_populates="warehouse", lazy="selectin"
    )
