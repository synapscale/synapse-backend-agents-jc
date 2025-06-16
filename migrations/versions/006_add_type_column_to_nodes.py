"""
Migração 006: Adiciona coluna 'type' na tabela nodes
"""
from alembic import op
import sqlalchemy as sa
import enum

# Revisão Alembic
revision = '006_add_type_column_to_nodes'
down_revision = None  # Ajuste para a última revisão real do seu projeto
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
    op.add_column(
        'nodes',
        sa.Column('type', sa.Enum(*[e.value for e in NodeType], name='nodetype'), nullable=False, server_default="operation")
    )

def downgrade():
    op.drop_column('nodes', 'type')
    sa.Enum(name='nodetype').drop(op.get_bind()) 