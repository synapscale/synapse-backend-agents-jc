#!/usr/bin/env python3
"""
Teste rápido para verificar se o sistema de agents está funcionando
"""

import os
import sys

# Configurar variáveis de ambiente mínimas para teste
os.environ.setdefault("SECRET_KEY", "test-key-123")
os.environ.setdefault("JWT_SECRET_KEY", "test-jwt-key-123")
os.environ.setdefault("DATABASE_URL", "postgresql://test:test@localhost/test")

# Adicionar src ao path
sys.path.insert(0, "src")


def test_imports():
    """Testa se todos os imports estão funcionando"""
    try:
        # Testar models
        from synapse.models.agent import Agent
        from synapse.models.agent_tools import AgentTool
        from synapse.models.agent_models import AgentModel
        from synapse.models.agent_configurations import AgentConfiguration
        from synapse.models.agent_acl import AgentACL
        from synapse.models.agent_error_logs import AgentErrorLog
        from synapse.models.agent_hierarchy import AgentHierarchy
        from synapse.models.agent_kbs import AgentKB
        from synapse.models.agent_quotas import AgentQuota
        from synapse.models.agent_triggers import AgentTrigger, TriggerType
        from synapse.models.agent_usage_metrics import AgentUsageMetric

        print("✅ Todos os models de agents importados com sucesso!")

        # Testar schemas
        from synapse.schemas.agent_tools import AgentToolCreate, AgentToolResponse
        from synapse.schemas.agent_models import AgentModelCreate, AgentModelResponse
        from synapse.schemas.agent_configurations import (
            AgentConfigurationCreate,
            AgentConfigurationResponse,
        )
        from synapse.schemas.agent_acl import AgentACLCreate, AgentACLResponse
        from synapse.schemas.agent_error_logs import (
            AgentErrorLogCreate,
            AgentErrorLogResponse,
        )
        from synapse.schemas.agent_hierarchy import (
            AgentHierarchyCreate,
            AgentHierarchyResponse,
        )
        from synapse.schemas.agent_kbs import AgentKBCreate, AgentKBResponse
        from synapse.schemas.agent_quotas import AgentQuotaCreate, AgentQuotaResponse
        from synapse.schemas.agent_triggers import (
            AgentTriggerCreate,
            AgentTriggerResponse,
        )
        from synapse.schemas.agent_usage_metrics import (
            AgentUsageMetricResponse,
            AgentUsageMetricSummary,
        )

        print("✅ Todos os schemas de agents importados com sucesso!")

        return True

    except Exception as e:
        print(f"❌ Erro no import: {e}")
        return False


def test_enums():
    """Testa se os enums estão funcionando"""
    try:
        from synapse.models.agent_triggers import TriggerType
        from synapse.schemas.agent_triggers import TriggerTypeEnum

        # Verificar valores dos enums
        assert TriggerType.SCHEDULE.value == "schedule"
        assert TriggerType.EVENT.value == "event"
        assert TriggerType.WEBHOOK.value == "webhook"

        assert TriggerTypeEnum.SCHEDULE == "schedule"
        assert TriggerTypeEnum.EVENT == "event"
        assert TriggerTypeEnum.WEBHOOK == "webhook"

        print("✅ Enums funcionando corretamente!")
        return True

    except Exception as e:
        print(f"❌ Erro nos enums: {e}")
        return False


def test_schemas_validation():
    """Testa se os schemas Pydantic estão validando corretamente"""
    try:
        from synapse.schemas.agent_tools import AgentToolCreate
        from uuid import uuid4

        # Teste de validação com dados corretos
        valid_data = AgentToolCreate(tool_id=uuid4(), config={"param1": "value1"})
        assert valid_data.tool_id is not None
        assert valid_data.config == {"param1": "value1"}

        print("✅ Validação de schemas funcionando!")
        return True

    except Exception as e:
        print(f"❌ Erro na validação de schemas: {e}")
        return False


def main():
    """Executa todos os testes"""
    print("🧪 Iniciando testes do sistema de agents...")

    all_passed = True

    all_passed &= test_imports()
    all_passed &= test_enums()
    all_passed &= test_schemas_validation()

    if all_passed:
        print(
            "\n🎉 TODOS OS TESTES PASSARAM! Sistema de agents está funcionando corretamente."
        )
        return 0
    else:
        print("\n❌ ALGUNS TESTES FALHARAM! Verifique os erros acima.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
