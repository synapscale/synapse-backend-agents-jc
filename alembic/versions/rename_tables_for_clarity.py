"""Rename tables for better clarity and organization

Revision ID: rename_tables
Revises: a5f72854
Create Date: 2025-01-07 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'rename_tables'
down_revision = 'a5f72854'
branch_labels = None
depends_on = None


def upgrade():
    """Rename tables to clearer names"""
    
    # Rename LLM-related tables
    op.execute("ALTER TABLE synapscale_db.usage_logs RENAME TO llms_usage_logs")
    op.execute("ALTER TABLE synapscale_db.messages RENAME TO llms_messages")
    op.execute("ALTER TABLE synapscale_db.message_feedbacks RENAME TO llms_message_feedbacks")
    op.execute("ALTER TABLE synapscale_db.conversations RENAME TO llms_conversations")
    op.execute("ALTER TABLE synapscale_db.conversation_llms RENAME TO llms_conversations_turns")
    
    # Rename workflow-related tables
    op.execute("ALTER TABLE synapscale_db.execution_metrics RENAME TO workflow_execution_metrics")
    op.execute("ALTER TABLE synapscale_db.execution_queue RENAME TO workflow_execution_queue")


def downgrade():
    """Revert table names to original"""
    
    # Revert workflow-related tables (order reversed for proper cleanup)
    op.execute("ALTER TABLE synapscale_db.workflow_execution_queue RENAME TO execution_queue")
    op.execute("ALTER TABLE synapscale_db.workflow_execution_metrics RENAME TO execution_metrics")
    
    # Revert LLM-related tables
    op.execute("ALTER TABLE synapscale_db.llms_conversations_turns RENAME TO conversation_llms")
    op.execute("ALTER TABLE synapscale_db.llms_conversations RENAME TO conversations")
    op.execute("ALTER TABLE synapscale_db.llms_message_feedbacks RENAME TO message_feedbacks")
    op.execute("ALTER TABLE synapscale_db.llms_messages RENAME TO messages")
    op.execute("ALTER TABLE synapscale_db.llms_usage_logs RENAME TO usage_logs") 