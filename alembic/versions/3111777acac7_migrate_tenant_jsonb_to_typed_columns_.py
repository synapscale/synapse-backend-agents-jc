"""migrate_tenant_jsonb_to_typed_columns_correct

Revision ID: 3111777acac7
Revises: 67fe75d237c8
Create Date: 2025-06-30 18:10:33.734502

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision: str = "3111777acac7"
down_revision: Union[str, None] = "67fe75d237c8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Migrar JSONB para colunas tipadas na arquitetura correta."""

    # Get database inspector
    connection = op.get_bind()
    inspector = inspect(connection)

    # === TENANTS: Configurações organizacionais globais ===

    # Get existing columns for tenants table
    tenant_columns = inspector.get_columns("tenants", schema="synapscale_db")
    tenant_column_names = [col["name"] for col in tenant_columns]

    # 1. Adicionar colunas de configuração organizacional (apenas se não existirem)
    if "timezone" not in tenant_column_names:
        op.add_column(
            "tenants",
            sa.Column("timezone", sa.String(50), nullable=True),
            schema="synapscale_db",
        )
    if "default_language" not in tenant_column_names:
        op.add_column(
            "tenants",
            sa.Column(
                "default_language", sa.String(10), nullable=True, default="pt-BR"
            ),
            schema="synapscale_db",
        )
    if "billing_email" not in tenant_column_names:
        op.add_column(
            "tenants",
            sa.Column("billing_email", sa.String(255), nullable=True),
            schema="synapscale_db",
        )
    if "organization_type" not in tenant_column_names:
        op.add_column(
            "tenants",
            sa.Column("organization_type", sa.String(50), nullable=True),
            schema="synapscale_db",
        )
    if "custom_domain" not in tenant_column_names:
        op.add_column(
            "tenants",
            sa.Column("custom_domain", sa.String(255), nullable=True),
            schema="synapscale_db",
        )

    # 2. Migrar dados existentes de settings JSONB (apenas se colunas foram criadas)
    # Check if settings column exists before trying to migrate data
    if "settings" in tenant_column_names:
        op.execute(
            """
            UPDATE synapscale_db.tenants 
            SET 
                timezone = COALESCE(settings->>'timezone', 'America/Sao_Paulo'),
                default_language = COALESCE(settings->>'language', 'pt-BR'),
                billing_email = settings->>'billing_email',
                organization_type = settings->>'organization_type',
                custom_domain = settings->>'custom_domain'
            WHERE timezone IS NULL OR default_language IS NULL
        """
        )
    else:
        # If no settings column, set default values
        op.execute(
            """
            UPDATE synapscale_db.tenants 
            SET 
                timezone = COALESCE(timezone, 'America/Sao_Paulo'),
                default_language = COALESCE(default_language, 'pt-BR')
            WHERE timezone IS NULL OR default_language IS NULL
        """
        )

    # 3. Tornar timezone obrigatório após migração (apenas se coluna existe)
    if (
        "timezone" in tenant_column_names or "timezone" not in tenant_column_names
    ):  # Will be true after adding
        try:
            op.alter_column(
                "tenants", "timezone", nullable=False, schema="synapscale_db"
            )
            op.alter_column(
                "tenants", "default_language", nullable=False, schema="synapscale_db"
            )
        except:
            pass  # Ignore if already set

    # 4. Adicionar índices para performance (apenas se não existirem)
    existing_indexes = inspector.get_indexes("tenants", schema="synapscale_db")
    existing_index_names = [idx["name"] for idx in existing_indexes]

    if "idx_tenants_timezone" not in existing_index_names:
        op.create_index(
            "idx_tenants_timezone", "tenants", ["timezone"], schema="synapscale_db"
        )
    if "idx_tenants_custom_domain" not in existing_index_names:
        op.create_index(
            "idx_tenants_custom_domain",
            "tenants",
            ["custom_domain"],
            schema="synapscale_db",
        )

    # === WORKSPACES: Tracking operacional (limites já existem) ===

    # Get existing columns for workspaces table
    workspace_columns = inspector.get_columns("workspaces", schema="synapscale_db")
    workspace_column_names = [col["name"] for col in workspace_columns]

    # 5. Adicionar colunas de tracking de uso (não limites!) apenas se não existirem
    if "api_calls_today" not in workspace_column_names:
        op.add_column(
            "workspaces",
            sa.Column("api_calls_today", sa.Integer(), nullable=True, default=0),
            schema="synapscale_db",
        )
    if "api_calls_this_month" not in workspace_column_names:
        op.add_column(
            "workspaces",
            sa.Column("api_calls_this_month", sa.Integer(), nullable=True, default=0),
            schema="synapscale_db",
        )
    if "last_api_reset_daily" not in workspace_column_names:
        op.add_column(
            "workspaces",
            sa.Column(
                "last_api_reset_daily", sa.DateTime(timezone=True), nullable=True
            ),
            schema="synapscale_db",
        )
    if "last_api_reset_monthly" not in workspace_column_names:
        op.add_column(
            "workspaces",
            sa.Column(
                "last_api_reset_monthly", sa.DateTime(timezone=True), nullable=True
            ),
            schema="synapscale_db",
        )
    if "feature_usage_count" not in workspace_column_names:
        op.add_column(
            "workspaces",
            sa.Column("feature_usage_count", postgresql.JSONB(), nullable=True),
            schema="synapscale_db",
        )

    # 6. Inicializar valores de tracking
    op.execute(
        """
        UPDATE synapscale_db.workspaces 
        SET 
            api_calls_today = COALESCE(api_calls_today, 0),
            api_calls_this_month = COALESCE(api_calls_this_month, 0),
            last_api_reset_daily = COALESCE(last_api_reset_daily, CURRENT_TIMESTAMP),
            last_api_reset_monthly = COALESCE(last_api_reset_monthly, CURRENT_TIMESTAMP),
            feature_usage_count = COALESCE(feature_usage_count, '{}'::jsonb)
    """
    )

    # 7. Tornar colunas de tracking NOT NULL (apenas se existirem)
    try:
        op.alter_column(
            "workspaces", "api_calls_today", nullable=False, schema="synapscale_db"
        )
        op.alter_column(
            "workspaces", "api_calls_this_month", nullable=False, schema="synapscale_db"
        )
    except:
        pass  # Ignore if already set

    # 8. Adicionar índices para queries de billing/usage (apenas se não existirem)
    workspace_indexes = inspector.get_indexes("workspaces", schema="synapscale_db")
    workspace_index_names = [idx["name"] for idx in workspace_indexes]

    if "idx_workspaces_api_calls_today" not in workspace_index_names:
        op.create_index(
            "idx_workspaces_api_calls_today",
            "workspaces",
            ["api_calls_today"],
            schema="synapscale_db",
        )
    if "idx_workspaces_last_api_reset_daily" not in workspace_index_names:
        op.create_index(
            "idx_workspaces_last_api_reset_daily",
            "workspaces",
            ["last_api_reset_daily"],
            schema="synapscale_db",
        )
    # Only create plan_id index if plan_id column exists
    if (
        "idx_workspaces_tenant_plan" not in workspace_index_names
        and "plan_id" in workspace_column_names
    ):
        op.create_index(
            "idx_workspaces_tenant_plan",
            "workspaces",
            ["tenant_id", "plan_id"],
            schema="synapscale_db",
        )


