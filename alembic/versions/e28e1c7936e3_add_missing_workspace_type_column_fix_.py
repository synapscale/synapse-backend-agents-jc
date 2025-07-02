"""add_missing_workspace_type_column_fix_schema_sync

Revision ID: e28e1c7936e3
Revises: 67fe75d237c8
Create Date: 2025-07-01 04:39:42.097327

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = "e28e1c7936e3"
down_revision: Union[str, None] = "67fe75d237c8"  # Pular a migração problemática
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Add missing type column to workspaces table."""

    # Criar o enum type se não existir
    workspace_type_enum = sa.Enum(
        "individual", "collaborative", name="workspacetype", schema="synapscale_db"
    )
    workspace_type_enum.create(op.get_bind(), checkfirst=True)

    # Verificar se a coluna já existe antes de adicionar
    connection = op.get_bind()
    inspector = inspect(connection)

    # Get columns for the workspaces table in synapscale_db schema
    columns = inspector.get_columns("workspaces", schema="synapscale_db")
    column_names = [col["name"] for col in columns]

    # Só adicionar a coluna se ela não existir
    if "type" not in column_names:
        op.add_column(
            "workspaces",
            sa.Column(
                "type", workspace_type_enum, nullable=False, server_default="individual"
            ),
            schema="synapscale_db",
        )


def downgrade() -> None:
    """Downgrade schema - Remove type column from workspaces table."""

    # Verificar se a coluna existe antes de remover
    connection = op.get_bind()
    inspector = inspect(connection)

    columns = inspector.get_columns("workspaces", schema="synapscale_db")
    column_names = [col["name"] for col in columns]

    # Só remover a coluna se ela existir
    if "type" in column_names:
        op.drop_column("workspaces", "type", schema="synapscale_db")

    # Remover o enum type
    workspace_type_enum = sa.Enum(
        "individual", "collaborative", name="workspacetype", schema="synapscale_db"
    )
    workspace_type_enum.drop(op.get_bind(), checkfirst=True)
