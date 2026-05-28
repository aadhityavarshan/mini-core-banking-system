from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.db import Base


class Customer(Base):
    __tablename__ = "customers"

    customer_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    phone: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)

    accounts = relationship("Account", back_populates="customer")
