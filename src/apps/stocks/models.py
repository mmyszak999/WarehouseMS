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


class Stock(Base):
    __tablename__ = "stock"
    id = Column(
        String, primary_key=True, unique=True, nullable=False, default=generate_uuid
    )
    weight = Column(DECIMAL, nullable=False)
    product_id = Column(
        String,
        ForeignKey("product.id", ondelete="SET NULL", onupdate="cascade"),
        nullable=True,
    )
    product = relationship("Product", back_populates="stocks", lazy="joined")
    reception_id = Column(
        String,
        ForeignKey("reception.id", ondelete="SET NULL", onupdate="cascade"),
        nullable=True,
    )
    reception = relationship("Reception", back_populates="stocks", lazy="joined")
    issue_id = Column(
        String,
        ForeignKey("issue.id", ondelete="SET NULL", onupdate="cascade"),
        nullable=True,
    )
    issue = relationship("Issue", back_populates="stocks", lazy="joined")
    product_count = Column(Integer, nullable=False)
    is_issued = Column(Boolean, nullable=False, server_default="false")
    updated_at = Column(DateTime, nullable=True)
