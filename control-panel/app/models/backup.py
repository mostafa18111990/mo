import enum
from datetime import datetime
from sqlalchemy import String, Integer, BigInteger, ForeignKey, Enum, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..database import Base


class BackupKind(str, enum.Enum):
    scheduled = "scheduled"
    manual = "manual"


class BackupStatus(str, enum.Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"


class Backup(Base):
    __tablename__ = "backups"

    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"), nullable=False, index=True)
    kind: Mapped[BackupKind] = mapped_column(Enum(BackupKind), default=BackupKind.scheduled)
    status: Mapped[BackupStatus] = mapped_column(Enum(BackupStatus), default=BackupStatus.pending)
    object_key: Mapped[str | None] = mapped_column(String(512), nullable=True)
    size_bytes: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    error_message: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    tenant: Mapped["Tenant"] = relationship("Tenant", back_populates="backups")  # noqa: F821
