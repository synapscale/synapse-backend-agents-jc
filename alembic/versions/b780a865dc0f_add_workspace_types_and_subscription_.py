"""add_workspace_types_and_subscription_system

Revision ID: b780a865dc0f
Revises: 6f67f2913b9a
Create Date: 2025-06-20 13:52:13.127894

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'b780a865dc0f'
down_revision: Union[str, None] = '6f67f2913b9a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    
    connection = op.get_bind()
    
    # 1. Adicionar campo type à tabela workspaces usando SQL direto
    connection.execute(sa.text("""
        ALTER TABLE synapscale_db.workspaces 
        ADD COLUMN type workspacetype DEFAULT 'INDIVIDUAL' NOT NULL
    """))
    
    # 2. Criar tabela plans usando SQL direto
    connection.execute(sa.text("""
        CREATE TABLE synapscale_db.plans (
            id UUID PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            slug VARCHAR(50) NOT NULL UNIQUE,
            type plantype NOT NULL,
            description TEXT,
            price_monthly FLOAT NOT NULL DEFAULT 0.0,
            price_yearly FLOAT NOT NULL DEFAULT 0.0,
            max_workspaces INTEGER NOT NULL DEFAULT 1,
            max_members_per_workspace INTEGER NOT NULL DEFAULT 1,
            max_projects_per_workspace INTEGER NOT NULL DEFAULT 10,
            max_storage_mb INTEGER NOT NULL DEFAULT 100,
            max_executions_per_month INTEGER NOT NULL DEFAULT 100,
            allow_collaborative_workspaces BOOLEAN NOT NULL DEFAULT FALSE,
            allow_custom_domains BOOLEAN NOT NULL DEFAULT FALSE,
            allow_api_access BOOLEAN NOT NULL DEFAULT FALSE,
            allow_advanced_analytics BOOLEAN NOT NULL DEFAULT FALSE,
            allow_priority_support BOOLEAN NOT NULL DEFAULT FALSE,
            features JSON,
            restrictions JSON,
            is_active BOOLEAN NOT NULL DEFAULT TRUE,
            is_public BOOLEAN NOT NULL DEFAULT TRUE,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """))
    
    # 3. Criar tabela user_subscriptions usando SQL direto
    connection.execute(sa.text("""
        CREATE TABLE synapscale_db.user_subscriptions (
            id UUID PRIMARY KEY,
            user_id UUID NOT NULL REFERENCES synapscale_db.users(id) ON DELETE CASCADE,
            plan_id UUID NOT NULL REFERENCES synapscale_db.plans(id),
            status subscriptionstatus NOT NULL DEFAULT 'active',
            started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            expires_at TIMESTAMPTZ,
            cancelled_at TIMESTAMPTZ,
            payment_method VARCHAR(50),
            payment_provider VARCHAR(50),
            external_subscription_id VARCHAR(255),
            billing_cycle VARCHAR(20) DEFAULT 'monthly',
            current_period_start TIMESTAMPTZ,
            current_period_end TIMESTAMPTZ,
            current_workspaces INTEGER NOT NULL DEFAULT 0,
            current_storage_mb FLOAT NOT NULL DEFAULT 0.0,
            current_executions_this_month INTEGER NOT NULL DEFAULT 0,
                         subscription_metadata JSON,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """))
    
    # 4. Criar índices
    connection.execute(sa.text("CREATE INDEX idx_workspaces_type ON synapscale_db.workspaces(type)"))
    connection.execute(sa.text("CREATE INDEX idx_plans_type ON synapscale_db.plans(type)"))
    connection.execute(sa.text("CREATE INDEX idx_plans_is_active ON synapscale_db.plans(is_active)"))
    connection.execute(sa.text("CREATE INDEX idx_user_subscriptions_user_id ON synapscale_db.user_subscriptions(user_id)"))
    connection.execute(sa.text("CREATE INDEX idx_user_subscriptions_status ON synapscale_db.user_subscriptions(status)"))
    
    # 5. Inserir plano FREE padrão
    import uuid
    free_plan_id = str(uuid.uuid4())
    connection.execute(sa.text("""
        INSERT INTO synapscale_db.plans 
        (id, name, slug, type, description, price_monthly, price_yearly, max_workspaces, max_members_per_workspace, max_projects_per_workspace, max_storage_mb, max_executions_per_month, allow_collaborative_workspaces, is_active, is_public, created_at, updated_at)
        VALUES (:id, :name, :slug, :type, :description, :price_monthly, :price_yearly, :max_workspaces, :max_members_per_workspace, :max_projects_per_workspace, :max_storage_mb, :max_executions_per_month, :allow_collaborative_workspaces, :is_active, :is_public, now(), now())
    """), {
        "id": free_plan_id,
        "name": "Plano FREE",
        "slug": "free",
        "type": "free",
        "description": "Plano gratuito com recursos básicos",
        "price_monthly": 0.0,
        "price_yearly": 0.0,
        "max_workspaces": 1,
        "max_members_per_workspace": 1,
        "max_projects_per_workspace": 5,
        "max_storage_mb": 100,
        "max_executions_per_month": 50,
        "allow_collaborative_workspaces": False,
        "is_active": True,
        "is_public": True
    })
    
    # 6. Criar assinaturas FREE para todos os usuários existentes
    connection.execute(sa.text(f"""
        INSERT INTO synapscale_db.user_subscriptions 
        (id, user_id, plan_id, status, started_at, current_workspaces, created_at, updated_at)
        SELECT 
            gen_random_uuid(),
            u.id,
            '{free_plan_id}',
            'active',
            now(),
            COALESCE((SELECT COUNT(*) FROM synapscale_db.workspaces w WHERE w.owner_id = u.id), 0),
            now(),
            now()
        FROM synapscale_db.users u
        WHERE NOT EXISTS (
            SELECT 1 FROM synapscale_db.user_subscriptions s WHERE s.user_id = u.id
        )
    """))


def downgrade() -> None:
    """Downgrade schema."""
    connection = op.get_bind()
    
    # Remover índices
    connection.execute(sa.text("DROP INDEX IF EXISTS synapscale_db.idx_user_subscriptions_status"))
    connection.execute(sa.text("DROP INDEX IF EXISTS synapscale_db.idx_user_subscriptions_user_id"))
    connection.execute(sa.text("DROP INDEX IF EXISTS synapscale_db.idx_plans_is_active"))
    connection.execute(sa.text("DROP INDEX IF EXISTS synapscale_db.idx_plans_type"))
    connection.execute(sa.text("DROP INDEX IF EXISTS synapscale_db.idx_workspaces_type"))
    
    # Remover tabelas
    connection.execute(sa.text("DROP TABLE IF EXISTS synapscale_db.user_subscriptions"))
    connection.execute(sa.text("DROP TABLE IF EXISTS synapscale_db.plans"))
    
    # Remover coluna type de workspaces
    connection.execute(sa.text("ALTER TABLE synapscale_db.workspaces DROP COLUMN IF EXISTS type"))
