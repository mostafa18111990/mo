from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.user import User, UserRole
from ..models.tenant import Tenant, TenantStatus
from ..schemas.tenant import TenantCreate, TenantOut, TenantAction
from ..core.security import get_current_user
from ..core.audit import audit
from ..services.naming import build_slug, build_subdomain, random_password, db_identifier
from .. import tasks

router = APIRouter()


def _own_or_admin(tenant: Tenant, user: User):
    if user.role == UserRole.super_admin:
        return
    if tenant.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Not your tenant")


@router.get("", response_model=list[TenantOut])
def list_tenants(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.role == UserRole.super_admin:
        return db.query(Tenant).all()
    return db.query(Tenant).filter(Tenant.owner_id == current_user.id).all()


@router.post("", response_model=TenantOut, status_code=201)
def create_tenant(
    body: TenantCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    slug = build_slug(body.slug)
    if db.query(Tenant).filter(Tenant.slug == slug).first():
        raise HTTPException(status_code=409, detail="Slug already taken")

    tenant = Tenant(
        owner_id=current_user.id,
        slug=slug,
        subdomain=build_subdomain(slug),
        display_name=body.display_name,
        db_name=db_identifier(slug),
        db_user=db_identifier(slug, prefix="u_"),
        db_password=random_password(),
        odoo_admin_password=random_password(),
        sector_code=body.sector_code,
        company_email=body.company_email or current_user.email,
        company_phone=body.company_phone,
    )
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    audit(db, "tenant.create", actor_id=current_user.id, target_type="tenant", target_id=tenant.id)
    db.commit()

    tasks.provision_tenant.delay(tenant.id)
    return tenant


@router.get("/{tenant_id}", response_model=TenantOut)
def get_tenant(
    tenant_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    tenant = db.get(Tenant, tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    _own_or_admin(tenant, current_user)
    return tenant


@router.post("/{tenant_id}/action", response_model=dict)
def tenant_action(
    tenant_id: int,
    body: TenantAction,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    tenant = db.get(Tenant, tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    _own_or_admin(tenant, current_user)

    action_map = {
        "suspend": tasks.suspend_tenant,
        "resume": tasks.resume_tenant,
        "restart": tasks.restart_tenant,
        "backup": tasks.backup_tenant,
        "delete": tasks.delete_tenant,
    }

    if body.action == "upgrade":
        if not body.target_version:
            raise HTTPException(status_code=400, detail="target_version required for upgrade")
        tasks.upgrade_tenant.delay(tenant_id, body.target_version)
    elif body.action in action_map:
        action_map[body.action].delay(tenant_id)
    else:
        raise HTTPException(status_code=400, detail=f"Unknown action: {body.action}")

    audit(db, f"tenant.{body.action}", actor_id=current_user.id, target_type="tenant", target_id=tenant_id)
    db.commit()
    return {"status": "queued", "action": body.action}
