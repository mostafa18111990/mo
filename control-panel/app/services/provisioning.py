import logging
from sqlalchemy.orm import Session
from ..config import get_settings
from ..models.tenant import Tenant, TenantStatus
from .docker_manager import DockerManager, ContainerSpec
from .postgres_admin import PostgresAdmin
from .traefik_manager import write_tenant_config, remove_tenant_config

logger = logging.getLogger(__name__)
settings = get_settings()


class ProvisioningService:
    def __init__(self, db: Session):
        self.db = db
        self.dm = DockerManager()
        self.pg = PostgresAdmin()

    def provision(self, tenant: Tenant):
        try:
            tenant.status = TenantStatus.provisioning
            self.db.commit()

            self.pg.create_tenant_db(tenant.db_name, tenant.db_user, tenant.db_password)

            spec = ContainerSpec(
                name=f"odoo-{tenant.slug}",
                image=settings.odoo_image,
                env={
                    "TENANT_DB_HOST": settings.postgres_host,
                    "TENANT_DB_PORT": str(settings.postgres_port),
                    "TENANT_DB_NAME": tenant.db_name,
                    "TENANT_DB_USER": tenant.db_user,
                    "TENANT_DB_PASSWORD": tenant.db_password,
                    "TENANT_ADMIN_PASSWORD": tenant.odoo_admin_password,
                    "TENANT_COMPANY_NAME": tenant.display_name,
                    "INSTALL_ACCOUNTING_KIT": "1",
                },
                labels={
                    "traefik.enable": "false",
                    "saas.tenant_id": str(tenant.id),
                    "saas.slug": tenant.slug,
                },
                mem_limit="1g",
                cpu_quota=100000,
                volumes={
                    f"odoo-data-{tenant.slug}": {"bind": "/var/lib/odoo", "mode": "rw"},
                },
            )
            container_id = self.dm.create(spec)
            write_tenant_config(tenant.slug, tenant.subdomain)

            tenant.container_id = container_id
            tenant.status = TenantStatus.active
            self.db.commit()
            logger.info("Provisioned tenant %s", tenant.slug)
        except Exception as exc:
            tenant.status = TenantStatus.error
            self.db.commit()
            raise

    def terminate(self, tenant: Tenant):
        if tenant.container_id:
            self.dm.remove(tenant.container_id)
        remove_tenant_config(tenant.slug)
        self.pg.drop_tenant_db(tenant.db_name, tenant.db_user)
        tenant.status = TenantStatus.terminated
        self.db.commit()

    def suspend(self, tenant: Tenant):
        if tenant.container_id:
            self.dm.stop(tenant.container_id)
        tenant.status = TenantStatus.suspended
        self.db.commit()

    def resume(self, tenant: Tenant):
        if tenant.container_id:
            self.dm.start(tenant.container_id)
        tenant.status = TenantStatus.active
        self.db.commit()

    def restart(self, tenant: Tenant):
        if tenant.container_id:
            self.dm.restart(tenant.container_id)

    def upgrade(self, tenant: Tenant, target_version: str):
        tenant.status = TenantStatus.upgrading
        self.db.commit()
        try:
            if tenant.container_id:
                self.dm.remove(tenant.container_id)
            new_image = settings.odoo_image.rsplit(":", 1)[0] + f":{target_version}"
            spec = ContainerSpec(
                name=f"odoo-{tenant.slug}",
                image=new_image,
                env={
                    "TENANT_DB_HOST": settings.postgres_host,
                    "TENANT_DB_PORT": str(settings.postgres_port),
                    "TENANT_DB_NAME": tenant.db_name,
                    "TENANT_DB_USER": tenant.db_user,
                    "TENANT_DB_PASSWORD": tenant.db_password,
                    "TENANT_ADMIN_PASSWORD": tenant.odoo_admin_password,
                    "TENANT_COMPANY_NAME": tenant.display_name,
                },
                labels={"saas.tenant_id": str(tenant.id), "saas.slug": tenant.slug},
                mem_limit="1g",
                cpu_quota=100000,
                volumes={
                    f"odoo-data-{tenant.slug}": {"bind": "/var/lib/odoo", "mode": "rw"},
                },
            )
            container_id = self.dm.create(spec)
            tenant.container_id = container_id
            tenant.odoo_version = target_version
            tenant.status = TenantStatus.active
            self.db.commit()
        except Exception:
            tenant.status = TenantStatus.error
            self.db.commit()
            raise
