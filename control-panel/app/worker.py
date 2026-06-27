from celery import Celery
from celery.schedules import crontab
from .config import get_settings

settings = get_settings()

celery_app = Celery(
    "saas_worker",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)

celery_app.conf.beat_schedule = {
    "backup-all-tenants": {
        "task": "app.tasks.backup_all_tenants",
        "schedule": crontab(hour=2, minute=0),
    },
    "sync-monitoring": {
        "task": "app.tasks.sync_monitoring",
        "schedule": crontab(minute="*/5"),
    },
    "prune-old-backups": {
        "task": "app.tasks.prune_old_backups",
        "schedule": crontab(hour=3, minute=30),
    },
}
