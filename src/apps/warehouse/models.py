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


class Warehouse(Base):
    __tablename__ = "warehouse"
    id = Column(
        String, primary_key=True, unique=True, nullable=False, index=True, default=generate_uuid
    )
    warehouse_name = Column(String(length=400), nullable=False)
    max_sections = Column(Integer, nullable=False)
    sections = relationship("Section", back_populates="warehouse", lazy="joined")
