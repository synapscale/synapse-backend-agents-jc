"""merge conflicting heads

Revision ID: 67fe75d237c8
Revises: e2bf1d835457, rename_tables
Create Date: 2025-06-26 10:23:21.861359

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "67fe75d237c8"
down_revision: Union[str, None] = ("e2bf1d835457", "rename_tables")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
