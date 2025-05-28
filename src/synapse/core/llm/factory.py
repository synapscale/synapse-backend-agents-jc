"""
Implementação da fábrica de conectores de LLM.
Este módulo fornece uma fábrica para criar instâncias de conectores
de LLM de forma dinâmica, baseado na configuração.
"""
from typing import Dict, Any, List, Optional
from synapse.core.llm.base import BaseLLMConnector
from synapse.core.llm.claude import ClaudeConnector
from synapse.core.llm.gemini import GeminiConnector
from synapse.core.llm.grok import GrokConnector
from synapse.core.llm.deepseek import DeepSeekConnector
from synapse.core.llm.tess import TessAIConnector
from synapse.core.llm.openai import OpenAIConnector
from synapse.core.llm.llama import LlamaConnector
from synapse.logging import get_logger

logger = get_logger(__name__)

class LLMFactory:
    """
    Fábrica para criar instâncias de conectores de LLM.
    
    Esta classe implementa o padrão Factory para criar instâncias
    do conector apropriado com base no provedor especificado.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa a fábrica com a configuração.
        
        Args:
            config: Configuração contendo chaves de API e outras configurações
        """
        self.config = config
        self._connectors = {}
        logger.info("Fábrica de LLM inicializada")
        
    def get_connector(self, provider: str = None) -> BaseLLMConnector:
        """
        Retorna uma instância do conector para o provedor especificado.
        
        Args:
            provider: Nome do provedor (ex: "claude", "gemini")
                     Se não especificado, usa o provedor padrão da configuração
                     
        Returns:
            Instância do conector apropriado
            
        Raises:
            ValueError: Se o provedor não for suportado ou não estiver configurado
        """
        provider = provider or self.config.LLM_DEFAULT_PROVIDER
        
        if provider not in self._connectors:
            logger.debug(f"Criando novo conector para provedor: {provider}")
            
            if provider == "claude":
                if not self.config.CLAUDE_API_KEY:
                    raise ValueError("Chave de API Claude não configurada")
                self._connectors[provider] = ClaudeConnector(
                    api_key=self.config.CLAUDE_API_KEY
                )
            elif provider == "gemini":
                if not self.config.GEMINI_API_KEY:
                    raise ValueError("Chave de API Gemini não configurada")
                self._connectors[provider] = GeminiConnector(
                    api_key=self.config.GEMINI_API_KEY
                )
            elif provider == "grok":
                if not self.config.GROK_API_KEY:
                    raise ValueError("Chave de API Grok não configurada")
                self._connectors[provider] = GrokConnector(
                    api_key=self.config.GROK_API_KEY
                )
            elif provider == "deepseek":
                if not self.config.DEEPSEEK_API_KEY:
                    raise ValueError("Chave de API DeepSeek não configurada")
                self._connectors[provider] = DeepSeekConnector(
                    api_key=self.config.DEEPSEEK_API_KEY
                )
            elif provider == "tess":
                if not self.config.TESS_API_KEY:
                    raise ValueError("Chave de API Tess AI não configurada")
                self._connectors[provider] = TessAIConnector(
                    api_key=self.config.TESS_API_KEY,
                    base_url=self.config.TESS_API_BASE_URL
                )
            elif provider == "openai":
                if not self.config.OPENAI_API_KEY:
                    raise ValueError("Chave de API OpenAI não configurada")
                self._connectors[provider] = OpenAIConnector(
                    api_key=self.config.OPENAI_API_KEY
                )
            elif provider == "llama":
                if not self.config.LLAMA_API_KEY:
                    raise ValueError("Chave de API LLaMA não configurada")
                self._connectors[provider] = LlamaConnector(
                    api_key=self.config.LLAMA_API_KEY
                )
            else:
                raise ValueError(f"Provedor não suportado: {provider}")
                
        return self._connectors[provider]
        
    def list_available_providers(self) -> List[str]:
        """
        Lista todos os provedores disponíveis com chaves de API configuradas.
        
        Returns:
            Lista de nomes de provedores disponíveis
        """
        providers = []
        
        if hasattr(self.config, "claude_api_key") and self.config.claude_api_key:
            providers.append("claude")
        if hasattr(self.config, "gemini_api_key") and self.config.gemini_api_key:
            providers.append("gemini")
        if hasattr(self.config, "grok_api_key") and self.config.grok_api_key:
            providers.append("grok")
        if hasattr(self.config, "deepseek_api_key") and self.config.deepseek_api_key:
            providers.append("deepseek")
        if hasattr(self.config, "tess_api_key") and self.config.tess_api_key:
            providers.append("tess")
        if hasattr(self.config, "openai_api_key") and self.config.openai_api_key:
            providers.append("openai")
        if hasattr(self.config, "llama_api_key") and self.config.llama_api_key:
            providers.append("llama")
            
        return providers
