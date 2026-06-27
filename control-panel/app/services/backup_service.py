import os
import subprocess
import logging
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from ..config import get_settings
from ..models.tenant import Tenant
from ..models.backup import Backup, BackupKind, BackupStatus

logger = logging.getLogger(__name__)
settings = get_settings()


class BackupService:
    def __init__(self, db: Session):
        self.db = db

    def create_and_upload(self, tenant: Tenant, kind: BackupKind = BackupKind.scheduled):
        backup = Backup(tenant_id=tenant.id, kind=kind, status=BackupStatus.running)
        self.db.add(backup)
        self.db.commit()

        try:
            dump_path = self._create_dump(tenant)
            object_key = self._upload(dump_path, tenant.slug)
            size = os.path.getsize(dump_path)
            os.unlink(dump_path)

            backup.object_key = object_key
            backup.size_bytes = size
            backup.status = BackupStatus.completed
        except Exception as exc:
            backup.status = BackupStatus.failed
            backup.error_message = str(exc)
            logger.exception("Backup failed for tenant %s", tenant.slug)
        finally:
            self.db.commit()

    def _create_dump(self, tenant: Tenant) -> str:
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        path = f"/tmp/{tenant.slug}_{ts}.pgdump"
        env = os.environ.copy()
        env["PGPASSWORD"] = tenant.db_password
        result = subprocess.run(
            ["pg_dump", "-Fc",
             "-h", settings.postgres_host,
             "-p", str(settings.postgres_port),
             "-U", tenant.db_user,
             "-d", tenant.db_name,
             "-f", path],
            env=env, capture_output=True, text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(f"pg_dump failed: {result.stderr}")
        return path

    def _upload(self, local_path: str, slug: str) -> str:
        filename = os.path.basename(local_path)
        object_key = f"backups/{slug}/{filename}"
        if settings.s3_bucket:
            import boto3
            s3 = boto3.client(
                "s3",
                region_name=settings.s3_region,
                aws_access_key_id=settings.aws_access_key_id,
                aws_secret_access_key=settings.aws_secret_access_key,
            )
            s3.upload_file(local_path, settings.s3_bucket, object_key)
        else:
            dest = f"/app/data/backups/{slug}"
            os.makedirs(dest, exist_ok=True)
            import shutil
            shutil.copy2(local_path, os.path.join(dest, filename))
            object_key = f"local://{dest}/{filename}"
        return object_key

    def prune_old_backups(self, keep_days: int = 30):
        cutoff = datetime.now(timezone.utc) - timedelta(days=keep_days)
        old = self.db.query(Backup).filter(
            Backup.created_at < cutoff,
            Backup.status == BackupStatus.completed,
        ).all()
        for b in old:
            if b.object_key and not b.object_key.startswith("local://") and settings.s3_bucket:
                try:
                    import boto3
                    s3 = boto3.client("s3", region_name=settings.s3_region)
                    s3.delete_object(Bucket=settings.s3_bucket, Key=b.object_key)
                except Exception:
                    pass
            self.db.delete(b)
        self.db.commit()
