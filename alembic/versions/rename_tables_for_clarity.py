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
    
    # Verificar se as tabelas existem antes de renomear
    inspector = sa.inspect(op.get_bind())
    existing_tables = inspector.get_table_names(schema='synapscale_db')
    
    # Rename LLM-related tables only if they exist
    if 'usage_logs' in existing_tables:
        op.execute("ALTER TABLE synapscale_db.usage_logs RENAME TO llms_usage_logs")
    
    if 'messages' in existing_tables:
        op.execute("ALTER TABLE synapscale_db.messages RENAME TO llms_messages")
    
    if 'message_feedbacks' in existing_tables:
        op.execute("ALTER TABLE synapscale_db.message_feedbacks RENAME TO llms_message_feedbacks")
    
    if 'conversations' in existing_tables:
        op.execute("ALTER TABLE synapscale_db.conversations RENAME TO llms_conversations")
    
    if 'conversation_llms' in existing_tables:
        op.execute("ALTER TABLE synapscale_db.conversation_llms RENAME TO llms_conversations_turns")
    
    # Rename workflow-related tables only if they exist
    if 'execution_metrics' in existing_tables:
        op.execute("ALTER TABLE synapscale_db.execution_metrics RENAME TO workflow_execution_metrics")
    
    if 'execution_queue' in existing_tables:
        op.execute("ALTER TABLE synapscale_db.execution_queue RENAME TO workflow_execution_queue")


def downgrade():
    """Revert table names to original"""
    
    # Verificar se as tabelas existem antes de renomear de volta
    inspector = sa.inspect(op.get_bind())
    existing_tables = inspector.get_table_names(schema='synapscale_db')
    
    # Revert workflow-related tables (order reversed for proper cleanup)
    if 'workflow_execution_queue' in existing_tables:
        op.execute("ALTER TABLE synapscale_db.workflow_execution_queue RENAME TO execution_queue")
    
    if 'workflow_execution_metrics' in existing_tables:
        op.execute("ALTER TABLE synapscale_db.workflow_execution_metrics RENAME TO execution_metrics")
    
    # Revert LLM-related tables
    if 'llms_conversations_turns' in existing_tables:
        op.execute("ALTER TABLE synapscale_db.llms_conversations_turns RENAME TO conversation_llms")
    
    if 'llms_conversations' in existing_tables:
        op.execute("ALTER TABLE synapscale_db.llms_conversations RENAME TO conversations")
    
    if 'llms_message_feedbacks' in existing_tables:
        op.execute("ALTER TABLE synapscale_db.llms_message_feedbacks RENAME TO message_feedbacks")
    
    if 'llms_messages' in existing_tables:
        op.execute("ALTER TABLE synapscale_db.llms_messages RENAME TO messages")
    
    if 'llms_usage_logs' in existing_tables:
        op.execute("ALTER TABLE synapscale_db.llms_usage_logs RENAME TO usage_logs") 