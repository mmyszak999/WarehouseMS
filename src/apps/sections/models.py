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
from src.core.utils.orm import default_available_section_weight, default_available_section_racks


class Section(Base):
    __tablename__ = "section"
    id = Column(
        String, primary_key=True, unique=True, nullable=False, index=True, default=generate_uuid
    )
    section_name = Column(String(length=400), nullable=False)
    max_weight = Column(DECIMAL, nullable=False)
    available_weight = Column(DECIMAL, nullable=False, default=default_available_section_weight)
    max_racks = Column(Integer, nullable=False)
    available_racks = Column(DECIMAL, nullable=False, default=default_available_section_racks)
    warehouse_id = Column(
        String,
        ForeignKey("warehouse.id", onupdate="cascade"),
        nullable=False,
    )
    warehouse = relationship("Warehouse", back_populates="sections", lazy="joined")
