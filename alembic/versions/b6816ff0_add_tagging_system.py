"""
Adiciona sistema de tagging flexível para conversations e messages
"""
from alembic import op
import sqlalchemy as sa

revision = 'b6816ff0'
down_revision = 'a5f72854'
branch_labels = None
depends_on = None

def upgrade():
    """Adiciona sistema de tagging"""
    
    # Verificar se a tabela já existe antes de criar
    inspector = sa.inspect(op.get_bind())
    existing_tables = inspector.get_table_names(schema='synapscale_db')
    
    if 'tags' not in existing_tables:
        # Tabela de tags para conversations, messages, users, etc
        op.create_table(
            'tags',
            sa.Column('id', sa.UUID(), nullable=False),
            sa.Column('target_type', sa.String(50), nullable=False),  # conversation, message, user, workspace
            sa.Column('target_id', sa.UUID(), nullable=False),
            sa.Column('tag_name', sa.String(100), nullable=False),
            sa.Column('tag_value', sa.Text(), nullable=True),  # Opcional: valor da tag
            sa.Column('tag_category', sa.String(50), nullable=True),  # categoria da tag
            sa.Column('is_system_tag', sa.Boolean(), server_default='false'),  # tag do sistema vs usuário
            sa.Column('created_by_user_id', sa.UUID(), nullable=True),
            sa.Column('auto_generated', sa.Boolean(), server_default='false'),
            sa.Column('confidence_score', sa.Float(), nullable=True),  # Para tags automáticas
            sa.Column('tag_metadata', sa.JSON(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.ForeignKeyConstraint(['created_by_user_id'], ['synapscale_db.users.id'], ondelete='SET NULL'),
            sa.PrimaryKeyConstraint('id'),
            schema='synapscale_db'
        )
        op.create_index('ix_tags_target_type', 'tags', ['target_type'], schema='synapscale_db')
        op.create_index('ix_tags_target_id', 'tags', ['target_id'], schema='synapscale_db')
        op.create_index('ix_tags_tag_name', 'tags', ['tag_name'], schema='synapscale_db')
        op.create_index('ix_tags_tag_category', 'tags', ['tag_category'], schema='synapscale_db')
        op.create_index('ix_tags_is_system_tag', 'tags', ['is_system_tag'], schema='synapscale_db')
        op.create_index('ix_tags_created_by_user_id', 'tags', ['created_by_user_id'], schema='synapscale_db')

def downgrade():
    """Remove sistema de tagging"""
    # Verificar se a tabela existe antes de tentar removê-la
    inspector = sa.inspect(op.get_bind())
    existing_tables = inspector.get_table_names(schema='synapscale_db')
    
    if 'tags' in existing_tables:
        op.drop_table('tags', schema='synapscale_db') 