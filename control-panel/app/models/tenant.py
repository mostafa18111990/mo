import enum
from datetime import datetime
from sqlalchemy import String, Integer, Float, ForeignKey, Enum, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..database import Base


class TenantStatus(str, enum.Enum):
    provisioning = "provisioning"
    active = "active"
    suspended = "suspended"
    upgrading = "upgrading"
    error = "error"
    terminated = "terminated"


class Tenant(Base):
    __tablename__ = "tenants"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    slug: Mapped[str] = mapped_column(String(63), unique=True, nullable=False, index=True)
    subdomain: Mapped[str] = mapped_column(String(63), unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    db_name: Mapped[str] = mapped_column(String(63), unique=True, nullable=False)
    db_user: Mapped[str] = mapped_column(String(63), unique=True, nullable=False)
    db_password: Mapped[str] = mapped_column(String(255), nullable=False)
    odoo_admin_password: Mapped[str] = mapped_column(String(255), nullable=False)
    container_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    odoo_version: Mapped[str] = mapped_column(String(20), default="17")
    status: Mapped[TenantStatus] = mapped_column(Enum(TenantStatus), default=TenantStatus.provisioning)
    cpu_usage: Mapped[float] = mapped_column(Float, default=0.0)
    memory_usage: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    owner: Mapped["User"] = relationship("User", back_populates="tenants")  # noqa: F821
    subscription: Mapped["Subscription | None"] = relationship("Subscription", back_populates="tenant", uselist=False)  # noqa: F821
    backups: Mapped[list["Backup"]] = relationship("Backup", back_populates="tenant")  # noqa: F821
