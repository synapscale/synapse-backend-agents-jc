"""add plan_id to workspaces

Revision ID: add_plan_id_manual
Revises: b780a865dc0f
Create Date: 2024-12-20 14:52:00.000000

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision = "add_plan_id_manual"
down_revision = "b780a865dc0f"
branch_labels = None
depends_on = None


def upgrade():
    # Adicionar coluna plan_id à tabela workspaces
    op.add_column(
        "workspaces",
        sa.Column("plan_id", UUID(as_uuid=True), nullable=True),
        schema="synapscale_db",
    )

    # Criar foreign key para plans
    op.create_foreign_key(
        "fk_workspaces_plan_id",
        "workspaces",
        "plans",
        ["plan_id"],
        ["id"],
        source_schema="synapscale_db",
        referent_schema="synapscale_db",
    )

    # Criar índice para performance
    op.create_index(
        "ix_workspaces_plan_id", "workspaces", ["plan_id"], schema="synapscale_db"
    )

    # Atualizar workspaces existentes com plano free
    op.execute(
        """
        UPDATE synapscale_db.workspaces 
        SET plan_id = (
            SELECT id FROM synapscale_db.plans 
            WHERE slug = 'free' 
            LIMIT 1
        )
        WHERE plan_id IS NULL
    """
    )

    # Tornar o campo obrigatório após atualizar dados existentes
    op.alter_column("workspaces", "plan_id", nullable=False, schema="synapscale_db")


def downgrade():
    op.drop_index("ix_workspaces_plan_id", "workspaces", schema="synapscale_db")
    op.drop_constraint("fk_workspaces_plan_id", "workspaces", schema="synapscale_db")
    op.drop_column("workspaces", "plan_id", schema="synapscale_db")
