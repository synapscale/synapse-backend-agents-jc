"""add is_encrypted column to user_variables

Revision ID: 7a1b2c3d4e5f
Revises: 6ef07e4e9be1
Create Date: 2025-06-16 16:40:00

"""
revision = '7a1b2c3d4e5f'
down_revision = '6ef07e4e9be1'
branch_labels = None
depends_on = None
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('user_variables', sa.Column('is_encrypted', sa.Boolean(), nullable=False, server_default=sa.text('false')), schema='synapscale_db')

def downgrade():
    op.drop_column('user_variables', 'is_encrypted', schema='synapscale_db') 