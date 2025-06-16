"""
Adiciona valor 'operation' ao Enum nodetype
"""
from alembic import op

revision = '007addoptoenum'
down_revision = 'b25def6b9d26'
branch_labels = None
depends_on = None

def upgrade():
    op.execute("ALTER TYPE nodetype ADD VALUE IF NOT EXISTS 'operation';")

def downgrade():
    # Não é possível remover valores de Enum facilmente
    pass 