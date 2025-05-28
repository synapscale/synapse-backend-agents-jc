"""
Classe base abstrata para conectores de LLMs.

Este módulo define a interface comum que todos os conectores de LLM
devem implementar, garantindo consistência entre diferentes provedores.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class BaseLLMConnector(ABC):
    """
    Classe base abstrata para conectores de LLM.
    
    Todos os conectores específicos de provedores devem herdar desta classe
    e implementar seus métodos abstratos.
    """
    
    @abstractmethod
    def __init__(self, api_key: str, **kwargs):
        """
        Inicializa o conector com a chave de API e configurações adicionais.
        
        Args:
            api_key: Chave de API para o provedor de LLM
            **kwargs: Configurações adicionais específicas do provedor
        """
        pass
        
    @abstractmethod
    async def generate_text(self, prompt: str, model: str = None, 
                           max_tokens: int = 1000, **kwargs) -> str:
        """
        Gera texto a partir de um prompt usando o modelo especificado.
        
        Args:
            prompt: Texto de entrada para o modelo
            model: ID do modelo a ser usado (opcional, usa o padrão se não especificado)
            max_tokens: Número máximo de tokens a gerar
            **kwargs: Parâmetros adicionais específicos do provedor
            
        Returns:
            Texto gerado pelo modelo
        """
        pass
        
    @abstractmethod
    async def count_tokens(self, text: str, model: str = None) -> int:
        """
        Conta o número de tokens em um texto para o modelo especificado.
        
        Args:
            text: Texto para contar tokens
            model: ID do modelo a ser usado (opcional, usa o padrão se não especificado)
            
        Returns:
            Número de tokens no texto
        """
        pass
        
    @abstractmethod
    async def get_models(self) -> List[Dict[str, Any]]:
        """
        Retorna a lista de modelos disponíveis para este provedor.
        
        Returns:
            Lista de dicionários com informações sobre cada modelo
        """
        pass
        
    @abstractmethod
    async def get_model_details(self, model_id: str) -> Dict[str, Any]:
        """
        Retorna detalhes sobre um modelo específico.
        
        Args:
            model_id: ID do modelo
            
        Returns:
            Dicionário com detalhes do modelo
            
        Raises:
            ValueError: Se o modelo não for encontrado
        """
        pass
        
    @abstractmethod
    def is_available(self) -> bool:
        """
        Verifica se o provedor está disponível e configurado corretamente.
        
        Returns:
            True se o provedor estiver disponível, False caso contrário
        """
        pass
        
    @abstractmethod
    def provider_name(self) -> str:
        """
        Retorna o nome do provedor.
        
        Returns:
            Nome do provedor (ex: "claude", "gemini")
        """
        pass
        
    @abstractmethod
    def default_model(self) -> str:
        """
        Retorna o ID do modelo padrão para este provedor.
        
        Returns:
            ID do modelo padrão
        """
        pass
        
    @abstractmethod
    def capabilities(self) -> List[str]:
        """
        Retorna a lista de capacidades suportadas por este provedor.
        
        Returns:
            Lista de capacidades (ex: ["text-generation", "image-understanding"])
        """
        pass
