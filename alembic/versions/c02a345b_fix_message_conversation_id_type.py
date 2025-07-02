"""
Corrige tipo de conversation_id na tabela messages de String para UUID
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "c02a345b"
down_revision = "b6816ff0"
branch_labels = None
depends_on = None


def upgrade():
    """Corrige conversation_id para UUID"""

    # Verifica se a constraint existe antes de tentar removê-la
    conn = op.get_bind()
    constraint_exists = conn.execute(
        sa.text(
            """
        SELECT EXISTS (
            SELECT 1 FROM information_schema.table_constraints 
            WHERE constraint_name = 'llms_messages_conversation_id_fkey' 
            AND table_name = 'llms_messages'
            AND table_schema = 'synapscale_db'
        )
    """
        )
    ).scalar()

    # 1. Remove a constraint de foreign key existente (se existir)
    if constraint_exists:
        op.drop_constraint(
            "llms_messages_conversation_id_fkey",
            "llms_messages",
            type_="foreignkey",
            schema="synapscale_db",
        )

    # 2. Verifica se a tabela llms_messages existe no schema correto
    table_exists = conn.execute(
        sa.text(
            """
        SELECT EXISTS (
            SELECT 1 FROM information_schema.tables 
            WHERE table_name = 'llms_messages'
            AND table_schema = 'synapscale_db'
        )
    """
        )
    ).scalar()

    if table_exists:
        # 3. Converte a coluna para UUID (assumindo que os dados existentes são UUIDs válidos em formato string)
        op.execute(
            """
            ALTER TABLE synapscale_db.llms_messages 
            ALTER COLUMN conversation_id TYPE UUID USING conversation_id::uuid
        """
        )

        # 4. Verifica se a tabela de destino existe
        target_table_exists = conn.execute(
            sa.text(
                """
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables 
                WHERE table_name = 'llms_conversations'
                AND table_schema = 'synapscale_db'
            )
        """
            )
        ).scalar()

        # 5. Recria a foreign key constraint apontando para o schema correto (se ambas as tabelas existirem)
        if target_table_exists:
            op.create_foreign_key(
                "llms_messages_conversation_id_fkey",
                "llms_messages",
                "llms_conversations",
                ["conversation_id"],
                ["id"],
                source_schema="synapscale_db",
                referent_schema="synapscale_db",
                ondelete="CASCADE",
                onupdate="CASCADE",
            )


def downgrade():
    """Reverte conversation_id para String"""

    conn = op.get_bind()

    # Verifica se a constraint existe antes de tentar removê-la
    constraint_exists = conn.execute(
        sa.text(
            """
        SELECT EXISTS (
            SELECT 1 FROM information_schema.table_constraints 
            WHERE constraint_name = 'llms_messages_conversation_id_fkey' 
            AND table_name = 'llms_messages'
            AND table_schema = 'synapscale_db'
        )
    """
        )
    ).scalar()

    # Remove a foreign key constraint (se existir)
    if constraint_exists:
        op.drop_constraint(
            "llms_messages_conversation_id_fkey",
            "llms_messages",
            type_="foreignkey",
            schema="synapscale_db",
        )

    # Verifica se a tabela existe antes de tentar modificá-la
    table_exists = conn.execute(
        sa.text(
            """
        SELECT EXISTS (
            SELECT 1 FROM information_schema.tables 
            WHERE table_name = 'llms_messages'
            AND table_schema = 'synapscale_db'
        )
    """
        )
    ).scalar()

    if table_exists:
        # Converte de volta para String
        op.execute(
            """
            ALTER TABLE synapscale_db.llms_messages 
            ALTER COLUMN conversation_id TYPE VARCHAR(30) USING conversation_id::varchar
        """
        )

        # Verifica se a tabela de destino existe
        target_table_exists = conn.execute(
            sa.text(
                """
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables 
                WHERE table_name = 'llms_conversations'
                AND table_schema = 'synapscale_db'
            )
        """
            )
        ).scalar()

        # Recria a foreign key constraint original (se ambas as tabelas existirem)
        if target_table_exists:
            op.create_foreign_key(
                "llms_messages_conversation_id_fkey",
                "llms_messages",
                "llms_conversations",
                ["conversation_id"],
                ["id"],
                source_schema="synapscale_db",
                referent_schema="synapscale_db",
                ondelete="CASCADE",
                onupdate="CASCADE",
            )
