"""add_created_updated_at_to_workspace_members

Revision ID: 10fc63eb296d
Revises: 2cedfbb519dd
Create Date: 2025-06-21 14:52:19.023771

"""
from typing import Sequence, Union
from datetime import datetime, timezone

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '10fc63eb296d'
down_revision: Union[str, None] = '2cedfbb519dd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Adicionar colunas created_at e updated_at à tabela workspace_members
    op.add_column('workspace_members', 
                  sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, 
                           server_default=sa.text('CURRENT_TIMESTAMP')), schema='synapscale_db')
    op.add_column('workspace_members', 
                  sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, 
                           server_default=sa.text('CURRENT_TIMESTAMP')), schema='synapscale_db')
    
    # Atualizar created_at para usar joined_at quando disponível
    op.execute("""
        UPDATE synapscale_db.workspace_members 
        SET created_at = joined_at 
        WHERE joined_at IS NOT NULL
    """)


def downgrade() -> None:
    """Downgrade schema."""
    # Remover as colunas adicionadas
    op.drop_column('workspace_members', 'updated_at', schema='synapscale_db')
    op.drop_column('workspace_members', 'created_at', schema='synapscale_db')
