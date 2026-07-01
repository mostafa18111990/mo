import logging
import psycopg
from ..config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class PostgresAdmin:
    def __init__(self):
        self._dsn = settings.tenant_admin_url

    def _conn(self):
        return psycopg.connect(self._dsn, autocommit=True)

    def create_tenant_db(self, db_name: str, db_user: str, db_password: str):
        with self._conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"CREATE ROLE {db_user} WITH LOGIN PASSWORD %s",
                    (db_password,)
                )
                cur.execute(
                    f'CREATE DATABASE "{db_name}" OWNER {db_user} ENCODING "UTF8"'
                )
                cur.execute(f'GRANT ALL PRIVILEGES ON DATABASE "{db_name}" TO {db_user}')
        logger.info("Created DB %s for user %s", db_name, db_user)

    def drop_tenant_db(self, db_name: str, db_user: str):
        with self._conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = %s",
                    (db_name,)
                )
                cur.execute(f'DROP DATABASE IF EXISTS "{db_name}"')
                cur.execute(f"DROP ROLE IF EXISTS {db_user}")
        logger.info("Dropped DB %s and role %s", db_name, db_user)
