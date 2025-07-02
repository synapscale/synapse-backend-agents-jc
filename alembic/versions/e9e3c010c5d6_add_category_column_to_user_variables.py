"""add category column to user_variables

Revision ID: e9e3c010c5d6
Revises: 294dba6f3a38
Create Date: 2025-06-16 15:57:26.840561

"""

revision = "e9e3c010c5d6"
down_revision = "294dba6f3a38"
branch_labels = None
depends_on = None
from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column(
        "user_variables",
        sa.Column("category", sa.String(length=100), nullable=True),
        schema="synapscale_db",
    )


def downgrade():
    op.drop_column("user_variables", "category", schema="synapscale_db")
