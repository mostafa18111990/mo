"""Add sector and company contact fields to tenants

Revision ID: 0003
Revises: 0002
Create Date: 2024-01-01 00:02:00
"""
from alembic import op
import sqlalchemy as sa

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("tenants", sa.Column("sector_code", sa.String(50), nullable=False, server_default="custom"))
    op.add_column("tenants", sa.Column("company_email", sa.String(255), nullable=True))
    op.add_column("tenants", sa.Column("company_phone", sa.String(50), nullable=True))


def downgrade():
    op.drop_column("tenants", "company_phone")
    op.drop_column("tenants", "company_email")
    op.drop_column("tenants", "sector_code")
