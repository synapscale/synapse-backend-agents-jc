"""
Adiciona a coluna 'type' na tabela nodes
"""
from alembic import op
import sqlalchemy as sa
import enum

revision = '006_add_type_column_to_nodes'
down_revision = 'b25def6b9d26'
branch_labels = None
depends_on = None

# Enum igual ao modelo
class NodeType(enum.Enum):
    LLM = "llm"
    TRANSFORM = "transform"
    API = "api"
    CONDITION = "condition"
    TRIGGER = "trigger"
    OPERATION = "operation"
    FLOW = "flow"
    INPUT = "input"
    OUTPUT = "output"
    FILE_PROCESSOR = "file_processor"

def upgrade():
    # Adiciona o valor 'operation' ao Enum nodetype, se não existir
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_type t JOIN pg_enum e ON t.oid = e.enumtypid WHERE t.typname = 'nodetype' AND e.enumlabel = 'operation') THEN
            ALTER TYPE nodetype ADD VALUE 'operation';
        END IF;
    END$$;
    """)
    # Só adiciona a coluna se ela não existir
    op.execute('''
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_schema='synapscale_db' AND table_name='nodes' AND column_name='type'
        ) THEN
            ALTER TABLE synapscale_db.nodes ADD COLUMN type nodetype DEFAULT 'operation' NOT NULL;
        END IF;
    END$$;
    ''')

def downgrade():
    op.drop_column('nodes', 'type')
    sa.Enum(name='nodetype').drop(op.get_bind()) 