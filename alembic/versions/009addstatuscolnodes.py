"""
Adiciona coluna 'status' na tabela nodes
"""
from alembic import op
import sqlalchemy as sa
import enum

revision = '009addstatuscolnodes'
down_revision = '008addtypecolnodes'
branch_labels = None
depends_on = None

class NodeStatus(enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    DEPRECATED = "deprecated"
    PRIVATE = "private"

def upgrade():
    op.execute("ALTER TYPE nodestatus ADD VALUE IF NOT EXISTS 'draft';")
    op.execute("ALTER TYPE nodestatus ADD VALUE IF NOT EXISTS 'published';")
    op.execute("ALTER TYPE nodestatus ADD VALUE IF NOT EXISTS 'deprecated';")
    op.execute("ALTER TYPE nodestatus ADD VALUE IF NOT EXISTS 'private';")
    op.execute('''
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_schema='synapscale_db' AND table_name='nodes' AND column_name='status'
        ) THEN
            ALTER TABLE synapscale_db.nodes ADD COLUMN status nodestatus DEFAULT 'draft' NOT NULL;
        END IF;
    END$$;
    ''')

def downgrade():
    op.drop_column('nodes', 'status', schema='synapscale_db') 