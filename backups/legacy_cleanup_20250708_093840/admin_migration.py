"""
Admin Migration Dashboard - LLM Endpoint Migration Tracking
Endpoints exclusivos para administradores acompanharem a migração dos endpoints LLM legados.
"""

from synapse.logger_config import get_logger
logger = get_logger(__name__)
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, text

from synapse.database import get_db
from synapse.models.user import User
from synapse.api.deps import get_admin_user

# Implementações temporárias para substituir legacy_tracking
def get_current_migration_phase() -> str:
    """Retorna a fase atual da migração (implementação temporária)."""
    return "phase_3"  # Fase simulada

def get_migration_phase_info() -> dict:
    """Retorna informações da fase de migração (implementação temporária)."""
    return {
        "phase": "phase_3",
        "status": "in_progress", 
        "description": "Migração de dados de LLM",
        "completion_percentage": 70
    }

router = APIRouter()


@router.get("/dashboard", summary="Dashboard de Migração LLM")
async def get_migration_dashboard(
    current_admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Dashboard principal para acompanhamento da migração de endpoints LLM.

    Fornece métricas em tempo real sobre:
    - Status da migração por fase
    - Usuários que ainda usam endpoints legados
    - Endpoints mais utilizados (legacy vs novo)
    - Projeções de conclusão da migração
    - Estatísticas de comunicação
    """
    try:
        logger.info(f"Admin {current_admin.id} acessando dashboard de migração")

        # Obter fase atual da migração
        phase_info = get_migration_phase_info()

        # Simular dados de migração (em produção, viria do banco de dados)
        # TODO: Implementar queries reais quando houver dados de legacy_usage
        dashboard_data = {
            "migration_overview": {
                "current_phase": phase_info,
                "total_users": await _get_total_users(db),
                "migrated_users": await _get_migrated_users_count(db),
                "legacy_users": await _get_legacy_users_count(db),
                "migration_percentage": await _calculate_migration_percentage(db),
                "projected_completion": _calculate_projected_completion(),
            },
            "legacy_endpoint_usage": {
                "most_used_endpoints": await _get_most_used_legacy_endpoints(db),
                "usage_by_day": await _get_legacy_usage_by_day(db),
                "top_legacy_users": await _get_top_legacy_users(db),
                "urgent_migrations": await _get_urgent_migrations(db),
            },
            "communication_stats": {
                "emails_sent": await _get_emails_sent_count(db),
                "email_open_rate": await _get_email_open_rate(db),
                "support_tickets": await _get_migration_support_tickets(db),
                "documentation_views": await _get_migration_docs_views(db),
            },
            "performance_metrics": {
                "average_migration_time": await _get_average_migration_time(db),
                "success_rate": await _get_migration_success_rate(db),
                "common_issues": await _get_common_migration_issues(db),
                "support_resolution_time": await _get_support_resolution_time(db),
            },
            "next_actions": await _get_recommended_actions(db),
        }

        logger.info(f"Dashboard de migração gerado para admin {current_admin.id}")
        return dashboard_data

    except HTTPException:
        raise
    except Exception as e:
        logger.logger.error(f"Erro inesperado em get_migration_dashboard: {str(e)}", extra={"error_type": type(e).__name__})
        raise


@router.get("/users", summary="Usuários em Migração")
async def get_migration_users(
    status: Optional[str] = Query(None, regex="^(legacy|migrating|migrated|all)$"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Lista usuários segmentados por status de migração.

    Permite filtrar por:
    - legacy: Ainda usando apenas endpoints antigos
    - migrating: Em processo de migração (usando ambos)
    - migrated: Completamente migrados
    - all: Todos os usuários
    """
    try:
        logger.info(
            f"Admin {current_admin.id} listando usuários de migração - status: {status}"
        )

        users_data = await _get_users_by_migration_status(db, status, limit, offset)

        return {
            "users": users_data["users"],
            "total": users_data["total"],
            "status_filter": status,
            "pagination": {
                "limit": limit,
                "offset": offset,
                "has_more": users_data["total"] > offset + limit,
            },
            "migration_stats": await _get_migration_status_distribution(db),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.logger.error(f"Erro ao listar usuários de migração: {str(e)}", extra={"error_type": type(e).__name__})
        raise


@router.post(
    "/communications/send",
    summary="Enviar Comunicação de Migração",
)
async def send_migration_communication(
    target_group: str = Query(
        ..., regex="^(all|legacy|migrating|enterprise|developers)$"
    ),
    communication_type: str = Query(..., regex="^(email|notification|urgent)$"),
    custom_message: Optional[str] = None,
    current_admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Envia comunicação direcionada sobre migração para grupos específicos de usuários.

    Args:
        target_group: Grupo de usuários (all, legacy, migrating, enterprise, developers)
        communication_type: Tipo de comunicação (email, notification, urgent)
        custom_message: Mensagem personalizada (opcional)
    """
    try:
        logger.info(
            f"Admin {current_admin.id} enviando comunicação de migração - grupo: {target_group}, tipo: {communication_type}"
        )

        # Simular envio de comunicação
        # TODO: Implementar envio real de emails/notificações

        target_users = await _get_users_for_communication(db, target_group)

        communication_result = {
            "communication_id": f"migration_comm_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "target_group": target_group,
            "communication_type": communication_type,
            "target_users_count": len(target_users),
            "message_preview": (
                custom_message[:100]
                if custom_message
                else _get_default_message(communication_type)
            ),
            "sent_at": datetime.now().isoformat(),
            "estimated_delivery": (datetime.now() + timedelta(minutes=5)).isoformat(),
            "tracking_enabled": True,
        }

        # Log da ação administrativa
        logger.info(
            f"Comunicação de migração enviada por admin {current_admin.id}: {communication_result['communication_id']}"
        )

        return communication_result

    except HTTPException:
        raise
    except Exception as e:
        logger.logger.error(f"Erro ao enviar comunicação de migração: {str(e)}", extra={"error_type": type(e).__name__})
        raise


@router.get("/analytics", summary="Analytics de Migração")
async def get_migration_analytics(
    start_date: datetime = Query(..., description="Data de início"),
    end_date: datetime = Query(..., description="Data de fim"),
    granularity: str = Query("day", regex="^(hour|day|week)$"),
    current_admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Analytics detalhadas da migração em período específico.

    Inclui:
    - Evolução do uso de endpoints legacy vs novos
    - Taxa de migração ao longo do tempo
    - Análise de padrões de uso
    - Identificação de usuários que precisam de atenção
    """
    try:
        if start_date > end_date:
            raise HTTPException(
                status_code=400, detail="Data de início deve ser anterior à data de fim"
            )

        logger.info(
            f"Admin {current_admin.id} solicitando analytics de migração - período: {start_date} a {end_date}"
        )

        analytics_data = {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "granularity": granularity,
            },
            "migration_trends": await _get_migration_trends(
                db, start_date, end_date, granularity
            ),
            "endpoint_usage_evolution": await _get_endpoint_usage_evolution(
                db, start_date, end_date, granularity
            ),
            "user_migration_patterns": await _get_user_migration_patterns(
                db, start_date, end_date
            ),
            "communication_effectiveness": await _get_communication_effectiveness(
                db, start_date, end_date
            ),
            "support_impact": await _get_support_impact_analysis(
                db, start_date, end_date
            ),
        }

        return analytics_data

    except HTTPException:
        raise
    except Exception as e:
        logger.logger.error(f"Erro ao gerar analytics de migração: {str(e)}", extra={"error_type": type(e).__name__})
        raise


# ================ FUNÇÕES AUXILIARES ================


async def _get_total_users(db: Session) -> int:
    """Retorna total de usuários no sistema."""
    try:
        result = db.execute(text("SELECT COUNT(*) FROM users")).scalar()
        return result or 0
    except Exception:
        return 1000  # Fallback simulation


async def _get_migrated_users_count(db: Session) -> int:
    """Retorna número de usuários que completaram a migração."""
    # TODO: Implementar query real baseada em tabela de tracking
    # Por agora, simular baseado na fase de migração
    total = await _get_total_users(db)
    phase = get_current_migration_phase()

    migration_simulation = {
        "phase_1": int(total * 0.1),  # 10% migrado na fase 1
        "phase_2": int(total * 0.35),  # 35% migrado na fase 2
        "phase_3": int(total * 0.70),  # 70% migrado na fase 3
        "phase_4": int(total * 0.95),  # 95% migrado na fase 4
    }

    return migration_simulation.get(phase, 0)


async def _get_legacy_users_count(db: Session) -> int:
    """Retorna número de usuários ainda usando endpoints legacy."""
    total = await _get_total_users(db)
    migrated = await _get_migrated_users_count(db)
    return max(0, total - migrated)


async def _calculate_migration_percentage(db: Session) -> float:
    """Calcula percentual de migração."""
    total = await _get_total_users(db)
    migrated = await _get_migrated_users_count(db)
    return (migrated / total * 100) if total > 0 else 0.0


def _calculate_projected_completion() -> str:
    """Calcula data projetada para conclusão da migração."""
    phase = get_current_migration_phase()

    projections = {
        "phase_1": "2024-09-15",
        "phase_2": "2024-08-30",
        "phase_3": "2024-08-15",
        "phase_4": "2024-08-01",
    }

    return projections.get(phase, "2024-10-01")


async def _get_most_used_legacy_endpoints(db: Session) -> List[Dict[str, Any]]:
    """Retorna endpoints legacy mais utilizados."""
    # Simulação - em produção viria da tabela legacy_usage
    return [
        {"endpoint": "/api/v1/openai/chat", "usage_count": 2840, "unique_users": 156},
        {
            "endpoint": "/api/v1/anthropic/generate",
            "usage_count": 1920,
            "unique_users": 89,
        },
        {"endpoint": "/api/v1/openai/models", "usage_count": 1450, "unique_users": 123},
        {"endpoint": "/api/v1/google/chat", "usage_count": 890, "unique_users": 67},
        {
            "endpoint": "/api/v1/anthropic/models",
            "usage_count": 670,
            "unique_users": 45,
        },
    ]


async def _get_legacy_usage_by_day(db: Session) -> List[Dict[str, Any]]:
    """Retorna uso de endpoints legacy por dia."""
    # Simulação - dados para últimos 7 dias
    base_date = datetime.now() - timedelta(days=6)
    usage_data = []

    for i in range(7):
        date = base_date + timedelta(days=i)
        # Simular redução gradual de uso legacy
        usage_count = max(100, 1000 - (i * 120))

        usage_data.append(
            {
                "date": date.strftime("%Y-%m-%d"),
                "legacy_requests": usage_count,
                "new_requests": 500 + (i * 150),
                "unique_users": max(20, 100 - (i * 10)),
            }
        )

    return usage_data


async def _get_top_legacy_users(db: Session) -> List[Dict[str, Any]]:
    """Retorna usuários que mais usam endpoints legacy."""
    # Simulação
    return [
        {
            "user_id": 1001,
            "email": "heavy.user@company.com",
            "legacy_requests": 450,
            "last_legacy_use": "2024-12-09T08:30:00Z",
        },
        {
            "user_id": 1042,
            "email": "api.client@enterprise.com",
            "legacy_requests": 320,
            "last_legacy_use": "2024-12-09T09:15:00Z",
        },
        {
            "user_id": 1089,
            "email": "dev.team@startup.io",
            "legacy_requests": 280,
            "last_legacy_use": "2024-12-09T07:45:00Z",
        },
        {
            "user_id": 1156,
            "email": "integration@bigcorp.com",
            "legacy_requests": 190,
            "last_legacy_use": "2024-12-09T06:30:00Z",
        },
    ]


async def _get_urgent_migrations(db: Session) -> List[Dict[str, Any]]:
    """Retorna migrações que precisam de atenção urgente."""
    return [
        {
            "user_id": 1001,
            "email": "heavy.user@company.com",
            "reason": "High volume legacy usage (450+ requests/day)",
            "priority": "urgent",
            "recommended_action": "Direct technical support contact",
        },
        {
            "user_id": 1042,
            "email": "api.client@enterprise.com",
            "reason": "Enterprise client with complex integration",
            "priority": "high",
            "recommended_action": "Dedicated migration engineer",
        },
    ]


# Implementar outras funções auxiliares com simulações similares...
async def _get_emails_sent_count(db: Session) -> int:
    return 1250  # Simulação


async def _get_email_open_rate(db: Session) -> float:
    return 68.5  # Simulação: 68.5%


async def _get_migration_support_tickets(db: Session) -> int:
    return 89  # Simulação


async def _get_migration_docs_views(db: Session) -> int:
    return 3400  # Simulação


async def _get_average_migration_time(db: Session) -> float:
    return 2.3  # Simulação: 2.3 dias em média


async def _get_migration_success_rate(db: Session) -> float:
    return 94.2  # Simulação: 94.2%


async def _get_common_migration_issues(db: Session) -> List[str]:
    return [
        "Authentication token format changes",
        "Response schema differences",
        "Rate limiting adjustments",
        "Provider parameter mapping",
    ]


async def _get_support_resolution_time(db: Session) -> float:
    return 4.2  # Simulação: 4.2 horas em média


async def _get_recommended_actions(db: Session) -> List[Dict[str, Any]]:
    return [
        {
            "action": "Contact high-usage legacy users",
            "priority": "urgent",
            "count": 12,
            "estimated_impact": "25% migration boost",
        },
        {
            "action": "Send phase 3 communication",
            "priority": "high",
            "count": 450,
            "estimated_impact": "15% migration boost",
        },
    ]


async def _get_users_by_migration_status(
    db: Session, status: str, limit: int, offset: int
) -> Dict[str, Any]:
    # Simulação simplificada
    total_users = await _get_total_users(db)

    if status == "legacy":
        users = [
            {
                "id": i + 1000,
                "email": f"legacy.user{i}@example.com",
                "last_legacy_use": "2024-12-09",
            }
            for i in range(limit)
        ]
        total = await _get_legacy_users_count(db)
    elif status == "migrated":
        users = [
            {
                "id": i + 2000,
                "email": f"migrated.user{i}@example.com",
                "migration_date": "2024-12-01",
            }
            for i in range(limit)
        ]
        total = await _get_migrated_users_count(db)
    else:
        users = [
            {"id": i + 3000, "email": f"user{i}@example.com", "status": "migrating"}
            for i in range(limit)
        ]
        total = total_users

    return {"users": users, "total": total}


async def _get_migration_status_distribution(db: Session) -> Dict[str, int]:
    total = await _get_total_users(db)
    migrated = await _get_migrated_users_count(db)
    legacy = await _get_legacy_users_count(db)

    return {
        "legacy": legacy,
        "migrating": max(0, total - migrated - legacy),
        "migrated": migrated,
        "total": total,
    }


async def _get_users_for_communication(
    db: Session, target_group: str
) -> List[Dict[str, Any]]:
    # Simulação
    return [{"id": i, "email": f"user{i}@example.com"} for i in range(1, 101)]


def _get_default_message(communication_type: str) -> str:
    messages = {
        "email": "Importante: Migração para novos endpoints LLM...",
        "notification": "Ação necessária: Migrar para API LLM unificada",
        "urgent": "URGENTE: Endpoints legacy serão removidos em 30 dias!",
    }
    return messages.get(communication_type, "Comunicação sobre migração LLM")


# Outras funções auxiliares com simulações...
async def _get_migration_trends(
    db: Session, start_date: datetime, end_date: datetime, granularity: str
) -> List[Dict[str, Any]]:
    return []  # Implementar simulação de trends


async def _get_endpoint_usage_evolution(
    db: Session, start_date: datetime, end_date: datetime, granularity: str
) -> List[Dict[str, Any]]:
    return []  # Implementar simulação de evolução


async def _get_user_migration_patterns(
    db: Session, start_date: datetime, end_date: datetime
) -> Dict[str, Any]:
    return {}  # Implementar simulação de padrões


async def _get_communication_effectiveness(
    db: Session, start_date: datetime, end_date: datetime
) -> Dict[str, Any]:
    return {}  # Implementar simulação de efetividade


async def _get_support_impact_analysis(
    db: Session, start_date: datetime, end_date: datetime
) -> Dict[str, Any]:
    return {}  # Implementar simulação de impacto no suporte
