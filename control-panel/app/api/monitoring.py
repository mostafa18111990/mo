from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.user import User, UserRole
from ..models.tenant import Tenant
from ..core.security import get_current_user
from ..services.docker_manager import DockerManager

router = APIRouter()


def _own_or_admin(tenant: Tenant, user: User):
    if user.role != UserRole.super_admin and tenant.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Not your tenant")


@router.get("/{tenant_id}/metrics")
def get_metrics(
    tenant_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    tenant = db.get(Tenant, tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    _own_or_admin(tenant, current_user)
    if not tenant.container_id:
        return {"cpu_percent": 0, "memory_mb": 0}
    dm = DockerManager()
    return dm.container_stats(tenant.container_id) or {"cpu_percent": 0, "memory_mb": 0}


@router.get("/{tenant_id}/logs")
def get_logs(
    tenant_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    tail: int = Query(default=200, le=500),
):
    tenant = db.get(Tenant, tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    _own_or_admin(tenant, current_user)
    if not tenant.container_id:
        return {"logs": ""}
    dm = DockerManager()
    return {"logs": dm.container_logs(tenant.container_id, tail=tail)}
