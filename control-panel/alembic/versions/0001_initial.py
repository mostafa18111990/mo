"""Initial schema

Revision ID: 0001
Revises:
Create Date: 2024-01-01 00:00:00
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("role", sa.Enum("customer", "support", "super_admin", name="userrole"), nullable=False, server_default="customer"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("stripe_customer_id", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_users_email", "users", ["email"])

    op.create_table(
        "plans",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(50), nullable=False, unique=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("monthly_price_cents", sa.Integer(), nullable=False),
        sa.Column("yearly_price_cents", sa.Integer(), nullable=False),
        sa.Column("stripe_monthly_price_id", sa.String(255), nullable=True),
        sa.Column("stripe_yearly_price_id", sa.String(255), nullable=True),
        sa.Column("max_users", sa.Integer(), nullable=False, server_default="5"),
        sa.Column("max_storage_gb", sa.Integer(), nullable=False, server_default="10"),
        sa.Column("cpu_limit", sa.String(20), nullable=False, server_default="0.5"),
        sa.Column("memory_limit", sa.String(20), nullable=False, server_default="512m"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
    )

    op.create_table(
        "tenants",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("owner_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("slug", sa.String(63), nullable=False, unique=True),
        sa.Column("subdomain", sa.String(63), nullable=False, unique=True),
        sa.Column("display_name", sa.String(255), nullable=False),
        sa.Column("db_name", sa.String(63), nullable=False, unique=True),
        sa.Column("db_user", sa.String(63), nullable=False, unique=True),
        sa.Column("db_password", sa.String(255), nullable=False),
        sa.Column("odoo_admin_password", sa.String(255), nullable=False),
        sa.Column("container_id", sa.String(255), nullable=True),
        sa.Column("odoo_version", sa.String(20), nullable=False, server_default="17"),
        sa.Column("status", sa.Enum("provisioning", "active", "suspended", "upgrading", "error", "terminated", name="tenantstatus"), nullable=False, server_default="provisioning"),
        sa.Column("cpu_usage", sa.Float(), nullable=False, server_default="0"),
        sa.Column("memory_usage", sa.Float(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_tenants_slug", "tenants", ["slug"])
    op.create_index("ix_tenants_owner_id", "tenants", ["owner_id"])

    op.create_table(
        "subscriptions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id"), nullable=False),
        sa.Column("plan_id", sa.Integer(), sa.ForeignKey("plans.id"), nullable=False),
        sa.Column("stripe_subscription_id", sa.String(255), nullable=True, unique=True),
        sa.Column("stripe_customer_id", sa.String(255), nullable=True),
        sa.Column("billing_period", sa.Enum("monthly", "yearly", name="billingperiod"), nullable=False, server_default="monthly"),
        sa.Column("status", sa.Enum("active", "past_due", "canceled", "trialing", "incomplete", name="subscriptionstatus"), nullable=False, server_default="incomplete"),
        sa.Column("current_period_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "backups",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id"), nullable=False),
        sa.Column("kind", sa.Enum("scheduled", "manual", name="backupkind"), nullable=False, server_default="scheduled"),
        sa.Column("status", sa.Enum("pending", "running", "completed", "failed", name="backupstatus"), nullable=False, server_default="pending"),
        sa.Column("object_key", sa.String(512), nullable=True),
        sa.Column("size_bytes", sa.BigInteger(), nullable=True),
        sa.Column("error_message", sa.String(1024), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_backups_tenant_id", "backups", ["tenant_id"])

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("actor_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("target_type", sa.String(50), nullable=True),
        sa.Column("target_id", sa.Integer(), nullable=True),
        sa.Column("payload", postgresql.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_audit_logs_actor_id", "audit_logs", ["actor_id"])
    op.create_index("ix_audit_logs_action", "audit_logs", ["action"])
    op.create_index("ix_audit_logs_created_at", "audit_logs", ["created_at"])


def downgrade():
    op.drop_table("audit_logs")
    op.drop_table("backups")
    op.drop_table("subscriptions")
    op.drop_table("tenants")
    op.drop_table("plans")
    op.drop_table("users")
    op.execute("DROP TYPE IF EXISTS userrole")
    op.execute("DROP TYPE IF EXISTS tenantstatus")
    op.execute("DROP TYPE IF EXISTS billingperiod")
    op.execute("DROP TYPE IF EXISTS subscriptionstatus")
    op.execute("DROP TYPE IF EXISTS backupkind")
    op.execute("DROP TYPE IF EXISTS backupstatus")
