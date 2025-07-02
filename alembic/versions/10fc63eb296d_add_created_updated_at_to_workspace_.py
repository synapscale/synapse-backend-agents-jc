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
revision: str = "10fc63eb296d"
down_revision: Union[str, None] = "2cedfbb519dd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Adicionar colunas created_at e updated_at à tabela workspace_members apenas se não existirem
    op.execute(
        """
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_schema='synapscale_db' AND table_name='workspace_members' AND column_name='created_at'
        ) THEN
            ALTER TABLE synapscale_db.workspace_members 
            ADD COLUMN created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL;
        END IF;
        
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_schema='synapscale_db' AND table_name='workspace_members' AND column_name='updated_at'
        ) THEN
            ALTER TABLE synapscale_db.workspace_members 
            ADD COLUMN updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL;
        END IF;
    END$$;
    """
    )

    # Atualizar created_at para usar joined_at quando disponível
    op.execute(
        """
        UPDATE synapscale_db.workspace_members 
        SET created_at = joined_at 
        WHERE joined_at IS NOT NULL AND created_at != joined_at
    """
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Remover as colunas adicionadas apenas se existirem
    op.execute(
        """
    DO $$
    BEGIN
        IF EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_schema='synapscale_db' AND table_name='workspace_members' AND column_name='updated_at'
        ) THEN
            ALTER TABLE synapscale_db.workspace_members DROP COLUMN updated_at;
        END IF;
        
        IF EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_schema='synapscale_db' AND table_name='workspace_members' AND column_name='created_at'
        ) THEN
            ALTER TABLE synapscale_db.workspace_members DROP COLUMN created_at;
        END IF;
    END$$;
    """
    )
