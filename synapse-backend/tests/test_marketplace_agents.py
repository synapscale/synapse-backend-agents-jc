import pytest
import httpx
import os
import json
from typing import Dict, Any

# Configurações de teste
API_URL = os.getenv("API_URL", "http://localhost:8000")
TEST_USERNAME = os.getenv("TEST_USERNAME", "testuser")
TEST_PASSWORD = os.getenv("TEST_PASSWORD", "password")

# Fixtures
@pytest.fixture
async def auth_token():
    """Obtém um token de autenticação para os testes."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_URL}/token",
            data={"username": TEST_USERNAME, "password": TEST_PASSWORD}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        return data["access_token"]

@pytest.fixture
async def auth_headers(auth_token):
    """Retorna os headers de autenticação para os testes."""
    return {"Authorization": f"Bearer {auth_token}"}

# Testes para o serviço Marketplace - Ferramentas
@pytest.mark.asyncio
async def test_list_tools(auth_headers):
    """Testa a listagem de ferramentas."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{API_URL}/api/marketplace/tools",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

@pytest.mark.asyncio
async def test_create_and_get_tool(auth_headers):
    """Testa a criação e obtenção de uma ferramenta."""
    # Dados para criação
    tool_data = {
        "name": "Ferramenta de Teste",
        "description": "Ferramenta para testes automatizados",
        "category": "test",
        "icon": "test_icon.svg",
        "config_schema": {
            "param1": {"type": "string", "required": True},
            "param2": {"type": "number", "required": False}
        }
    }
    
    # Criar ferramenta
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_URL}/api/marketplace/tools",
            headers=auth_headers,
            json=tool_data
        )
        assert response.status_code == 200
        created_tool = response.json()
        assert "id" in created_tool
        assert created_tool["name"] == tool_data["name"]
        
        # Obter ferramenta criada
        tool_id = created_tool["id"]
        response = await client.get(
            f"{API_URL}/api/marketplace/tools/{tool_id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        retrieved_tool = response.json()
        assert retrieved_tool["id"] == tool_id
        assert retrieved_tool["name"] == tool_data["name"]
        
        # Limpar - remover ferramenta
        response = await client.delete(
            f"{API_URL}/api/marketplace/tools/{tool_id}",
            headers=auth_headers
        )
        assert response.status_code == 200

@pytest.mark.asyncio
async def test_update_tool(auth_headers):
    """Testa a atualização de uma ferramenta."""
    # Criar ferramenta para teste
    tool_data = {
        "name": "Ferramenta para Atualização",
        "description": "Ferramenta para testar atualização",
        "category": "test",
        "icon": "test_icon.svg",
        "config_schema": {
            "param1": {"type": "string", "required": True}
        }
    }
    
    async with httpx.AsyncClient() as client:
        # Criar ferramenta
        response = await client.post(
            f"{API_URL}/api/marketplace/tools",
            headers=auth_headers,
            json=tool_data
        )
        assert response.status_code == 200
        created_tool = response.json()
        tool_id = created_tool["id"]
        
        # Atualizar ferramenta
        updated_data = {
            "name": "Ferramenta Atualizada",
            "description": "Descrição atualizada",
            "category": "test-updated",
            "icon": "updated_icon.svg",
            "config_schema": {
                "param1": {"type": "string", "required": True},
                "param2": {"type": "boolean", "required": False}
            }
        }
        
        response = await client.put(
            f"{API_URL}/api/marketplace/tools/{tool_id}",
            headers=auth_headers,
            json=updated_data
        )
        assert response.status_code == 200
        updated_tool = response.json()
        assert updated_tool["id"] == tool_id
        assert updated_tool["name"] == updated_data["name"]
        assert updated_tool["description"] == updated_data["description"]
        
        # Limpar - remover ferramenta
        response = await client.delete(
            f"{API_URL}/api/marketplace/tools/{tool_id}",
            headers=auth_headers
        )
        assert response.status_code == 200

# Testes para o serviço Marketplace - Personalidades
@pytest.mark.asyncio
async def test_list_personalities(auth_headers):
    """Testa a listagem de personalidades."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{API_URL}/api/marketplace/personalities",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

@pytest.mark.asyncio
async def test_create_and_get_personality(auth_headers):
    """Testa a criação e obtenção de uma personalidade."""
    # Dados para criação
    personality_data = {
        "name": "Personalidade de Teste",
        "description": "Personalidade para testes automatizados",
        "category": "test",
        "icon": "test_personality.svg",
        "prompt_template": "Você é um assistente de testes que [ACTION]."
    }
    
    # Criar personalidade
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_URL}/api/marketplace/personalities",
            headers=auth_headers,
            json=personality_data
        )
        assert response.status_code == 200
        created_personality = response.json()
        assert "id" in created_personality
        assert created_personality["name"] == personality_data["name"]
        
        # Obter personalidade criada
        personality_id = created_personality["id"]
        response = await client.get(
            f"{API_URL}/api/marketplace/personalities/{personality_id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        retrieved_personality = response.json()
        assert retrieved_personality["id"] == personality_id
        assert retrieved_personality["name"] == personality_data["name"]
        
        # Limpar - remover personalidade
        response = await client.delete(
            f"{API_URL}/api/marketplace/personalities/{personality_id}",
            headers=auth_headers
        )
        assert response.status_code == 200

# Testes para o serviço Marketplace - Presets
@pytest.mark.asyncio
async def test_list_presets(auth_headers):
    """Testa a listagem de presets."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{API_URL}/api/marketplace/presets",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

@pytest.mark.asyncio
async def test_create_and_get_preset(auth_headers):
    """Testa a criação e obtenção de um preset."""
    # Dados para criação
    preset_data = {
        "name": "Preset de Teste",
        "description": "Preset para testes automatizados",
        "category": "test",
        "icon": "test_preset.svg",
        "model": "gpt-3.5-turbo",
        "provider": "openai",
        "parameters": {
            "temperature": 0.7,
            "top_p": 0.9,
            "max_tokens": 1000
        }
    }
    
    # Criar preset
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_URL}/api/marketplace/presets",
            headers=auth_headers,
            json=preset_data
        )
        assert response.status_code == 200
        created_preset = response.json()
        assert "id" in created_preset
        assert created_preset["name"] == preset_data["name"]
        
        # Obter preset criado
        preset_id = created_preset["id"]
        response = await client.get(
            f"{API_URL}/api/marketplace/presets/{preset_id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        retrieved_preset = response.json()
        assert retrieved_preset["id"] == preset_id
        assert retrieved_preset["name"] == preset_data["name"]
        
        # Limpar - remover preset
        response = await client.delete(
            f"{API_URL}/api/marketplace/presets/{preset_id}",
            headers=auth_headers
        )
        assert response.status_code == 200

# Testes para o serviço Agents
@pytest.mark.asyncio
async def test_list_agents(auth_headers):
    """Testa a listagem de agentes."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{API_URL}/api/agents/agents",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

@pytest.mark.asyncio
async def test_create_and_get_agent(auth_headers):
    """Testa a criação e obtenção de um agente."""
    # Primeiro, criar uma ferramenta, personalidade e preset para usar no agente
    tool_data = {
        "name": "Ferramenta para Agente",
        "description": "Ferramenta para usar no teste de agente",
        "category": "test",
        "icon": "test_tool.svg",
        "config_schema": {
            "param1": {"type": "string", "required": True}
        }
    }
    
    personality_data = {
        "name": "Personalidade para Agente",
        "description": "Personalidade para usar no teste de agente",
        "category": "test",
        "icon": "test_personality.svg",
        "prompt_template": "Você é um assistente de testes que [ACTION]."
    }
    
    preset_data = {
        "name": "Preset para Agente",
        "description": "Preset para usar no teste de agente",
        "category": "test",
        "icon": "test_preset.svg",
        "model": "gpt-3.5-turbo",
        "provider": "openai",
        "parameters": {
            "temperature": 0.7,
            "max_tokens": 1000
        }
    }
    
    async with httpx.AsyncClient() as client:
        # Criar ferramenta
        response = await client.post(
            f"{API_URL}/api/marketplace/tools",
            headers=auth_headers,
            json=tool_data
        )
        assert response.status_code == 200
        created_tool = response.json()
        tool_id = created_tool["id"]
        
        # Criar personalidade
        response = await client.post(
            f"{API_URL}/api/marketplace/personalities",
            headers=auth_headers,
            json=personality_data
        )
        assert response.status_code == 200
        created_personality = response.json()
        personality_id = created_personality["id"]
        
        # Criar preset
        response = await client.post(
            f"{API_URL}/api/marketplace/presets",
            headers=auth_headers,
            json=preset_data
        )
        assert response.status_code == 200
        created_preset = response.json()
        preset_id = created_preset["id"]
        
        # Agora criar o agente
        agent_data = {
            "name": "Agente de Teste",
            "description": "Agente para testes automatizados",
            "icon": "test_agent.svg",
            "system_prompt": "Você é um agente de teste que ajuda com testes automatizados.",
            "tools": [
                {
                    "id": tool_id,
                    "parameters": {"param1": "valor_teste"}
                }
            ],
            "personality_id": personality_id,
            "preset_id": preset_id,
            "is_public": True,
            "tags": ["test", "automated"]
        }
        
        # Criar agente
        response = await client.post(
            f"{API_URL}/api/agents/agents",
            headers=auth_headers,
            json=agent_data
        )
        assert response.status_code == 200
        created_agent = response.json()
        assert "id" in created_agent
        assert created_agent["name"] == agent_data["name"]
        
        # Obter agente criado
        agent_id = created_agent["id"]
        response = await client.get(
            f"{API_URL}/api/agents/agents/{agent_id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        retrieved_agent = response.json()
        assert retrieved_agent["id"] == agent_id
        assert retrieved_agent["name"] == agent_data["name"]
        
        # Limpar - remover agente, ferramenta, personalidade e preset
        response = await client.delete(
            f"{API_URL}/api/agents/agents/{agent_id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        response = await client.delete(
            f"{API_URL}/api/marketplace/tools/{tool_id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        response = await client.delete(
            f"{API_URL}/api/marketplace/personalities/{personality_id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        response = await client.delete(
            f"{API_URL}/api/marketplace/presets/{preset_id}",
            headers=auth_headers
        )
        assert response.status_code == 200

@pytest.mark.asyncio
async def test_execute_agent(auth_headers):
    """Testa a execução de um agente."""
    # Criar um agente simples para teste
    agent_data = {
        "name": "Agente para Execução",
        "description": "Agente para testar execução",
        "icon": "test_agent.svg",
        "system_prompt": "Você é um assistente simples que responde perguntas básicas.",
        "tools": [],
        "personality_id": None,
        "preset_id": None,
        "is_public": True,
        "tags": ["test", "execution"]
    }
    
    async with httpx.AsyncClient() as client:
        # Criar agente
        response = await client.post(
            f"{API_URL}/api/agents/agents",
            headers=auth_headers,
            json=agent_data
        )
        assert response.status_code == 200
        created_agent = response.json()
        agent_id = created_agent["id"]
        
        # Executar agente
        execution_data = {
            "input": "Qual é a capital do Brasil?",
            "metadata": {"context": "test"}
        }
        
        response = await client.post(
            f"{API_URL}/api/agents/agents/{agent_id}/execute",
            headers=auth_headers,
            json=execution_data
        )
        assert response.status_code == 200
        execution = response.json()
        assert "id" in execution
        assert execution["status"] == "running"
        assert execution["input"] == execution_data["input"]
        
        # Obter resultado da execução (pode estar ainda em andamento)
        execution_id = execution["id"]
        response = await client.get(
            f"{API_URL}/api/agents/executions/{execution_id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        # Limpar - remover agente
        response = await client.delete(
            f"{API_URL}/api/agents/agents/{agent_id}",
            headers=auth_headers
        )
        assert response.status_code == 200

# Testes de integração entre serviços
@pytest.mark.asyncio
async def test_marketplace_agents_integration(auth_headers):
    """Testa a integração entre os serviços Marketplace e Agents."""
    # Criar ferramenta no Marketplace
    tool_data = {
        "name": "Ferramenta de Integração",
        "description": "Ferramenta para teste de integração",
        "category": "integration",
        "icon": "integration_tool.svg",
        "config_schema": {
            "param1": {"type": "string", "required": True}
        }
    }
    
    async with httpx.AsyncClient() as client:
        # Criar ferramenta
        response = await client.post(
            f"{API_URL}/api/marketplace/tools",
            headers=auth_headers,
            json=tool_data
        )
        assert response.status_code == 200
        created_tool = response.json()
        tool_id = created_tool["id"]
        
        # Criar agente usando a ferramenta
        agent_data = {
            "name": "Agente de Integração",
            "description": "Agente para teste de integração",
            "icon": "integration_agent.svg",
            "system_prompt": "Você é um agente de teste de integração.",
            "tools": [
                {
                    "id": tool_id,
                    "parameters": {"param1": "valor_integração"}
                }
            ],
            "is_public": True,
            "tags": ["integration", "test"]
        }
        
        response = await client.post(
            f"{API_URL}/api/agents/agents",
            headers=auth_headers,
            json=agent_data
        )
        assert response.status_code == 200
        created_agent = response.json()
        agent_id = created_agent["id"]
        
        # Verificar se a ferramenta está corretamente associada ao agente
        response = await client.get(
            f"{API_URL}/api/agents/agents/{agent_id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        retrieved_agent = response.json()
        assert len(retrieved_agent["tools"]) == 1
        assert retrieved_agent["tools"][0]["id"] == tool_id
        
        # Limpar - remover agente e ferramenta
        response = await client.delete(
            f"{API_URL}/api/agents/agents/{agent_id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        
        response = await client.delete(
            f"{API_URL}/api/marketplace/tools/{tool_id}",
            headers=auth_headers
        )
        assert response.status_code == 200

# Testes de erros e casos de borda
@pytest.mark.asyncio
async def test_not_found_errors(auth_headers):
    """Testa respostas de erro para recursos não encontrados."""
    async with httpx.AsyncClient() as client:
        # Ferramenta não existente
        response = await client.get(
            f"{API_URL}/api/marketplace/tools/tool-nonexistent",
            headers=auth_headers
        )
        assert response.status_code == 404
        
        # Personalidade não existente
        response = await client.get(
            f"{API_URL}/api/marketplace/personalities/pers-nonexistent",
            headers=auth_headers
        )
        assert response.status_code == 404
        
        # Preset não existente
        response = await client.get(
            f"{API_URL}/api/marketplace/presets/pres-nonexistent",
            headers=auth_headers
        )
        assert response.status_code == 404
        
        # Agente não existente
        response = await client.get(
            f"{API_URL}/api/agents/agents/agent-nonexistent",
            headers=auth_headers
        )
        assert response.status_code == 404
        
        # Execução não existente
        response = await client.get(
            f"{API_URL}/api/agents/executions/exec-nonexistent",
            headers=auth_headers
        )
        assert response.status_code == 404

@pytest.mark.asyncio
async def test_validation_errors(auth_headers):
    """Testa validação de dados inválidos."""
    async with httpx.AsyncClient() as client:
        # Ferramenta com dados inválidos
        invalid_tool = {
            "name": "",  # Nome vazio
            "description": "Descrição válida",
            "category": "test"
            # Faltando campos obrigatórios
        }
        
        response = await client.post(
            f"{API_URL}/api/marketplace/tools",
            headers=auth_headers,
            json=invalid_tool
        )
        assert response.status_code == 400
        
        # Agente com dados inválidos
        invalid_agent = {
            "name": "Agente Inválido",
            "description": "Descrição válida",
            # Faltando system_prompt obrigatório
            "tools": [
                {
                    "id": "tool-nonexistent",  # Ferramenta que não existe
                    "parameters": {}
                }
            ]
        }
        
        response = await client.post(
            f"{API_URL}/api/agents/agents",
            headers=auth_headers,
            json=invalid_agent
        )
        assert response.status_code == 400

@pytest.mark.asyncio
async def test_unauthorized_access():
    """Testa acesso não autorizado aos endpoints."""
    async with httpx.AsyncClient() as client:
        # Tentar acessar sem token
        response = await client.get(
            f"{API_URL}/api/marketplace/tools"
        )
        assert response.status_code == 401
        
        # Tentar acessar com token inválido
        invalid_headers = {"Authorization": "Bearer invalid_token"}
        response = await client.get(
            f"{API_URL}/api/marketplace/tools",
            headers=invalid_headers
        )
        assert response.status_code == 401

# Execução dos testes
if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
