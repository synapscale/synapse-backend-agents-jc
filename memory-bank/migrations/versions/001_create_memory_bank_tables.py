"""
Script de migração para criar as tabelas do Memory Bank
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from datetime import datetime

# Revisão
revision = 'memory_bank_tables_001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    """Cria as tabelas do Memory Bank"""
    
    # Criar tabela de coleções
    op.create_table(
        'memory_bank_collections',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('workspace_id', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['synapscale_db.users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['workspace_id'], ['synapscale_db.workspaces.id'], ondelete='CASCADE'),
        schema='synapscale_db'
    )
    
    # Criar índices para coleções
    op.create_index('ix_memory_bank_collections_user_id', 'memory_bank_collections', ['user_id'], schema='synapscale_db')
    op.create_index('ix_memory_bank_collections_workspace_id', 'memory_bank_collections', ['workspace_id'], schema='synapscale_db')
    op.create_index('ix_memory_bank_collections_name', 'memory_bank_collections', ['name'], schema='synapscale_db')
    
    # Criar tabela de memórias
    op.create_table(
        'memory_bank_memories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('embedding', postgresql.ARRAY(sa.Float()), nullable=True),
        sa.Column('metadata', postgresql.JSONB(), nullable=True),
        sa.Column('collection_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('workspace_id', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['collection_id'], ['synapscale_db.memory_bank_collections.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['synapscale_db.users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['workspace_id'], ['synapscale_db.workspaces.id'], ondelete='CASCADE'),
        schema='synapscale_db'
    )
    
    # Criar índices para memórias
    op.create_index('ix_memory_bank_memories_user_id', 'memory_bank_memories', ['user_id'], schema='synapscale_db')
    op.create_index('ix_memory_bank_memories_workspace_id', 'memory_bank_memories', ['workspace_id'], schema='synapscale_db')
    op.create_index('ix_memory_bank_memories_collection_id', 'memory_bank_memories', ['collection_id'], schema='synapscale_db')
    
    # Criar tabela de configurações do Memory Bank
    op.create_table(
        'memory_bank_settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('workspace_id', sa.Integer(), nullable=True),
        sa.Column('embedding_model', sa.String(255), nullable=False, default='all-MiniLM-L6-v2'),
        sa.Column('vector_store_type', sa.String(50), nullable=False, default='faiss'),
        sa.Column('vector_store_path', sa.String(255), nullable=True),
        sa.Column('max_memories', sa.Integer(), nullable=False, default=1000),
        sa.Column('config', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['synapscale_db.users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['workspace_id'], ['synapscale_db.workspaces.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id', 'workspace_id', name='uq_memory_bank_settings_user_workspace'),
        schema='synapscale_db'
    )
    
    # Criar índices para configurações
    op.create_index('ix_memory_bank_settings_user_id', 'memory_bank_settings', ['user_id'], schema='synapscale_db')
    op.create_index('ix_memory_bank_settings_workspace_id', 'memory_bank_settings', ['workspace_id'], schema='synapscale_db')

def downgrade():
    """Remove as tabelas do Memory Bank"""
    
    # Remover tabelas na ordem inversa
    op.drop_table('memory_bank_settings', schema='synapscale_db')
    op.drop_table('memory_bank_memories', schema='synapscale_db')
    op.drop_table('memory_bank_collections', schema='synapscale_db')
