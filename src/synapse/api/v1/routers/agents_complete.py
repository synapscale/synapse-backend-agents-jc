"""
Router consolidado para todos os endpoints de agents
Inclui tabelas principais e especializadas
"""

from fastapi import APIRouter
from synapse.api.v1.endpoints import (
    agents,
    agent_tools,
    agent_models,
    agent_configurations,
    agent_advanced,
)

# Router principal para agents
agents_router = APIRouter()

# Incluir endpoints principais (tabela agents)
agents_router.include_router(
    agents.router,
    prefix="/agents",
    tags=["agents"],
)

# Incluir endpoints especializados
agents_router.include_router(
    agent_tools.router,
    prefix="/agents",
    tags=["agent-tools"],
)
agents_router.include_router(
    agent_models.router,
    prefix="/agents",
    tags=["agent-models"],
)
agents_router.include_router(
    agent_configurations.router,
    prefix="/agents",
    tags=["agent-configurations"],
)
agents_router.include_router(
    agent_advanced.router,
    prefix="/agents",
    tags=["agent-advanced"],
)
