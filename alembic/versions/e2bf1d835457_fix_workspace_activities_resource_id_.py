"""Fix workspace_activities resource_id type to string

Revision ID: e2bf1d835457
Revises: d1bd1387
Create Date: 2025-06-23 16:23:02.237923

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e2bf1d835457"
down_revision: Union[str, None] = "d1bd1387"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Alterar o tipo do campo resource_id de Integer para String(255)
    op.alter_column(
        "workspace_activities",
        "resource_id",
        type_=sa.String(255),
        existing_type=sa.Integer(),
        schema="synapscale_db",
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Reverter o tipo do campo resource_id de String(255) para Integer
    op.alter_column(
        "workspace_activities",
        "resource_id",
        type_=sa.Integer(),
        existing_type=sa.String(255),
        schema="synapscale_db",
    )
