from datetime import datetime
from sqlalchemy import String, Integer, ForeignKey, JSON, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from ..database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    actor_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    target_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    target_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
