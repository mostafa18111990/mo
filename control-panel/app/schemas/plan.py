from pydantic import BaseModel


class PlanOut(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    code: str
    name: str
    monthly_price_cents: int
    yearly_price_cents: int
    max_users: int
    max_storage_gb: int
    cpu_limit: str
    memory_limit: str
    is_active: bool


class PlanCreate(BaseModel):
    code: str
    name: str
    monthly_price_cents: int
    yearly_price_cents: int
    stripe_monthly_price_id: str | None = None
    stripe_yearly_price_id: str | None = None
    max_users: int = 5
    max_storage_gb: int = 10
    cpu_limit: str = "0.5"
    memory_limit: str = "512m"
