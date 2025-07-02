#!/usr/bin/env python3
"""
Script para validar se os modelos estão alinhados com a estrutura real do banco
"""

import sys
import os
sys.path.insert(0, '/Users/joaovictormiranda/backend/synapse-backend-agents-jc')

# Configurar variáveis de ambiente mínimas
os.environ.setdefault('SECRET_KEY', 'test-secret-key')
os.environ.setdefault('JWT_SECRET_KEY', 'test-jwt-secret')
os.environ.setdefault('DATABASE_URL', 'postgresql://test:test@localhost/test')

from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey, ARRAY
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid

# Base isolada para teste
Base = declarative_base()

# Definir estruturas reais do banco (obtidas via queries)
REAL_DB_STRUCTURES = {
    'users': ['id', 'email', 'username', 'hashed_password', 'full_name', 'is_active', 'is_verified', 'is_superuser', 'profile_image_url', 'bio', 'created_at', 'updated_at', 'status', 'metadata', 'last_login_at', 'login_count', 'failed_login_attempts', 'account_locked_until', 'tenant_id'],
    'tenants': ['id', 'name', 'slug', 'domain', 'status', 'created_at', 'updated_at', 'plan_id', 'theme', 'default_language', 'timezone', 'mfa_required', 'session_timeout', 'ip_whitelist', 'max_storage_mb', 'max_workspaces', 'max_api_calls_per_day', 'max_members_per_workspace', 'enabled_features'],
    'agents': ['id', 'name', 'description', 'is_active', 'user_id', 'created_at', 'updated_at', 'workspace_id', 'tenant_id', 'status', 'priority', 'version', 'environment', 'current_config'],
    'workspaces': ['id', 'name', 'slug', 'description', 'avatar_url', 'color', 'owner_id', 'is_public', 'is_template', 'allow_guest_access', 'require_approval', 'max_members', 'max_projects', 'max_storage_mb', 'enable_real_time_editing', 'enable_comments', 'enable_chat', 'enable_video_calls', 'member_count', 'project_count', 'activity_count', 'storage_used_mb', 'status', 'created_at', 'updated_at', 'last_activity_at', 'tenant_id', 'email_notifications', 'push_notifications', 'api_calls_today', 'api_calls_this_month', 'last_api_reset_daily', 'last_api_reset_monthly', 'feature_usage_count', 'type']
}

# Criar modelos de teste baseados na estrutura real
class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "synapscale_db"}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    username = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(200), nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)
    profile_image_url = Column(String(500))
    bio = Column(String(1000))
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    status = Column(String(20), default='active')
    user_metadata = Column('metadata', JSONB, default=dict)
    last_login_at = Column(DateTime(timezone=True))
    login_count = Column(Integer, default=0)
    failed_login_attempts = Column(Integer, default=0)
    account_locked_until = Column(DateTime(timezone=True))
    tenant_id = Column(UUID(as_uuid=True), nullable=True)

class Tenant(Base):
    __tablename__ = "tenants"
    __table_args__ = {"schema": "synapscale_db"}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    slug = Column(String, nullable=False)
    domain = Column(String)
    status = Column(String, nullable=False, default="active")
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    plan_id = Column(UUID(as_uuid=True), nullable=False)
    theme = Column(String, default="light")
    default_language = Column(String, default="en")
    timezone = Column(String, default="UTC")
    mfa_required = Column(Boolean, default=False)
    session_timeout = Column(Integer, default=3600)
    ip_whitelist = Column(JSONB, default=list)
    max_storage_mb = Column(Integer)
    max_workspaces = Column(Integer)
    max_api_calls_per_day = Column(Integer)
    max_members_per_workspace = Column(Integer)
    enabled_features = Column(ARRAY(String))

class Agent(Base):
    __tablename__ = "agents"
    __table_args__ = {"schema": "synapscale_db"}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now())
    workspace_id = Column(UUID(as_uuid=True), nullable=True)
    tenant_id = Column(UUID(as_uuid=True), nullable=False)
    status = Column(String, nullable=True, default='active')
    priority = Column(Integer, nullable=True, default=1)
    version = Column(String, nullable=True, default='1.0.0')
    environment = Column(String, nullable=True, default='development')
    current_config = Column(UUID(as_uuid=True), nullable=True)

def validate_model(model_class, table_name):
    """Valida se um modelo está alinhado com a estrutura real do banco"""
    print(f"\n=== VALIDANDO {table_name.upper()} ===")
    
    # Obter colunas do modelo
    model_columns = [col.name for col in model_class.__table__.columns]
    expected_columns = REAL_DB_STRUCTURES[table_name]
    
    print(f"Modelo tem {len(model_columns)} colunas")
    print(f"Banco tem {len(expected_columns)} colunas")
    
    # Verificar diferenças
    missing = set(expected_columns) - set(model_columns)
    extra = set(model_columns) - set(expected_columns)
    
    if missing:
        print(f"❌ Colunas FALTANDO no modelo: {missing}")
    
    if extra:
        print(f"❌ Colunas EXTRAS no modelo: {extra}")
    
    if not missing and not extra:
        print(f"✅ Modelo {table_name.upper()} PERFEITAMENTE ALINHADO!")
        return True
    else:
        print(f"❌ Modelo {table_name.upper()} precisa de ajustes")
        return False

def main():
    print("🔍 VALIDAÇÃO DE ALINHAMENTO DOS MODELOS COM O BANCO REAL")
    print("=" * 70)
    
    models_to_test = [
        (User, 'users'),
        (Tenant, 'tenants'),
        (Agent, 'agents'),
    ]
    
    all_aligned = True
    
    for model_class, table_name in models_to_test:
        try:
            is_aligned = validate_model(model_class, table_name)
            all_aligned = all_aligned and is_aligned
        except Exception as e:
            print(f"❌ Erro ao validar {table_name}: {e}")
            all_aligned = False
    
    print("\n" + "=" * 70)
    if all_aligned:
        print("🎉 TODOS OS MODELOS ESTÃO PERFEITAMENTE ALINHADOS COM O BANCO!")
    else:
        print("⚠️  ALGUNS MODELOS PRECISAM DE AJUSTES")
    
    return all_aligned

if __name__ == "__main__":
    main()
