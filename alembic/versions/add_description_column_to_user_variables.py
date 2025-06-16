"""add description column to user_variables

Revision ID: 6ef07e4e9be1
Revises: e9e3c010c5d6
Create Date: 2025-06-16 16:20:00

"""
revision = '6ef07e4e9be1'
down_revision = 'e9e3c010c5d6'
branch_labels = None
depends_on = None
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('user_variables', sa.Column('description', sa.Text(), nullable=True), schema='synapscale_db')

def downgrade():
    op.drop_column('user_variables', 'description', schema='synapscale_db') 