from datetime import datetime

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


class UserStock(Base):
    __tablename__ = "user_stock"
    id = Column(
        String, primary_key=True, unique=True, nullable=False, default=generate_uuid
    )
    user_id = Column(String, ForeignKey("user.id", ondelete="SET NULL"), nullable=False)
    user = relationship(
        "User",
        back_populates="stock_user_history",
        foreign_keys=[user_id],
        lazy="joined",
    )

    stock_id = Column(
        String, ForeignKey("stock.id", ondelete="SET NULL"), nullable=False
    )
    stock = relationship(
        "Stock",
        back_populates="stock_user_history",
        foreign_keys=[stock_id],
        lazy="joined",
    )

    moved_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    from_waiting_room_id = Column(
        String, ForeignKey("waiting_room.id", ondelete="SET NULL"), nullable=True
    )
    from_waiting_room = relationship(
        "WaitingRoom", foreign_keys=[from_waiting_room_id], lazy="joined"
    )

    to_waiting_room_id = Column(
        String, ForeignKey("waiting_room.id", ondelete="SET NULL"), nullable=True
    )
    to_waiting_room = relationship(
        "WaitingRoom", foreign_keys=[to_waiting_room_id], lazy="joined"
    )

    issue_id = Column(
        String, ForeignKey("issue.id", ondelete="SET NULL"), nullable=True
    )
    issue = relationship("Issue", foreign_keys=[issue_id], lazy="joined")


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
    waiting_room_id = Column(
        String,
        ForeignKey("waiting_room.id", ondelete="SET NULL", onupdate="cascade"),
        nullable=True,
    )
    waiting_room = relationship("WaitingRoom", back_populates="stocks", lazy="joined")
    product_count = Column(Integer, nullable=False)
    is_issued = Column(Boolean, nullable=False, server_default="false")
    updated_at = Column(DateTime, nullable=True)
    stock_user_history = relationship(
        "UserStock",
        back_populates="stock",
        foreign_keys="UserStock.stock_id",
        lazy="joined",
    )
