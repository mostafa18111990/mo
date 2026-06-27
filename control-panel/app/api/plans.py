from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.user import User, UserRole
from ..models.plan import Plan
from ..schemas.plan import PlanOut, PlanCreate
from ..core.security import get_current_user, require_role

router = APIRouter()


@router.get("", response_model=list[PlanOut])
def list_plans(db: Annotated[Session, Depends(get_db)]):
    return db.query(Plan).filter(Plan.is_active == True).all()  # noqa: E712


@router.post("", response_model=PlanOut, status_code=201,
             dependencies=[Depends(require_role(UserRole.super_admin))])
def create_plan(body: PlanCreate, db: Annotated[Session, Depends(get_db)]):
    if db.query(Plan).filter(Plan.code == body.code).first():
        raise HTTPException(status_code=409, detail="Plan code already exists")
    plan = Plan(**body.model_dump())
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


@router.delete("/{plan_id}", status_code=204,
               dependencies=[Depends(require_role(UserRole.super_admin))])
def delete_plan(plan_id: int, db: Annotated[Session, Depends(get_db)]):
    plan = db.get(Plan, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    plan.is_active = False
    db.commit()
