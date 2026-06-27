"""Seed default plans

Revision ID: 0002
Revises: 0001
Create Date: 2024-01-01 00:01:00
"""
from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None

plans_table = sa.table(
    "plans",
    sa.column("code", sa.String),
    sa.column("name", sa.String),
    sa.column("monthly_price_cents", sa.Integer),
    sa.column("yearly_price_cents", sa.Integer),
    sa.column("max_users", sa.Integer),
    sa.column("max_storage_gb", sa.Integer),
    sa.column("cpu_limit", sa.String),
    sa.column("memory_limit", sa.String),
)


def upgrade():
    op.bulk_insert(plans_table, [
        {
            "code": "starter",
            "name": "Starter",
            "monthly_price_cents": 4900,
            "yearly_price_cents": 49900,
            "max_users": 5,
            "max_storage_gb": 10,
            "cpu_limit": "0.5",
            "memory_limit": "512m",
        },
        {
            "code": "business",
            "name": "Business",
            "monthly_price_cents": 14900,
            "yearly_price_cents": 149900,
            "max_users": 25,
            "max_storage_gb": 50,
            "cpu_limit": "1.0",
            "memory_limit": "1g",
        },
        {
            "code": "enterprise",
            "name": "Enterprise",
            "monthly_price_cents": 39900,
            "yearly_price_cents": 399900,
            "max_users": 100,
            "max_storage_gb": 200,
            "cpu_limit": "2.0",
            "memory_limit": "2g",
        },
    ])


def downgrade():
    op.execute("DELETE FROM plans WHERE code IN ('starter', 'business', 'enterprise')")
