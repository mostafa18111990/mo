import logging
from typing import Annotated
from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..services.stripe_service import StripeService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/stripe")
async def stripe_webhook(request: Request, db: Annotated[Session, Depends(get_db)]):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")
    svc = StripeService(db)
    try:
        event = svc.verify_webhook(payload, sig_header)
    except Exception as exc:
        logger.warning("Stripe webhook verification failed: %s", exc)
        raise HTTPException(status_code=400, detail="Invalid webhook signature")
    svc.handle_event(event)
    return {"received": True}
