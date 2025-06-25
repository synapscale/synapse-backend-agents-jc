"""
Corrige tipo de workspace_id na tabela conversations e foreign keys relacionadas
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = 'd1bd1387'
down_revision = 'c02a345b'
branch_labels = None
depends_on = None

def upgrade():
    """Corrige workspace_id para UUID e foreign keys"""
    
    # 1. Corrigir workspace_id para UUID se necessário
    op.execute("""
    DO $$
    BEGIN
        -- Verifica se a coluna workspace_id já é UUID
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_schema = 'synapscale_db' 
            AND table_name = 'llms_conversations' 
            AND column_name = 'workspace_id'
            AND udt_name = 'uuid'
        ) THEN
            -- Se não for UUID, converte
            ALTER TABLE synapscale_db.llms_conversations 
            ALTER COLUMN workspace_id TYPE UUID USING workspace_id::uuid;
        END IF;
    END$$;
    """)
    
    # 2. Adicionar foreign key para workspace_id se não existir
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.table_constraints 
            WHERE constraint_schema = 'synapscale_db'
            AND table_name = 'llms_conversations'
            AND constraint_name = 'llms_conversations_workspace_id_fkey'
        ) THEN
            ALTER TABLE synapscale_db.llms_conversations
            ADD CONSTRAINT llms_conversations_workspace_id_fkey
            FOREIGN KEY (workspace_id) REFERENCES synapscale_db.workspaces(id)
            ON DELETE SET NULL;
        END IF;
    END$$;
    """)
    
    # 3. Corrigir agent_id foreign key para schema correto se necessário
    op.execute("""
    DO $$
    BEGIN
        -- Remove constraint antiga se existir
        IF EXISTS (
            SELECT 1 FROM information_schema.table_constraints 
            WHERE constraint_schema = 'synapscale_db'
            AND table_name = 'llms_conversations'
            AND constraint_name = 'llms_conversations_agent_id_fkey'
        ) THEN
            ALTER TABLE synapscale_db.llms_conversations
            DROP CONSTRAINT llms_conversations_agent_id_fkey;
        END IF;
        
        -- Adiciona constraint correta
        ALTER TABLE synapscale_db.llms_conversations
        ADD CONSTRAINT llms_conversations_agent_id_fkey
        FOREIGN KEY (agent_id) REFERENCES synapscale_db.agents(id)
        ON DELETE SET NULL ON UPDATE CASCADE;
    END$$;
    """)

def downgrade():
    """Reverte as alterações"""
    
    # Remove as foreign keys adicionadas
    op.execute("""
    DO $$
    BEGIN
        IF EXISTS (
            SELECT 1 FROM information_schema.table_constraints 
            WHERE constraint_schema = 'synapscale_db'
            AND table_name = 'llms_conversations'
            AND constraint_name = 'llms_conversations_workspace_id_fkey'
        ) THEN
            ALTER TABLE synapscale_db.llms_conversations
            DROP CONSTRAINT llms_conversations_workspace_id_fkey;
        END IF;
    END$$;
    """)
    
    # Nota: Não revertemos o tipo da coluna para preservar dados 