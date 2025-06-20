"""Merge multiple heads: add_plan_id_manual and 7aa856f973a0

Revision ID: 59a0aa3e97ef
Revises: 7aa856f973a0, add_plan_id_manual
Create Date: 2025-06-20 20:16:26.805326

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '59a0aa3e97ef'
down_revision: Union[str, None] = ('7aa856f973a0', 'add_plan_id_manual')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
