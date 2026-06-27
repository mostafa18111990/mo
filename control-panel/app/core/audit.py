from sqlalchemy.orm import Session
from ..models.audit_log import AuditLog


def audit(
    db: Session,
    action: str,
    actor_id: int | None = None,
    target_type: str | None = None,
    target_id: int | None = None,
    payload: dict | None = None,
):
    db.add(AuditLog(
        actor_id=actor_id,
        action=action,
        target_type=target_type,
        target_id=target_id,
        payload=payload,
    ))
