"""add is_active column to user_variables

Revision ID: 8b2c3d4e5f6a
Revises: 7a1b2c3d4e5f
Create Date: 2025-06-16 16:50:00

"""
revision = '8b2c3d4e5f6a'
down_revision = '7a1b2c3d4e5f'
branch_labels = None
depends_on = None
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('user_variables', sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')), schema='synapscale_db')

def downgrade():
    op.drop_column('user_variables', 'is_active', schema='synapscale_db') 