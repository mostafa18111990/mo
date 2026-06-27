from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    domain: str = "myodoo.com"
    admin_domain: str = "admin.myodoo.com"

    postgres_host: str = "postgres"
    postgres_port: int = 5432
    postgres_user: str = "saas_admin"
    postgres_password: str
    postgres_db: str = "saas_control"

    redis_url: str = "redis://redis:6379/0"

    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440

    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_publishable_key: str = ""

    s3_bucket: str = ""
    s3_region: str = "us-east-1"
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""

    odoo_image: str = "odoo:17"
    odoo_admin_email: str = "admin@example.com"

    traefik_dynamic_dir: str = "/etc/traefik/dynamic/tenants"

    celery_broker_url: str = "redis://redis:6379/1"
    celery_result_backend: str = "redis://redis:6379/2"

    @property
    def cp_database_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def tenant_admin_url(self) -> str:
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/postgres"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