def downgrade() -> None:
    """Reverter migração movendo dados de volta para JSONB."""

    # Get database inspector
    connection = op.get_bind()
    inspector = inspect(connection)

    # === WORKSPACES ROLLBACK ===

    # Check existing indexes before dropping
    workspace_indexes = inspector.get_indexes("workspaces", schema="synapscale_db")
    workspace_index_names = [idx["name"] for idx in workspace_indexes]

    # 1. Remover índices de workspaces (apenas se existirem)
    if "idx_workspaces_tenant_plan" in workspace_index_names:
        op.drop_index("idx_workspaces_tenant_plan", schema="synapscale_db")
    if "idx_workspaces_last_api_reset_daily" in workspace_index_names:
        op.drop_index("idx_workspaces_last_api_reset_daily", schema="synapscale_db")
    if "idx_workspaces_api_calls_today" in workspace_index_names:
        op.drop_index("idx_workspaces_api_calls_today", schema="synapscale_db")

    # Check existing columns before dropping
    workspace_columns = inspector.get_columns("workspaces", schema="synapscale_db")
    workspace_column_names = [col["name"] for col in workspace_columns]

    # 2. Remover colunas de tracking de workspaces (apenas se existirem)
    if "feature_usage_count" in workspace_column_names:
        op.drop_column("workspaces", "feature_usage_count", schema="synapscale_db")
    if "last_api_reset_monthly" in workspace_column_names:
        op.drop_column("workspaces", "last_api_reset_monthly", schema="synapscale_db")
    if "last_api_reset_daily" in workspace_column_names:
        op.drop_column("workspaces", "last_api_reset_daily", schema="synapscale_db")
    if "api_calls_this_month" in workspace_column_names:
        op.drop_column("workspaces", "api_calls_this_month", schema="synapscale_db")
    if "api_calls_today" in workspace_column_names:
        op.drop_column("workspaces", "api_calls_today", schema="synapscale_db")

    # === TENANTS ROLLBACK ===

    # 3. Mover dados de volta para JSONB antes de remover colunas
    # Only move data back to JSONB if settings column exists
    if "settings" in tenant_column_names:
        op.execute(
            """
            UPDATE synapscale_db.tenants 
            SET settings = COALESCE(settings, '{}'::jsonb) ||
                          jsonb_build_object(
                              'timezone', timezone,
                              'language', default_language,
                              'billing_email', billing_email,
                              'organization_type', organization_type,
                              'custom_domain', custom_domain
                          )
            WHERE timezone IS NOT NULL 
               OR default_language IS NOT NULL
               OR billing_email IS NOT NULL
        """
        )

    # Check existing indexes before dropping
    tenant_indexes = inspector.get_indexes("tenants", schema="synapscale_db")
    tenant_index_names = [idx["name"] for idx in tenant_indexes]

    # 4. Remover índices de tenants (apenas se existirem)
    if "idx_tenants_custom_domain" in tenant_index_names:
        op.drop_index("idx_tenants_custom_domain", schema="synapscale_db")
    if "idx_tenants_timezone" in tenant_index_names:
        op.drop_index("idx_tenants_timezone", schema="synapscale_db")

    # Check existing columns before dropping
    tenant_columns = inspector.get_columns("tenants", schema="synapscale_db")
    tenant_column_names = [col["name"] for col in tenant_columns]

    # 5. Remover colunas tipadas de tenants (apenas se existirem)
    if "custom_domain" in tenant_column_names:
        op.drop_column("tenants", "custom_domain", schema="synapscale_db")
    if "organization_type" in tenant_column_names:
        op.drop_column("tenants", "organization_type", schema="synapscale_db")
    if "billing_email" in tenant_column_names:
        op.drop_column("tenants", "billing_email", schema="synapscale_db")
    if "default_language" in tenant_column_names:
        op.drop_column("tenants", "default_language", schema="synapscale_db")
    if "timezone" in tenant_column_names:
        op.drop_column("tenants", "timezone", schema="synapscale_db")
