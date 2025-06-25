"""
Corrige tipo de conversation_id na tabela messages de String para UUID
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = 'c02a345b'
down_revision = 'b6816ff0'
branch_labels = None
depends_on = None

def upgrade():
    """Corrige conversation_id para UUID"""
    
    # 1. Primeiro, remove a constraint de foreign key existente
    op.drop_constraint('llms_messages_conversation_id_fkey', 'llms_messages', type_='foreignkey', schema='synapscale_db')
    
    # 2. Converte a coluna para UUID (assumindo que os dados existentes são UUIDs válidos em formato string)
    op.execute("""
        ALTER TABLE synapscale_db.llms_messages 
        ALTER COLUMN conversation_id TYPE UUID USING conversation_id::uuid
    """)
    
    # 3. Recria a foreign key constraint apontando para o schema correto
    op.create_foreign_key(
        'llms_messages_conversation_id_fkey',
        'llms_messages', 'llms_conversations',
        ['conversation_id'], ['id'],
        source_schema='synapscale_db',
        referent_schema='synapscale_db',
        ondelete='CASCADE',
        onupdate='CASCADE'
    )

def downgrade():
    """Reverte conversation_id para String"""
    
    # Remove a foreign key constraint
    op.drop_constraint('llms_messages_conversation_id_fkey', 'llms_messages', type_='foreignkey', schema='synapscale_db')
    
    # Converte de volta para String
    op.execute("""
        ALTER TABLE synapscale_db.llms_messages 
        ALTER COLUMN conversation_id TYPE VARCHAR(30) USING conversation_id::varchar
    """)
    
    # Recria a foreign key constraint original
    op.create_foreign_key(
        'llms_messages_conversation_id_fkey',
        'llms_messages', 'llms_conversations',
        ['conversation_id'], ['id'],
        source_schema='synapscale_db',
        referent_schema='synapscale_db',
        ondelete='CASCADE',
        onupdate='CASCADE'
    ) 