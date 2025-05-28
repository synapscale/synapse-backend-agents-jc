"""
Implementação do conector para a Tess AI.

Este módulo contém a implementação do conector para a Tess AI,
seguindo o padrão de interface definido em BaseLLMConnector.
"""

import os
import json
import time
import requests
from typing import Dict, List, Any, Optional, Union, Tuple

from synapse.core.llm.base import BaseLLMConnector
from synapse.config import settings
from synapse.logging import get_logger

logger = get_logger(__name__)


class TessAIConnector(BaseLLMConnector):
    """
    Conector para a Tess AI.
    
    Este conector implementa a interface BaseLLMConnector para
    integração com a plataforma Tess AI, que oferece acesso a
    múltiplos modelos de linguagem através de agentes.
    """
    
    def __init__(self, api_key: str = None, **kwargs):
        """
        Inicializa o conector Tess AI.
        
        Args:
            api_key: Chave de API da Tess AI (opcional, usa a configuração se não fornecida)
            **kwargs: Argumentos adicionais para configuração
        """
        self.api_key = api_key or settings.TESS_API_KEY
        self.base_url = kwargs.get('base_url') or settings.TESS_API_BASE_URL or "https://tess.pareto.io/api"
        
        # Cabeçalhos para requisições
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # Cache para agentes e modelos
        self._agents_cache = None
        self._models_cache = {}
        self._agent_details_cache = {}
        
        logger.info(f"Conector Tess AI inicializado com base_url={self.base_url}")
    
    def provider_name(self) -> str:
        """
        Retorna o nome do provedor.
        
        Returns:
            Nome do provedor
        """
        return "tess"
    
    def default_model(self) -> str:
        """
        Retorna o modelo padrão para este provedor.
        
        Returns:
            Nome do modelo padrão
        """
        return "tess-agent"
    
    def is_available(self) -> bool:
        """
        Verifica se o provedor está disponível.
        
        Returns:
            True se o provedor estiver disponível, False caso contrário
        """
        return bool(self.api_key)
    
    def capabilities(self) -> List[str]:
        """
        Retorna as capacidades deste provedor.
        
        Returns:
            Lista de capacidades
        """
        return ["text-generation", "chat", "reasoning"]
    
    async def get_model_details(self, model_id: str) -> Dict[str, Any]:
        """
        Obtém detalhes de um modelo específico.
        
        Args:
            model_id: ID do modelo
            
        Returns:
            Detalhes do modelo
        """
        models = await self.list_models()
        for model in models:
            if model["id"] == model_id:
                return model
        
        # Se não encontrar, retorna informações padrão
        return {
            "id": model_id,
            "name": model_id,
            "provider": "Tess AI",
            "context_window": 4000,
            "capabilities": ["text-generation"]
        }
    
    async def get_models(self) -> List[Dict[str, Any]]:
        """
        Lista os modelos disponíveis.
        
        Returns:
            Lista de modelos disponíveis
        """
        return await self.list_models()
    
    async def generate_text(
        self, 
        prompt: str, 
        model: Optional[str] = None, 
        max_tokens: int = 1000, 
        temperature: float = 0.7, 
        top_p: float = 0.95, 
        top_k: int = 40, 
        **kwargs
    ) -> str:
        """
        Gera texto a partir de um prompt usando a Tess AI.
        
        Args:
            prompt: Texto de entrada para o modelo
            model: Modelo específico a ser usado (opcional)
            max_tokens: Número máximo de tokens a gerar
            temperature: Temperatura para amostragem (0.0-1.0)
            top_p: Valor de top-p para amostragem nucleus
            top_k: Valor de top-k para amostragem
            **kwargs: Argumentos adicionais
            
        Returns:
            Texto gerado
        """
        try:
            # Obtém o ID do agente (se fornecido ou encontra o melhor)
            agent_id = kwargs.get('agent_id')
            if not agent_id:
                agent_id = await self._get_best_agent_for_task("chat")
                if not agent_id:
                    agent_id = await self._get_best_agent_for_task("text")
                    if not agent_id:
                        raise ValueError("Nenhum agente de chat ou texto disponível")
            
            # Prepara os parâmetros
            params = {
                'temperature': str(temperature),
                'maxlength': max_tokens,
                'language': kwargs.get('language', "Portuguese (Brazil)")
            }
            
            # Obtém detalhes do agente para saber quais parâmetros são necessários
            agent = await self._get_agent_details(agent_id)
            if not agent:
                raise ValueError(f"Agente com ID {agent_id} não encontrado")
            
            # Adiciona a pergunta ao parâmetro apropriado
            # Tenta identificar o campo principal para a pergunta
            question_field = None
            for q in agent.get('questions', []):
                if q.get('type') in ['text', 'textarea'] and q.get('required') and q.get('name') != 'model':
                    question_field = q.get('name')
                    break
            
            if question_field:
                params[question_field] = prompt
            else:
                # Se não encontrar um campo específico, usa um nome genérico
                params['prompt'] = prompt
            
            # Adiciona o modelo se especificado
            if model:
                params['model'] = model
            
            # Executa o agente
            response = await self._execute_agent(agent_id, params)
            if not response:
                raise ValueError("Não foi possível obter uma resposta do agente")
            
            return response.get('content', '')
        except Exception as e:
            logger.error(f"Erro ao gerar texto com Tess AI: {str(e)}")
            raise
    
    async def count_tokens(self, text: str, model: Optional[str] = None, **kwargs) -> int:
        """
        Conta o número de tokens em um texto.
        
        Args:
            text: Texto para contar tokens
            model: Modelo específico a ser usado (opcional)
            **kwargs: Argumentos adicionais
            
        Returns:
            Número de tokens
        """
        # A Tess AI não possui um endpoint específico para contagem de tokens
        # Esta é uma implementação aproximada baseada em heurísticas
        
        # Regra aproximada: 1 token ~= 4 caracteres em português
        # Esta é uma estimativa grosseira e pode variar significativamente
        estimated_tokens = len(text) // 4
        
        # Ajuste para diferentes modelos (se necessário)
        if model and "gpt-4" in model:
            # GPT-4 tende a usar tokenização mais eficiente
            estimated_tokens = int(estimated_tokens * 0.9)
        
        return max(1, estimated_tokens)
    
    async def list_models(self, **kwargs) -> List[Dict[str, Any]]:
        """
        Lista os modelos disponíveis.
        
        Args:
            **kwargs: Argumentos adicionais
            
        Returns:
            Lista de modelos disponíveis
        """
        try:
            # Obtém o ID do agente (se fornecido ou encontra o melhor)
            agent_id = kwargs.get('agent_id')
            if not agent_id:
                agent_id = await self._get_best_agent_for_task("chat")
                if not agent_id:
                    agent_id = await self._get_best_agent_for_task("text")
                    if not agent_id:
                        raise ValueError("Nenhum agente de chat ou texto disponível")
            
            # Obtém os modelos disponíveis para o agente
            models = await self._get_available_models(agent_id)
            
            # Formata os modelos para o padrão esperado
            formatted_models = []
            for model_name in models:
                provider = "Desconhecido"
                capabilities = ["text-generation"]
                context_window = 4000  # Valor padrão
                
                # Determina o provedor e capacidades com base no nome do modelo
                if "gpt" in model_name.lower():
                    provider = "OpenAI"
                    if "4" in model_name:
                        context_window = 8000
                        capabilities.append("reasoning")
                elif "claude" in model_name.lower():
                    provider = "Anthropic"
                    if "opus" in model_name or "3" in model_name:
                        context_window = 100000
                        capabilities.append("reasoning")
                elif "gemini" in model_name.lower():
                    provider = "Google"
                    if "pro" in model_name or "1.5" in model_name:
                        context_window = 32000
                        capabilities.append("reasoning")
                elif "llama" in model_name.lower() or "meta" in model_name.lower():
                    provider = "Meta"
                elif "tess" in model_name.lower():
                    provider = "Tess AI"
                
                formatted_models.append({
                    "id": model_name,
                    "name": model_name,
                    "provider": provider,
                    "context_window": context_window,
                    "capabilities": capabilities
                })
            
            return formatted_models
        except Exception as e:
            logger.error(f"Erro ao listar modelos com Tess AI: {str(e)}")
            raise
    
    async def _list_agents(self) -> List[Dict[str, Any]]:
        """
        Lista todos os agentes disponíveis.
        
        Returns:
            Lista de agentes
        """
        # Usa cache se disponível
        if self._agents_cache is not None:
            return self._agents_cache
        
        try:
            response = requests.get(
                f"{self.base_url}/agents",
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                agents = data.get('data', [])
                self._agents_cache = agents
                return agents
            else:
                logger.error(f"Erro ao listar agentes: {response.status_code} - {response.text}")
                return []
        except Exception as e:
            logger.error(f"Erro ao listar agentes: {str(e)}")
            return []
    
    async def _get_agent_details(self, agent_id: int) -> Dict[str, Any]:
        """
        Obtém detalhes de um agente específico.
        
        Args:
            agent_id: ID do agente
            
        Returns:
            Detalhes do agente
        """
        # Usa cache se disponível
        if agent_id in self._agent_details_cache:
            return self._agent_details_cache[agent_id]
        
        try:
            response = requests.get(
                f"{self.base_url}/agents/{agent_id}",
                headers=self.headers
            )
            
            if response.status_code == 200:
                agent = response.json()
                self._agent_details_cache[agent_id] = agent
                return agent
            else:
                logger.error(f"Erro ao obter detalhes do agente: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logger.error(f"Erro ao obter detalhes do agente: {str(e)}")
            return None
    
    async def _get_available_models(self, agent_id: int) -> List[str]:
        """
        Obtém os modelos disponíveis para um agente específico.
        
        Args:
            agent_id: ID do agente
            
        Returns:
            Lista de modelos disponíveis
        """
        # Usa cache se disponível
        if agent_id in self._models_cache:
            return self._models_cache[agent_id]
        
        try:
            agent = await self._get_agent_details(agent_id)
            if not agent:
                return []
            
            # Procura por perguntas do tipo "select" com nome "model"
            for question in agent.get('questions', []):
                if question.get('type') == 'select' and question.get('name') == 'model':
                    models = [option.get('value') for option in question.get('options', [])]
                    self._models_cache[agent_id] = models
                    return models
            
            return []
        except Exception as e:
            logger.error(f"Erro ao obter modelos disponíveis: {str(e)}")
            return []
    
    async def _get_best_agent_for_task(self, agent_type: str) -> Optional[int]:
        """
        Encontra o melhor agente para um tipo específico de tarefa.
        
        Args:
            agent_type: Tipo de agente ("chat", "text", etc.)
            
        Returns:
            ID do agente ou None se não encontrado
        """
        try:
            agents = await self._list_agents()
            
            # Filtra por tipo
            filtered_agents = [a for a in agents if a.get('type') == agent_type]
            
            if not filtered_agents:
                return None
            
            # Ordena por relevância (assumindo que o primeiro é o mais relevante)
            return filtered_agents[0]['id']
        except Exception as e:
            logger.error(f"Erro ao encontrar agente para tarefa: {str(e)}")
            return None
    
    async def _execute_agent(self, agent_id: int, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executa um agente com os parâmetros fornecidos.
        
        Args:
            agent_id: ID do agente
            params: Parâmetros para o agente
            
        Returns:
            Resposta do agente
        """
        try:
            response = requests.post(
                f"{self.base_url}/agents/{agent_id}/execute",
                headers=self.headers,
                json=params
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Erro ao executar agente: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logger.error(f"Erro ao executar agente: {str(e)}")
            return None
