"""
Adiciona coluna 'type' na tabela nodes
"""

from alembic import op
import sqlalchemy as sa
import enum

revision = "008addtypecolnodes"
down_revision = "007addoptoenum"
branch_labels = None
depends_on = None


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
        "nodes",
        sa.Column(
            "type",
            sa.Enum(*[e.value for e in NodeType], name="nodetype"),
            nullable=False,
            server_default="operation",
        ),
        schema="synapscale_db",
    )


def downgrade():
    op.drop_column("nodes", "type", schema="synapscale_db")
