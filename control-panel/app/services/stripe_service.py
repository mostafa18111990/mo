import logging
import stripe
from sqlalchemy.orm import Session
from ..config import get_settings
from ..models.user import User
from ..models.plan import Plan
from ..models.tenant import Tenant, TenantStatus
from ..models.subscription import Subscription, SubscriptionStatus, BillingPeriod
from .. import tasks

logger = logging.getLogger(__name__)
settings = get_settings()

stripe.api_key = settings.stripe_secret_key


class StripeService:
    def __init__(self, db: Session):
        self.db = db

    def _get_or_create_customer(self, user: User) -> str:
        if user.stripe_customer_id:
            return user.stripe_customer_id
        customer = stripe.Customer.create(email=user.email, metadata={"user_id": str(user.id)})
        user.stripe_customer_id = customer.id
        self.db.commit()
        return customer.id

    def create_checkout_session(
        self, user: User, tenant_id: int, plan_code: str, billing_period: BillingPeriod
    ) -> str:
        plan = self.db.query(Plan).filter(Plan.code == plan_code).first()
        if not plan:
            raise ValueError(f"Plan {plan_code} not found")
        price_id = (
            plan.stripe_monthly_price_id
            if billing_period == BillingPeriod.monthly
            else plan.stripe_yearly_price_id
        )
        customer_id = self._get_or_create_customer(user)
        session = stripe.checkout.Session.create(
            customer=customer_id,
            mode="subscription",
            line_items=[{"price": price_id, "quantity": 1}],
            success_url=f"https://{settings.admin_domain}/tenants/{tenant_id}?checkout=success",
            cancel_url=f"https://{settings.admin_domain}/tenants/{tenant_id}?checkout=cancel",
            metadata={"tenant_id": str(tenant_id), "plan_code": plan_code, "billing_period": billing_period},
        )
        return session.url

    def create_portal_session(self, user: User) -> str:
        customer_id = self._get_or_create_customer(user)
        session = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=f"https://{settings.admin_domain}/tenants",
        )
        return session.url

    def verify_webhook(self, payload: bytes, sig_header: str) -> stripe.Event:
        return stripe.Webhook.construct_event(payload, sig_header, settings.stripe_webhook_secret)

    def handle_event(self, event: stripe.Event):
        handlers = {
            "checkout.session.completed": self._on_checkout_completed,
            "customer.subscription.updated": self._on_subscription_updated,
            "customer.subscription.deleted": self._on_subscription_deleted,
            "invoice.payment_failed": self._on_payment_failed,
            "invoice.payment_succeeded": self._on_payment_succeeded,
        }
        handler = handlers.get(event["type"])
        if handler:
            handler(event["data"]["object"])

    def _on_checkout_completed(self, obj):
        tenant_id = int(obj["metadata"]["tenant_id"])
        plan_code = obj["metadata"]["plan_code"]
        billing_period = obj["metadata"]["billing_period"]
        plan = self.db.query(Plan).filter(Plan.code == plan_code).first()
        sub = self.db.query(Subscription).filter(Subscription.tenant_id == tenant_id).first()
        if not sub:
            sub = Subscription(
                user_id=int(obj.get("metadata", {}).get("user_id", 0)),
                tenant_id=tenant_id,
                plan_id=plan.id if plan else 0,
                billing_period=billing_period,
            )
            self.db.add(sub)
        sub.stripe_subscription_id = obj.get("subscription")
        sub.stripe_customer_id = obj.get("customer")
        sub.status = SubscriptionStatus.active
        self.db.commit()

    def _on_subscription_updated(self, obj):
        sub = self.db.query(Subscription).filter(
            Subscription.stripe_subscription_id == obj["id"]
        ).first()
        if sub:
            sub.status = SubscriptionStatus(obj["status"])
            self.db.commit()

    def _on_subscription_deleted(self, obj):
        sub = self.db.query(Subscription).filter(
            Subscription.stripe_subscription_id == obj["id"]
        ).first()
        if sub:
            sub.status = SubscriptionStatus.canceled
            self.db.commit()
            tasks.suspend_tenant.delay(sub.tenant_id)

    def _on_payment_failed(self, obj):
        customer_id = obj.get("customer")
        sub = self.db.query(Subscription).filter(
            Subscription.stripe_customer_id == customer_id
        ).first()
        if sub:
            sub.status = SubscriptionStatus.past_due
            self.db.commit()
            tasks.suspend_tenant.delay(sub.tenant_id)

    def _on_payment_succeeded(self, obj):
        customer_id = obj.get("customer")
        sub = self.db.query(Subscription).filter(
            Subscription.stripe_customer_id == customer_id
        ).first()
        if sub and sub.status != SubscriptionStatus.active:
            sub.status = SubscriptionStatus.active
            self.db.commit()
            tasks.resume_tenant.delay(sub.tenant_id)
