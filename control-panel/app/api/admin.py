from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.user import User, UserRole
from ..models.tenant import Tenant, TenantStatus
from ..schemas.user import UserOut, UserUpdate
from ..schemas.tenant import TenantOut
from ..core.security import require_role
from .. import tasks

router = APIRouter()

_admin_dep = Depends(require_role(UserRole.super_admin, UserRole.support))


@router.get("/stats", dependencies=[_admin_dep])
def platform_stats(db: Annotated[Session, Depends(get_db)]):
    total_tenants = db.query(Tenant).count()
    active_tenants = db.query(Tenant).filter(Tenant.status == TenantStatus.active).count()
    suspended = db.query(Tenant).filter(Tenant.status == TenantStatus.suspended).count()
    total_users = db.query(User).count()
    return {
        "total_tenants": total_tenants,
        "active_tenants": active_tenants,
        "suspended_tenants": suspended,
        "total_users": total_users,
    }


@router.get("/tenants", response_model=list[TenantOut], dependencies=[_admin_dep])
def all_tenants(db: Annotated[Session, Depends(get_db)]):
    return db.query(Tenant).all()


@router.get("/users", response_model=list[UserOut], dependencies=[_admin_dep])
def all_users(db: Annotated[Session, Depends(get_db)]):
    return db.query(User).all()


class PackagesBody(BaseModel):
    packages: list[str] = ["qifparse"]
    tenant_id: int | None = None


@router.post("/fix-packages", dependencies=[Depends(require_role(UserRole.super_admin))])
def fix_packages(body: PackagesBody, db: Annotated[Session, Depends(get_db)]):
    if body.tenant_id:
        tenant = db.get(Tenant, body.tenant_id)
        if not tenant:
            raise HTTPException(status_code=404, detail="Tenant not found")
        tasks.install_pip_packages.delay(tenant.id, body.packages)
        return {"status": "queued", "tenant": tenant.slug, "packages": body.packages}
    else:
        tasks.fix_all_tenants_packages.delay(body.packages)
        return {"status": "queued_all", "packages": body.packages}


@router.patch("/users/{user_id}", response_model=UserOut,
              dependencies=[Depends(require_role(UserRole.super_admin))])
def update_user(
    user_id: int,
    body: UserUpdate,
    db: Annotated[Session, Depends(get_db)],
):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if body.is_active is not None:
        user.is_active = body.is_active
    if body.role is not None:
        user.role = body.role
    db.commit()
    db.refresh(user)
    return user
