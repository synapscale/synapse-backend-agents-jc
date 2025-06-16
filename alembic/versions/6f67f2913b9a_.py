"""empty message

Revision ID: 6f67f2913b9a
Revises: 006_add_type_column_to_nodes, 009addstatuscolnodes, 010addstatuscolnodes, 8b2c3d4e5f6a
Create Date: 2025-06-16 18:14:09.906846

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6f67f2913b9a'
down_revision: Union[str, None] = ('006_add_type_column_to_nodes', '009addstatuscolnodes', '010addstatuscolnodes', '8b2c3d4e5f6a')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
