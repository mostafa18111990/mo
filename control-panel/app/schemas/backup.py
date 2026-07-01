from datetime import datetime
from pydantic import BaseModel
from ..models.backup import BackupKind, BackupStatus


class BackupOut(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    tenant_id: int
    kind: BackupKind
    status: BackupStatus
    object_key: str | None
    size_bytes: int | None
    created_at: datetime
