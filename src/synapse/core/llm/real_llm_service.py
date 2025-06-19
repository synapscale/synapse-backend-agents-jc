"""
Real LLM Service - Implementação real com APIs dos provedores
Criado para substituir o mock service com chamadas reais para LLMs
"""

import asyncio
import aiohttp
import json
from typing import Dict, Any, Optional, List
from collections.abc import AsyncGenerator
import os
from datetime import datetime

# Import providers
try:
    import openai
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    import google.generativeai as genai
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False

from synapse.config import Settings
from synapse.logger_config import get_logger
# Import for ListModelsResponse to avoid circular import issues
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from synapse.api.v1.endpoints.llm.schemas import ListModelsResponse

logger = get_logger(__name__)


class LLMResponse:
    """Resposta padrão dos LLMs"""
    def __init__(self, content: str, model: str, provider: str, usage: dict = None, metadata: dict = None):
        self.content = content
        self.model = model
        self.provider = provider
        self.usage = usage or {}
        self.metadata = metadata or {}


class RealLLMService:
    """Serviço real para integração com múltiplos provedores de LLM"""

    def __init__(self):
        self.settings = Settings()
        self.providers = {}
        self.clients = {}
        self._initialize_providers()

    def _initialize_providers(self):
        """Inicializa os provedores de LLM disponíveis com suas configurações reais"""
        
        # OpenAI
        if OPENAI_AVAILABLE and self.settings.OPENAI_API_KEY:
            try:
                self.clients["openai"] = AsyncOpenAI(api_key=self.settings.OPENAI_API_KEY)
                self.providers["openai"] = {
                    "name": "OpenAI",
                    "models": ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"],
                    "available": True
                }
                logger.info("OpenAI provider initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI: {e}")
                self.providers["openai"] = {"available": False, "error": str(e)}

        # Anthropic
        anthropic_key = getattr(self.settings, 'ANTHROPIC_API_KEY', None) or getattr(self.settings, 'CLAUDE_API_KEY', None)
        if ANTHROPIC_AVAILABLE and anthropic_key:
            try:
                self.clients["anthropic"] = anthropic.AsyncAnthropic(api_key=anthropic_key)
                self.providers["anthropic"] = {
                    "name": "Anthropic",
                    "models": ["claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"],
                    "available": True
                }
                logger.info("Anthropic provider initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Anthropic: {e}")
                self.providers["anthropic"] = {"available": False, "error": str(e)}

        # Google Gemini
        google_key = getattr(self.settings, 'GOOGLE_API_KEY', None) or getattr(self.settings, 'GEMINI_API_KEY', None)
        if GOOGLE_AVAILABLE and google_key:
            try:
                genai.configure(api_key=google_key)
                self.providers["google"] = {
                    "name": "Google",
                    "models": ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-1.0-pro"],
                    "available": True
                }
                logger.info("Google provider initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Google: {e}")
                self.providers["google"] = {"available": False, "error": str(e)}

        logger.info(f"Initialized {len([p for p in self.providers.values() if p.get('available')])} LLM providers")

    async def generate_text(
        self,
        prompt: str,
        model: str | None = None,
        provider: str | None = None,
        **kwargs,
    ) -> LLMResponse:
        """
        Gera texto usando o LLM especificado

        Args:
            prompt: Prompt para o LLM
            model: Modelo específico (opcional)
            provider: Provedor específico (opcional)
            **kwargs: Parâmetros adicionais

        Returns:
            LLMResponse: Resposta do LLM
        """
        # Determine provider and model
        if not provider:
            provider = getattr(self.settings, 'LLM_DEFAULT_PROVIDER', 'openai')
        
        if not model:
            model = self._get_default_model(provider)

        # Route to appropriate provider
        if provider == "openai" and self.providers.get("openai", {}).get("available"):
            return await self._generate_openai(prompt, model, **kwargs)
        elif provider == "anthropic" and self.providers.get("anthropic", {}).get("available"):
            return await self._generate_anthropic(prompt, model, **kwargs)
        elif provider == "google" and self.providers.get("google", {}).get("available"):
            return await self._generate_google(prompt, model, **kwargs)
        else:
            # Fallback to mock if provider not available
            return LLMResponse(
                content=f"Provider {provider} not available. Mock response for: {prompt[:50]}...",
                model=model or "mock-model",
                provider=provider or "mock",
                usage={"tokens": 100},
                metadata={"mock": True, "reason": "provider_not_available"}
            )

    async def _generate_openai(self, prompt: str, model: str, **kwargs) -> LLMResponse:
        """Generate text using OpenAI"""
        try:
            client = self.clients["openai"]
            
            response = await client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=kwargs.get("max_tokens", 1000),
                temperature=kwargs.get("temperature", 0.7),
                top_p=kwargs.get("top_p", 1.0),
                frequency_penalty=kwargs.get("frequency_penalty", 0.0),
                presence_penalty=kwargs.get("presence_penalty", 0.0),
            )
            
            return LLMResponse(
                content=response.choices[0].message.content,
                model=model,
                provider="openai",
                usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                },
                metadata={
                    "finish_reason": response.choices[0].finish_reason,
                    "created": response.created,
                }
            )
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise Exception(f"OpenAI API error: {str(e)}")

    async def _generate_anthropic(self, prompt: str, model: str, **kwargs) -> LLMResponse:
        """Generate text using Anthropic Claude"""
        try:
            client = self.clients["anthropic"]
            
            response = await client.messages.create(
                model=model,
                max_tokens=kwargs.get("max_tokens", 1000),
                temperature=kwargs.get("temperature", 0.7),
                messages=[{"role": "user", "content": prompt}]
            )
            
            return LLMResponse(
                content=response.content[0].text,
                model=model,
                provider="anthropic",
                usage={
                    "prompt_tokens": response.usage.input_tokens,
                    "completion_tokens": response.usage.output_tokens,
                    "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
                },
                metadata={
                    "stop_reason": response.stop_reason,
                }
            )
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise Exception(f"Anthropic API error: {str(e)}")

    async def _generate_google(self, prompt: str, model: str, **kwargs) -> LLMResponse:
        """Generate text using Google Gemini"""
        try:
            model_obj = genai.GenerativeModel(model)
            
            generation_config = genai.types.GenerationConfig(
                temperature=kwargs.get("temperature", 0.7),
                top_p=kwargs.get("top_p", 0.95),
                top_k=kwargs.get("top_k", 40),
                max_output_tokens=kwargs.get("max_tokens", 1000),
            )
            
            response = await model_obj.generate_content_async(
                prompt,
                generation_config=generation_config
            )
            
            return LLMResponse(
                content=response.text,
                model=model,
                provider="google",
                usage={
                    "prompt_tokens": response.usage_metadata.prompt_token_count if hasattr(response, 'usage_metadata') else 0,
                    "completion_tokens": response.usage_metadata.candidates_token_count if hasattr(response, 'usage_metadata') else 0,
                    "total_tokens": response.usage_metadata.total_token_count if hasattr(response, 'usage_metadata') else 0,
                },
                metadata={
                    "finish_reason": response.candidates[0].finish_reason.name if response.candidates else "stop",
                }
            )
        except Exception as e:
            logger.error(f"Google API error: {e}")
            raise Exception(f"Google API error: {str(e)}")

    def _get_default_model(self, provider: str) -> str:
        """Get default model for provider"""
        defaults = {
            "openai": "gpt-4o",
            "anthropic": "claude-3-sonnet-20240229",
            "google": "gemini-1.5-pro",
        }
        return defaults.get(provider, "gpt-4o")

    async def chat_completion(
        self,
        messages: list[dict[str, str]],
        model: str | None = None,
        provider: str | None = None,
        **kwargs,
    ) -> LLMResponse:
        """
        Chat completion using the specified LLM

        Args:
            messages: Lista de mensagens do chat
            model: Modelo específico (opcional)
            provider: Provedor específico (opcional)
            **kwargs: Parâmetros adicionais

        Returns:
            LLMResponse: Resposta do LLM
        """
        # Convert messages to a single prompt for providers that don't support chat format
        if messages:
            prompt = "\n".join([f"{msg.get('role', 'user')}: {msg.get('content', '')}" for msg in messages])
        else:
            prompt = ""

        return await self.generate_text(prompt, model, provider, **kwargs)

    def get_available_models(self, provider: str | None = None) -> list[str]:
        """
        Retorna lista de modelos disponíveis

        Args:
            provider: Provedor específico (opcional)

        Returns:
            List[str]: Lista de modelos disponíveis
        """
        if provider and provider in self.providers:
            return self.providers[provider].get("models", [])
        
        # Return all available models
        all_models = []
        for prov_info in self.providers.values():
            if prov_info.get("available"):
                all_models.extend(prov_info.get("models", []))
        
        return all_models

    def get_available_providers(self) -> dict[str, Any]:
        """
        Retorna lista de provedores disponíveis

        Returns:
            Dict[str, Any]: Informações dos provedores
        """
        providers_info = []
        
        for provider_id, info in self.providers.items():
            if info.get("available"):
                providers_info.append({
                    "id": provider_id,
                    "name": info.get("name", provider_id.title()),
                    "description": f"Provedor {info.get('name', provider_id)} com modelos de linguagem",
                    "models_count": len(info.get("models", [])),
                    "status": "operational",
                    "documentation_url": self._get_provider_docs(provider_id),
                })

        return {
            "providers": providers_info,
            "count": len(providers_info),
        }

    def _get_provider_docs(self, provider: str) -> str:
        """Get documentation URL for provider"""
        docs = {
            "openai": "https://platform.openai.com/docs",
            "anthropic": "https://docs.anthropic.com",
            "google": "https://ai.google.dev/docs",
        }
        return docs.get(provider)

    async def health_check(self, provider: str | None = None) -> dict[str, Any]:
        """
        Verifica a saúde dos provedores de LLM

        Args:
            provider: Provedor específico (opcional)

        Returns:
            Dict[str, Any]: Status de saúde
        """
        if provider:
            if provider in self.providers:
                return {
                    "status": "healthy" if self.providers[provider].get("available") else "unhealthy",
                    "provider": provider,
                    "available": self.providers[provider].get("available", False),
                    "models": self.providers[provider].get("models", []),
                }
            else:
                return {"status": "not_found", "provider": provider}
        
        # Overall health check
        available_providers = sum(1 for p in self.providers.values() if p.get("available"))
        total_providers = len(self.providers)
        
        return {
            "status": "healthy" if available_providers > 0 else "unhealthy",
            "providers_available": available_providers,
            "providers_total": total_providers,
            "providers": {
                provider_id: {
                    "available": info.get("available", False),
                    "models": info.get("models", []),
                }
                for provider_id, info in self.providers.items()
            },
        }

    async def count_tokens(
        self, text: str, provider: str | None = None, model: str | None = None
    ) -> dict[str, Any]:
        """
        Conta o número de tokens em um texto

        Args:
            text: Texto para contar tokens
            provider: Provedor específico (opcional)
            model: Modelo específico (opcional)

        Returns:
            Dict[str, Any]: Informações sobre contagem de tokens
        """
        # For now, use simple estimation
        # In production, could use tiktoken for OpenAI or provider-specific tokenizers
        
        # Estimativa básica: ~4 caracteres por token (média para inglês)
        estimated_tokens = max(1, len(text) // 4)

        # Contagem mais precisa por palavras
        words = len(text.split())
        word_based_tokens = max(1, int(words * 1.3))  # ~1.3 tokens por palavra

        # Usar a maior estimativa para ser conservador
        token_count = max(estimated_tokens, word_based_tokens)

        return {
            "text": text[:100] + "..." if len(text) > 100 else text,
            "token_count": token_count,
            "character_count": len(text),
            "word_count": words,
            "provider": provider or "default",
            "model": model or "default",
            "estimation_method": "character_and_word_based",
            "note": "Estimation based on character and word count. For precise count, use provider-specific tokenizers.",
        }

    async def list_models(self, provider: str | None = None):
        """
        Lista todos os modelos disponíveis, agrupados por provedor.
        """
        # Real models data based on initialized providers
        all_models = {}
        
        for provider_id, info in self.providers.items():
            if info.get("available"):
                models_list = []
                for model_id in info.get("models", []):
                    model_info = {
                        "id": model_id,
                        "name": self._get_model_display_name(model_id),
                        "provider": provider_id,
                        "capabilities": self._get_model_capabilities(model_id),
                        "context_window": self._get_model_context_window(model_id),
                        "status": "available",
                    }
                    models_list.append(model_info)
                
                if models_list:
                    all_models[provider_id] = models_list

        # Filter by provider if requested
        if provider and provider in all_models:
            models = {provider: all_models[provider]}
        else:
            models = all_models

        count = sum(len(m) for m in models.values())
        
        # Import here to avoid circular imports
        from synapse.api.v1.endpoints.llm.schemas import ListModelsResponse
        
        return ListModelsResponse(models=models, count=count)

    def _get_model_display_name(self, model_id: str) -> str:
        """Get display name for model"""
        names = {
            "gpt-4o": "GPT-4o",
            "gpt-4-turbo": "GPT-4 Turbo",
            "gpt-3.5-turbo": "GPT-3.5 Turbo",
            "claude-3-opus-20240229": "Claude 3 Opus",
            "claude-3-sonnet-20240229": "Claude 3 Sonnet",
            "claude-3-haiku-20240307": "Claude 3 Haiku",
            "gemini-1.5-pro": "Gemini 1.5 Pro",
            "gemini-1.5-flash": "Gemini 1.5 Flash",
            "gemini-1.0-pro": "Gemini 1.0 Pro",
        }
        return names.get(model_id, model_id.title())

    def _get_model_capabilities(self, model_id: str) -> list[str]:
        """Get capabilities for model"""
        capabilities = {
            "gpt-4o": ["text", "vision", "function_calling"],
            "gpt-4-turbo": ["text", "vision"],
            "gpt-3.5-turbo": ["text"],
            "claude-3-opus-20240229": ["text", "vision", "reasoning"],
            "claude-3-sonnet-20240229": ["text", "vision", "reasoning"],
            "claude-3-haiku-20240307": ["text", "reasoning"],
            "gemini-1.5-pro": ["text", "vision", "code"],
            "gemini-1.5-flash": ["text", "vision", "code"],
            "gemini-1.0-pro": ["text"],
        }
        return capabilities.get(model_id, ["text"])

    def _get_model_context_window(self, model_id: str) -> int:
        """Get context window for model"""
        contexts = {
            "gpt-4o": 128000,
            "gpt-4-turbo": 128000,
            "gpt-3.5-turbo": 16385,
            "claude-3-opus-20240229": 200000,
            "claude-3-sonnet-20240229": 200000,
            "claude-3-haiku-20240307": 200000,
            "gemini-1.5-pro": 2097152,
            "gemini-1.5-flash": 1048576,
            "gemini-1.0-pro": 30720,
        }
        return contexts.get(model_id, 4096)


# Create global instance
real_llm_service = RealLLMService() 