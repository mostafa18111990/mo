from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.user import User
from ..schemas.subscription import CheckoutRequest
from ..core.security import get_current_user
from ..services.stripe_service import StripeService

router = APIRouter()


@router.post("/checkout")
def create_checkout(
    body: CheckoutRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    svc = StripeService(db)
    url = svc.create_checkout_session(current_user, body.tenant_id, body.plan_code, body.billing_period)
    return {"checkout_url": url}


@router.post("/portal")
def billing_portal(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    svc = StripeService(db)
    url = svc.create_portal_session(current_user)
    return {"portal_url": url}
