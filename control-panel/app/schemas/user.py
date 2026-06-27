from datetime import datetime
from pydantic import BaseModel, EmailStr
from ..models.user import UserRole


class UserOut(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    email: EmailStr
    role: UserRole
    is_active: bool
    created_at: datetime


class UserUpdate(BaseModel):
    is_active: bool | None = None
    role: UserRole | None = None
