from datetime import datetime
from pydantic import BaseModel
from ..models.subscription import BillingPeriod, SubscriptionStatus


class SubscriptionOut(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    tenant_id: int
    plan_id: int
    billing_period: BillingPeriod
    status: SubscriptionStatus
    current_period_end: datetime | None
    created_at: datetime


class CheckoutRequest(BaseModel):
    tenant_id: int
    plan_code: str
    billing_period: BillingPeriod = BillingPeriod.monthly
