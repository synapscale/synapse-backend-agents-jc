"""Add tenant_id foreign key to billing_events table

Revision ID: 18130f981b06
Revises: 38215f9aed79
Create Date: 2025-07-04 13:45:12.301301

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision: str = '18130f981b06'
down_revision: Union[str, None] = '38215f9aed79'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create foreign key constraint
    op.create_foreign_key(
        'fk_billing_events_tenant_id',
        'billing_events',
        'tenants',
        ['tenant_id'],
        ['id'],
        source_schema='synapscale_db',
        referent_schema='synapscale_db',
        ondelete='CASCADE'
    )
    
    # Create index for better performance
    # op.create_index(
    #     "idx_billing_events_tenant_id",
    #     "billing_events",
    #     ["tenant_id"],
    #     unique=False,
    #     schema="synapscale_db"
    # )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop index
    # op.drop_index(
    #     'idx_billing_events_tenant_id',
    #     'billing_events',
    #     schema='synapscale_db'
    # )
    
    # Drop foreign key constraint
    op.drop_constraint(
        'fk_billing_events_tenant_id',
        'billing_events',
        type_='foreignkey',
        schema='synapscale_db'
    )
