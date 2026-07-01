from datetime import datetime
from pydantic import BaseModel, field_validator
from ..models.tenant import TenantStatus


class TenantCreate(BaseModel):
    slug: str
    display_name: str
    plan_code: str
    billing_period: str = "monthly"
    sector_code: str = "custom"
    company_email: str | None = None
    company_phone: str | None = None

    @field_validator("slug")
    @classmethod
    def slug_must_be_valid(cls, v: str) -> str:
        from ..services.naming import validate_slug
        validate_slug(v)
        return v


class TenantOut(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    slug: str
    subdomain: str
    display_name: str
    odoo_version: str
    sector_code: str
    company_email: str | None
    company_phone: str | None
    status: TenantStatus
    cpu_usage: float
    memory_usage: float
    created_at: datetime


class TenantAction(BaseModel):
    action: str
    target_version: str | None = None
