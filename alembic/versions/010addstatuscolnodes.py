"""
Adiciona coluna 'status' na tabela nodes
"""
from alembic import op
import sqlalchemy as sa

revision = '010addstatuscolnodes'
down_revision = '009addnodestatusenum'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column(
        'nodes',
        sa.Column('status', sa.Enum('draft', 'published', 'deprecated', 'private', name='nodestatus'), nullable=False, server_default="draft"),
        schema='synapscale_db'
    )

def downgrade():
    op.drop_column('nodes', 'status', schema='synapscale_db') 