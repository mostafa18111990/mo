from sqlalchemy import String, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..database import Base


class Plan(Base):
    __tablename__ = "plans"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    monthly_price_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    yearly_price_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    stripe_monthly_price_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    stripe_yearly_price_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    max_users: Mapped[int] = mapped_column(Integer, default=5)
    max_storage_gb: Mapped[int] = mapped_column(Integer, default=10)
    cpu_limit: Mapped[str] = mapped_column(String(20), default="0.5")
    memory_limit: Mapped[str] = mapped_column(String(20), default="512m")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    subscriptions: Mapped[list["Subscription"]] = relationship("Subscription", back_populates="plan")  # noqa: F821
