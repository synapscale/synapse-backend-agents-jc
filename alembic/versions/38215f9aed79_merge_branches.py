"""merge branches

Revision ID: 38215f9aed79
Revises: 3111777acac7, e28e1c7936e3
Create Date: 2025-07-01 09:21:30.302704

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "38215f9aed79"
down_revision: Union[str, None] = ("3111777acac7", "e28e1c7936e3")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
