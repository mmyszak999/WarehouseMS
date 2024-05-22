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

category_product_association_table = Table(
    "category_product_association_table",
    Base.metadata,
    Column(
        "category_id",
        ForeignKey("category.id", ondelete="SET NULL", onupdate="cascade"),
        nullable=True,
    ),
    Column(
        "product_id",
        ForeignKey("product.id", ondelete="cascade", onupdate="cascade"),
        nullable=False,
    ),
)


class Category(Base):
    __tablename__ = "category"
    id = Column(
        String, primary_key=True, unique=True, nullable=False, default=generate_uuid
    )
    name = Column(String(length=75), nullable=False, unique=True)
    products = relationship(
        "Product",
        secondary=category_product_association_table,
        back_populates="categories",
    )


class Product(Base):
    __tablename__ = "product"
    id = Column(
        String, primary_key=True, unique=True, nullable=False, default=generate_uuid
    )
    name = Column(String(length=75), nullable=False, unique=True)
    wholesale_price = Column(DECIMAL, nullable=False)
    amount_in_goods = Column(Integer, nullable=False, default=0)
    description = Column(String(length=300), nullable=True)
    weight = Column(DECIMAL, nullable=False)
    legacy_product = Column(Boolean, nullable=False, server_default="false")
    categories = relationship(
        "Category",
        secondary=category_product_association_table,
        back_populates="products",
        lazy="joined",
    )
