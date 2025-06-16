"""
Garante que todos os valores existem no Enum nodestatus
"""
from alembic import op

revision = '009addnodestatusenum'
down_revision = '008addtypecolnodes'
branch_labels = None
depends_on = None

def upgrade():
    op.execute("ALTER TYPE nodestatus ADD VALUE IF NOT EXISTS 'draft';")
    op.execute("ALTER TYPE nodestatus ADD VALUE IF NOT EXISTS 'published';")
    op.execute("ALTER TYPE nodestatus ADD VALUE IF NOT EXISTS 'deprecated';")
    op.execute("ALTER TYPE nodestatus ADD VALUE IF NOT EXISTS 'private';")

def downgrade():
    pass  # Não é possível remover valores de Enum facilmente 