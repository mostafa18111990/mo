from celery import shared_task
from .worker import celery_app
from .database import session_scope
from .models.tenant import Tenant, TenantStatus
from .services.provisioning import ProvisioningService
from .services.backup_service import BackupService
from .services.docker_manager import DockerManager


@celery_app.task(bind=True, max_retries=3, default_retry_delay=30)
def provision_tenant(self, tenant_id: int):
    try:
        with session_scope() as db:
            tenant = db.get(Tenant, tenant_id)
            svc = ProvisioningService(db)
            svc.provision(tenant)
            # إرسال بريد الترحيب بعد اكتمال الإنشاء
            from .services.email_service import send_tenant_ready
            from .models.user import User
            from .config import get_settings
            _s = get_settings()
            owner = db.get(User, tenant.owner_id)
            if owner:
                send_tenant_ready(
                    user_email=owner.email,
                    company_name=tenant.display_name,
                    subdomain=tenant.subdomain,
                    admin_email=tenant.company_email or owner.email,
                    admin_password=tenant.odoo_admin_password,
                    domain=_s.domain,
                )
    except Exception as exc:
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=10)
def suspend_tenant(self, tenant_id: int):
    try:
        with session_scope() as db:
            tenant = db.get(Tenant, tenant_id)
            svc = ProvisioningService(db)
            svc.suspend(tenant)
            from .services.email_service import send_tenant_suspended
            from .models.user import User
            from .config import get_settings
            _s = get_settings()
            owner = db.get(User, tenant.owner_id)
            if owner:
                send_tenant_suspended(owner.email, tenant.display_name, _s.domain)
    except Exception as exc:
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=10)
def resume_tenant(self, tenant_id: int):
    try:
        with session_scope() as db:
            tenant = db.get(Tenant, tenant_id)
            svc = ProvisioningService(db)
            svc.resume(tenant)
    except Exception as exc:
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=10)
def restart_tenant(self, tenant_id: int):
    try:
        with session_scope() as db:
            tenant = db.get(Tenant, tenant_id)
            svc = ProvisioningService(db)
            svc.restart(tenant)
    except Exception as exc:
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=2, default_retry_delay=60)
def upgrade_tenant(self, tenant_id: int, target_version: str):
    try:
        with session_scope() as db:
            tenant = db.get(Tenant, tenant_id)
            svc = ProvisioningService(db)
            svc.upgrade(tenant, target_version)
    except Exception as exc:
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=2, default_retry_delay=30)
def delete_tenant(self, tenant_id: int):
    try:
        with session_scope() as db:
            tenant = db.get(Tenant, tenant_id)
            if not tenant:
                return

            owner_id = tenant.owner_id

            # 1. إلغاء اشتراك Stripe إن وجد
            from .models.subscription import Subscription, SubscriptionStatus
            import stripe
            from .config import get_settings
            _settings = get_settings()
            stripe.api_key = _settings.stripe_secret_key
            sub = db.query(Subscription).filter(
                Subscription.tenant_id == tenant_id
            ).first()
            if sub and sub.stripe_subscription_id:
                try:
                    stripe.Subscription.cancel(sub.stripe_subscription_id)
                except Exception:
                    pass
                sub.status = SubscriptionStatus.canceled
                db.commit()

            # 2. حذف السجلات المرتبطة (backups, subscription)
            from .models.backup import Backup
            db.query(Backup).filter(Backup.tenant_id == tenant_id).delete()
            if sub:
                db.delete(sub)
            db.commit()

            # 3. تدمير الكونتينر والقاعدة والـ Traefik config
            svc = ProvisioningService(db)
            svc.terminate(tenant)

            # 4. حذف سجل الـ Tenant
            db.delete(tenant)
            db.commit()

            # 5. إلغاء تفعيل حساب العميل إذا لم يعد لديه أي tenant آخر
            from .models.user import User
            remaining = db.query(Tenant).filter(
                Tenant.owner_id == owner_id
            ).count()
            if remaining == 0:
                user = db.get(User, owner_id)
                if user:
                    user.is_active = False
                    db.commit()

    except Exception as exc:
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def backup_tenant(self, tenant_id: int):
    try:
        with session_scope() as db:
            tenant = db.get(Tenant, tenant_id)
            svc = BackupService(db)
            svc.create_and_upload(tenant)
    except Exception as exc:
        raise self.retry(exc=exc)


@shared_task
def backup_all_tenants():
    with session_scope() as db:
        tenants = db.query(Tenant).filter(
            Tenant.status == TenantStatus.active
        ).all()
        for tenant in tenants:
            backup_tenant.delay(tenant.id)


@shared_task
def sync_monitoring():
    from .services.docker_manager import DockerManager
    dm = DockerManager()
    with session_scope() as db:
        tenants = db.query(Tenant).filter(
            Tenant.status == TenantStatus.active
        ).all()
        for tenant in tenants:
            if tenant.container_id:
                stats = dm.container_stats(tenant.container_id)
                if stats:
                    tenant.cpu_usage = stats.get("cpu_percent", 0.0)
                    tenant.memory_usage = stats.get("memory_mb", 0.0)


@shared_task
def prune_old_backups():
    from .services.backup_service import BackupService
    with session_scope() as db:
        svc = BackupService(db)
        svc.prune_old_backups(keep_days=30)


@celery_app.task(bind=True, max_retries=2, default_retry_delay=10)
def install_pip_packages(self, tenant_id: int, packages: list[str]):
    try:
        with session_scope() as db:
            tenant = db.get(Tenant, tenant_id)
            if not tenant or not tenant.container_id:
                return {"error": "Tenant or container not found"}
            dm = DockerManager()
            exit_code, output = dm.exec_in_container(
                tenant.container_id,
                ["pip", "install"] + packages
            )
            if exit_code != 0:
                raise RuntimeError(f"pip install failed: {output}")
            dm.restart(tenant.container_id)
            return {"status": "ok", "output": output}
    except Exception as exc:
        raise self.retry(exc=exc)


@celery_app.task
def fix_all_tenants_packages(packages: list[str] | None = None):
    pkgs = packages or ["qifparse"]
    with session_scope() as db:
        tenants = db.query(Tenant).filter(
            Tenant.status == TenantStatus.active
        ).all()
        for tenant in tenants:
            if tenant.container_id:
                install_pip_packages.delay(tenant.id, pkgs)
