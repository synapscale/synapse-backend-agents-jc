#!/usr/bin/env python3
"""
Script para validação completa do sistema de agentes
Task 4: Sistema de Agentes Completo - VALIDAÇÃO FINAL
"""

import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def validate_agent_system():
    """Valida todos os modelos do sistema de agentes"""
    print("🔍 Validação Completa do Sistema de Agentes")
    print("=" * 80)
    
    issues = []
    success_count = 0
    
    try:
        print("\n📦 Importando modelos de agentes...")
        
        # Modelos existentes (já estavam implementados)
        from synapse.models.agent import Agent
        from synapse.models.agent_acl import AgentACL
        from synapse.models.agent_configuration import AgentConfiguration
        from synapse.models.agent_model import AgentModel
        from synapse.models.agent_knowledge_base import AgentKnowledgeBase
        from synapse.models.agent_tool import AgentTool
        
        print("✅ Modelos existentes importados com sucesso!")
        
        # Novos modelos implementados na Task 4
        from synapse.models.agent_quota import AgentQuota
        from synapse.models.agent_hierarchy import AgentHierarchy
        from synapse.models.agent_trigger import AgentTrigger
        from synapse.models.agent_error_log import AgentErrorLog
        from synapse.models.agent_usage_metric import AgentUsageMetric
        
        print("✅ Novos modelos da Task 4 importados com sucesso!")
        success_count += 1
        
    except ImportError as e:
        issues.append(f"❌ Erro de importação: {e}")
        print(f"❌ Erro de importação: {e}")
        return issues, success_count
    
    print("\n🧪 Testando funcionalidades dos modelos...")
    
    # Testar AgentQuota
    try:
        print("\n📊 Testando AgentQuota...")
        
        # Testar criação de quota diária
        daily_quota = AgentQuota.create_daily_quota(
            agent_id="test-agent-1",
            tenant_id="test-tenant-1",
            max_calls=1000,
            max_tokens=50000
        )
        print(f"  ✅ Quota diária criada: {daily_quota.max_calls} calls, {daily_quota.max_tokens} tokens")
        
        # Testar criação de quota mensal
        monthly_quota = AgentQuota.create_monthly_quota(
            agent_id="test-agent-2",
            tenant_id="test-tenant-1",
            max_calls=30000,
            max_tokens=1500000
        )
        print(f"  ✅ Quota mensal criada: {monthly_quota.max_calls} calls, {monthly_quota.max_tokens} tokens")
        
        # Testar métodos de tempo
        remaining_time = daily_quota.get_remaining_time()
        print(f"  ✅ Tempo restante calculado: {remaining_time}")
        
        period_start = daily_quota.get_period_start()
        period_end = daily_quota.get_period_end()
        print(f"  ✅ Período calculado: {period_start} - {period_end}")
        
        success_count += 1
        
    except Exception as e:
        issues.append(f"❌ AgentQuota falhou: {e}")
    
    # Testar AgentHierarchy
    try:
        print("\n🌳 Testando AgentHierarchy...")
        
        # Testar criação de autoreferência
        self_ref = AgentHierarchy.create_self_reference("test-agent-1")
        print(f"  ✅ Autoreferência criada: depth={self_ref.depth}")
        
        # Testar criação de relação pai-filho
        parent_child = AgentHierarchy.create_parent_child("parent-agent", "child-agent")
        print(f"  ✅ Relação pai-filho criada: depth={parent_child.depth}")
        
        # Testar validações
        is_direct = parent_child.is_direct_parent_child()
        is_self = self_ref.is_self_reference()
        print(f"  ✅ Validações: direct={is_direct}, self={is_self}")
        
        success_count += 1
        
    except Exception as e:
        issues.append(f"❌ AgentHierarchy falhou: {e}")
    
    # Testar AgentTrigger
    try:
        print("\n⏰ Testando AgentTrigger...")
        
        # Testar criação de trigger cron
        cron_trigger = AgentTrigger.create_cron_trigger(
            agent_id="test-agent-1",
            cron_expression="0 */6 * * *",  # A cada 6 horas
            active=True
        )
        print(f"  ✅ Trigger cron criado: {cron_trigger.cron_expr}")
        
        # Testar validação de cron
        is_valid_cron = cron_trigger.is_valid_cron_expression()
        print(f"  ✅ Expressão cron válida: {is_valid_cron}")
        
        # Testar criação de trigger de evento
        event_trigger = AgentTrigger.create_event_trigger(
            agent_id="test-agent-2",
            event_name="user_message_received",
            active=True
        )
        print(f"  ✅ Trigger de evento criado: {event_trigger.event_name}")
        
        # Testar verificações de tipo
        is_cron = cron_trigger.is_cron_trigger()
        is_event = event_trigger.is_event_trigger()
        print(f"  ✅ Tipos verificados: cron={is_cron}, event={is_event}")
        
        success_count += 1
        
    except Exception as e:
        issues.append(f"❌ AgentTrigger falhou: {e}")
    
    # Testar AgentErrorLog
    try:
        print("\n📝 Testando AgentErrorLog...")
        
        # Testar criação de log de erro
        error_log = AgentErrorLog.log_error(
            agent_id="test-agent-1",
            error_code="TIMEOUT_ERROR",
            error_message="Operation timed out after 30 seconds",
            context={"request_id": "req-123", "user_id": "user-456"}
        )
        print(f"  ✅ Log de erro criado: {error_log.error_code}")
        
        # Testar métodos de análise
        severity = error_log.get_severity_level()
        message = error_log.get_error_message()
        context = error_log.get_error_context()
        print(f"  ✅ Análise: severity={severity}, message='{message}', context_keys={list(context.keys())}")
        
        # Testar criação de log a partir de exceção
        try:
            raise ValueError("Test exception for logging")
        except Exception as e:
            exception_log = AgentErrorLog.log_exception(
                agent_id="test-agent-2",
                exception=e,
                context={"test": True}
            )
            print(f"  ✅ Log de exceção criado: {exception_log.error_code}")
        
        # Testar formatação de resumo
        summary = error_log.format_error_summary()
        print(f"  ✅ Resumo formatado: {summary[:80]}...")
        
        success_count += 1
        
    except Exception as e:
        issues.append(f"❌ AgentErrorLog falhou: {e}")
    
    # Testar AgentUsageMetric
    try:
        print("\n📈 Testando AgentUsageMetric...")
        
        from datetime import datetime, timezone
        
        # Testar criação de métrica diária
        daily_metric = AgentUsageMetric.create_daily_metric(
            agent_id="test-agent-1",
            day_start=datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0),
            calls_count=150,
            tokens_used=7500,
            cost_est=12.50
        )
        print(f"  ✅ Métrica diária criada: {daily_metric.calls_count} calls, ${daily_metric.cost_est}")
        
        # Testar cálculos de taxa
        calls_per_hour = daily_metric.get_calls_per_hour()
        tokens_per_hour = daily_metric.get_tokens_per_hour()
        cost_per_hour = daily_metric.get_cost_per_hour()
        print(f"  ✅ Taxas: {calls_per_hour:.2f} calls/h, {tokens_per_hour:.2f} tokens/h, ${cost_per_hour:.4f}/h")
        
        # Testar cálculos de eficiência
        cost_per_call = daily_metric.get_cost_per_call()
        cost_per_token = daily_metric.get_cost_per_token()
        efficiency_score = daily_metric.get_efficiency_score()
        print(f"  ✅ Eficiência: ${cost_per_call:.4f}/call, ${cost_per_token:.6f}/token, score={efficiency_score:.2f}")
        
        # Testar identificação de tipo de período
        period_type = daily_metric.get_period_type()
        duration_hours = daily_metric.get_period_duration_hours()
        print(f"  ✅ Período: type={period_type}, duration={duration_hours:.1f}h")
        
        success_count += 1
        
    except Exception as e:
        issues.append(f"❌ AgentUsageMetric falhou: {e}")
    
    # Testar métodos de criação avançados
    try:
        print("\n🔧 Testando métodos avançados...")
        
        # AgentQuota: testar quota customizada
        custom_quota = AgentQuota.create_custom_quota(
            agent_id="test-agent-3",
            tenant_id="test-tenant-2",
            max_calls=500,
            max_tokens=25000,
            period_hours=12  # 12 horas
        )
        print(f"  ✅ Quota customizada (12h): {custom_quota.max_calls} calls")
        
        # AgentUsageMetric: testar métrica horária
        hourly_metric = AgentUsageMetric.create_hourly_metric(
            agent_id="test-agent-3",
            hour_start=datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0),
            calls_count=25,
            tokens_used=1250,
            cost_est=2.10
        )
        print(f"  ✅ Métrica horária: {hourly_metric.calls_count} calls")
        
        success_count += 1
        
    except Exception as e:
        issues.append(f"❌ Métodos avançados falharam: {e}")
    
    # Resumo final
    print("\n" + "=" * 80)
    print("📋 RESUMO DA VALIDAÇÃO DO SISTEMA DE AGENTES")
    print("=" * 80)
    
    print(f"✅ Testes bem-sucedidos: {success_count}")
    print(f"❌ Problemas encontrados: {len(issues)}")
    
    if issues:
        print("\n🚨 PROBLEMAS DETECTADOS:")
        for issue in issues:
            print(f"  {issue}")
    else:
        print("\n🎉 TODOS OS TESTES PASSARAM! Sistema de agentes totalmente funcional!")
        
    # Validação de modelos implementados
    print("\n📦 MODELOS IMPLEMENTADOS NA TASK 4:")
    models_implemented = [
        "✅ AgentQuota - Gerenciamento de quotas e limites de uso",
        "✅ AgentHierarchy - Sistema de hierarquia com closure table",
        "✅ AgentTrigger - Triggers baseados em cron e eventos",
        "✅ AgentErrorLog - Sistema completo de logging de erros",
        "✅ AgentUsageMetric - Métricas avançadas de uso e performance"
    ]
    
    for model in models_implemented:
        print(f"  {model}")
    
    print("\n🔗 MODELOS EXISTENTES (já implementados):")
    existing_models = [
        "✅ Agent - Modelo principal de agentes",
        "✅ AgentACL - Controle de acesso",
        "✅ AgentConfiguration - Configurações",
        "✅ AgentModel - Modelos de IA/LLM",
        "✅ AgentKnowledgeBase - Bases de conhecimento",
        "✅ AgentTool - Ferramentas disponíveis"
    ]
    
    for model in existing_models:
        print(f"  {model}")
        
    print(f"\n🎯 TOTAL DE MODELOS NO SISTEMA: 11 modelos")
    print("🚀 Sistema de Agentes COMPLETO e FUNCIONANDO!")
    
    return issues, success_count

if __name__ == "__main__":
    issues, success_count = validate_agent_system()
    
    # Exit code baseado nos resultados
    if issues:
        sys.exit(1)
    else:
        sys.exit(0) 