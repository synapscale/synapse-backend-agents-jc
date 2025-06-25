"""
Endpoints da API para interação com LLMs
Criado por José - um desenvolvedor Full Stack
API completa para integração com modelos de linguagem

Este módulo define os endpoints da API para interação com
Modelos de Linguagem de Grande Escala (LLMs).
"""

import logging
from typing import Optional, Dict, Any, List, Union
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from enum import Enum
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from synapse.api.deps import get_current_user
from synapse.database import get_async_db, get_db_sync
from synapse.logger_config import get_logger
from synapse.api.v1.endpoints.llm.schemas import (
    GenerateTextResponse,
    CountTokensResponse,
    ListModelsResponse,
    ListProvidersResponse,
    ModelInfo,
    ModelCapability,
    ModelStatus,
    ProviderInfo,
    ProviderStatus,
)
from synapse.schemas.llm import (
    LLMGenerateRequest as GenerateRequest,
    LLMChatRequest as ChatRequest,
    LLMResponse
)
from synapse.schemas.user_variable import UserVariableCreate
from synapse.models.user import User
from synapse.models.usage_log import UsageLog
from synapse.models.billing_event import BillingEvent
from synapse.models.llm import LLM
from synapse.middlewares.metrics import track_llm_metrics
from synapse.services.llm_service import get_llm_service, UnifiedLLMService
import time
from synapse.exceptions import ValidationError, LLMServiceError

logger = get_logger(__name__)

router = APIRouter()


async def get_dynamic_provider_enum(unified_llm_service: UnifiedLLMService):
    """
    Create a dynamic provider enum based on available providers in database
    """
    try:
        providers = await unified_llm_service.get_available_providers()
        # Create dynamic enum class
        provider_dict = {provider: provider for provider in providers}
        return Enum('DynamicProviderEnum', provider_dict)
    except Exception as e:
        logger.warning(f"Could not get dynamic providers, using fallback: {e}")
        # Fallback to static enum if database is unavailable
        return ProviderEnum


class ProviderEnum(str, Enum):
    openai = "openai"
    claude = "claude"
    gemini = "gemini"
    llama = "llama"
    grok = "grok"
    deepseek = "deepseek"
    tess = "tess"


class ModelEnum(str, Enum):
    gpt_4o = "gpt-4o"
    gpt_4_turbo = "gpt-4-turbo"
    gpt_35_turbo = "gpt-3.5-turbo"
    claude_3_opus = "claude-3-opus"
    claude_3_sonnet = "claude-3-sonnet-20240229"
    claude_3_haiku = "claude-3-haiku"
    gemini_pro = "gemini-1.5-pro"
    gemini_flash = "gemini-1.5-flash"
    llama_3_70b = "llama-3-70b"
    llama_3_8b = "llama-3-8b"
    llama_2_70b = "llama-2-70b"
    grok_1 = "grok-1"
    deepseek_chat = "deepseek-chat"
    deepseek_coder = "deepseek-coder"


def _transform_db_model_to_response(model_dict: Dict[str, Any]) -> ModelInfo:
    """
    Transform database model dictionary to ModelInfo response format.
    
    Args:
        model_dict: Dictionary from LLM.to_dict()
        
    Returns:
        ModelInfo: Formatted model information for API response
    """
    # Map capabilities based on model features
    capabilities = [ModelCapability.text]  # All models support text
    
    if model_dict.get("supports_vision", False):
        capabilities.append(ModelCapability.vision)
    if model_dict.get("supports_function_calling", False):
        capabilities.append(ModelCapability.function_calling)
    
    # Add reasoning capability for Claude models
    if "claude" in model_dict.get("name", "").lower():
        capabilities.append(ModelCapability.reasoning)
    
    # Add code capability for certain models
    if any(keyword in model_dict.get("name", "").lower() for keyword in ["coder", "code", "gemini"]):
        capabilities.append(ModelCapability.code)
    
    # Determine pricing information using correct field names
    pricing = None
    if model_dict.get("cost_per_1k_tokens_input") is not None and model_dict.get("cost_per_1k_tokens_output") is not None:
        pricing = {
            "input": model_dict["cost_per_1k_tokens_input"],
            "output": model_dict["cost_per_1k_tokens_output"]
        }
    
    return ModelInfo(
        id=model_dict["name"],  # Use name as ID for compatibility
        name=model_dict["display_name"],
        provider=model_dict["provider"],
        capabilities=capabilities,
        context_window=model_dict.get("context_window", 4096),
        pricing=pricing,
        status=ModelStatus.available if model_dict.get("is_active", True) else ModelStatus.unavailable
    )


def _get_fallback_models_response(provider: Optional[str] = None) -> ListModelsResponse:
    """
    Get fallback models response when database is unavailable.
    
    Args:
        provider: Optional provider filter
        
    Returns:
        ListModelsResponse: Empty response when database is unavailable
    """
    logger.error("Database unavailable - returning empty models response")
    
    # Return empty response when database is unavailable
    # All data should come from database, no fallback models
    return ListModelsResponse(
        models={},
        count=0
    )


@router.post("/generate", response_model=LLMResponse, tags=["ai"])
async def generate_text(
    request: GenerateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
    db_sync: Session = Depends(get_db_sync),
    unified_llm_service: UnifiedLLMService = Depends(get_llm_service),
):
    """
    Gerar texto usando LLM
    
    Este endpoint permite gerar texto usando diferentes provedores de LLM
    como OpenAI, Claude, Gemini, etc.
    """
    start_time = time.time()
    
    try:
        logger.info(f"Generating text for user {current_user.id} with model {request.model}")
        
        # Use the unified service for text generation with user-specific API keys
        response = await unified_llm_service.generate_text_for_user(
            prompt=request.prompt,
            user_id=current_user.id,
            db_sync=db_sync,
            model=request.model,
            provider=request.provider,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            top_p=request.top_p,
            frequency_penalty=request.frequency_penalty,
            presence_penalty=request.presence_penalty,
        )
        
        # Track metrics
        duration = time.time() - start_time
        await track_llm_metrics(
            db=db,
            user_id=current_user.id,
            provider=response.provider,
            model=response.model,
            tokens_used=response.usage.get("total_tokens", 0),
            duration=duration,
            operation="generate"
        )
        
        return LLMResponse(
            content=response.content,
            model=response.model,
            provider=response.provider,
            usage=response.usage,
            metadata=response.metadata
        )
        
    except Exception as e:
        logger.error(f"Error generating text: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating text: {str(e)}")


@router.post("/chat", response_model=LLMResponse, tags=["ai"])
async def chat_completion(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
    db_sync: Session = Depends(get_db_sync),
    unified_llm_service: UnifiedLLMService = Depends(get_llm_service),
):
    """
    Chat completion usando LLM
    
    Este endpoint permite realizar conversas com diferentes provedores de LLM.
    """
    start_time = time.time()
    
    try:
        logger.info(f"Chat completion for user {current_user.id} with model {request.model}")
        
        # Convert chat messages to a single prompt for now
        # TODO: Implement proper chat handling in the unified service
        prompt = "\n".join([f"{msg.role}: {msg.content}" for msg in request.messages])
        
        # Use the unified service for text generation
        response = await unified_llm_service.generate_text_for_user(
            prompt=prompt,
            user_id=current_user.id,
            db_sync=db_sync,
            model=request.model,
            provider=request.provider,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            top_p=request.top_p,
            frequency_penalty=request.frequency_penalty,
            presence_penalty=request.presence_penalty,
        )
        
        # Track metrics
        duration = time.time() - start_time
        await track_llm_metrics(
            db=db,
            user_id=current_user.id,
            provider=response.provider,
            model=response.model,
            tokens_used=response.usage.get("total_tokens", 0),
            duration=duration,
            operation="chat"
        )
        
        return LLMResponse(
            content=response.content,
            model=response.model,
            provider=response.provider,
            usage=response.usage,
            metadata=response.metadata
        )
        
    except Exception as e:
        logger.error(f"Error in chat completion: {e}")
        raise HTTPException(status_code=500, detail=f"Error in chat completion: {str(e)}")


@router.post("/count-tokens", response_model=CountTokensResponse, summary="Contar tokens de texto", tags=["ai"])
async def count_tokens_endpoint(
    text: str = Query(
        ...,
        description="Texto para contar os tokens",
        example="Este é um exemplo de texto para contar tokens.",
    ),
    provider: Optional[ProviderEnum] = Query(
        None,
        description="Provedor LLM a ser usado para a contagem",
        example="openai",
    ),
    model: Optional[str] = Query(
        None,
        description="Modelo específico a ser usado para a contagem",
        example="gpt-4o",
    ),
    current_user=Depends(get_current_user),
    unified_llm_service: UnifiedLLMService = Depends(get_llm_service),
) -> CountTokensResponse:
    """
    Contar tokens em um texto usando um provedor LLM específico
    
    Esta funcionalidade é útil para estimar custos antes de fazer uma requisição
    """
    try:
        # Try to get actual provider from database if specified
        actual_provider = provider
        if provider and model:
            # Validate model exists in database
            is_valid = await unified_llm_service.validate_model_provider(model, provider)
            if not is_valid:
                logger.warning(f"Model {model} not found for provider {provider} in database")
                # Use simple estimation if model not found
                estimated_tokens = len(text) // 4
                return CountTokensResponse(
                    token_count=estimated_tokens,
                    provider=provider,
                    model=model
                )
        
        # For now, use a simple estimation (4 characters = 1 token)
        # TODO: Implement proper token counting using provider-specific tokenizers
        estimated_tokens = len(text) // 4
        
        return CountTokensResponse(
            token_count=estimated_tokens,
            provider=actual_provider or "openai",
            model=model
        )
        
    except Exception as e:
        logger.error(f"Error counting tokens: {e}")
        raise HTTPException(status_code=500, detail=f"Error counting tokens: {str(e)}")


@router.get("/test-tags", summary="Teste de tags", tags=["ai"])
async def test_tags(current_user: User = Depends(get_current_user)):
    """Endpoint de teste para verificar as tags da documentação"""
    return {"message": "Tags funcionando corretamente!", "user": current_user.email}


@router.get("/models", response_model=ListModelsResponse, summary="Listar modelos", tags=["ai"])
async def list_models(
    provider: Optional[ProviderEnum] = Query(
        None,
        description="Filtrar por provedor específico",
        example="openai",
    ),
    current_user=Depends(get_current_user),
    unified_llm_service: UnifiedLLMService = Depends(get_llm_service),
) -> ListModelsResponse:
    """
    Listar todos os modelos LLM disponíveis
    
    Retorna uma lista de modelos disponíveis, opcionalmente filtrados por provedor.
    """
    try:
        logger.info(f"Listing models for provider: {provider}")
        
        # Get models from unified service
        models_data = await unified_llm_service.get_available_models(provider=provider)
        
        # Transform to response format
        models = [_transform_db_model_to_response(model) for model in models_data]
        
        # Group models by provider
        models_by_provider = {}
        for model in models:
            if model.provider not in models_by_provider:
                models_by_provider[model.provider] = []
            models_by_provider[model.provider].append(model)
        
        return ListModelsResponse(
            models=models_by_provider,
            count=len(models)
        )
        
    except Exception as e:
        logger.error(f"Error listing models: {e}")
        # Return empty response when database is unavailable
        return _get_fallback_models_response(provider)


@router.get("/providers", response_model=ListProvidersResponse, summary="Listar provedores", tags=["ai"])
async def list_providers(
    current_user=Depends(get_current_user),
    unified_llm_service: UnifiedLLMService = Depends(get_llm_service)
) -> ListProvidersResponse:
    """
    Listar todos os provedores LLM disponíveis
    
    Retorna informações sobre os provedores de LLM suportados.
    """
    try:
        logger.info("Listing LLM providers")
        
        # Get providers from unified service
        provider_names = await unified_llm_service.get_available_providers()
        
        # Transform to response format
        providers = []
        for provider_name in provider_names:
            # Get models for this provider
            models_data = await unified_llm_service.get_available_models(provider=provider_name)
            model_count = len(models_data)
            
            providers.append(ProviderInfo(
                id=provider_name,
                name=provider_name.title(),
                description=f"Provider {provider_name.title()}",
                models_count=model_count,
                status=ProviderStatus.operational,
                documentation_url=_get_provider_documentation_url(provider_name)
            ))
        
        return ListProvidersResponse(
            providers=providers,
            count=len(providers)
        )
        
    except Exception as e:
        logger.error(f"Error listing providers: {e}")
        # Return empty response when database is unavailable
        # All data should come from database, no fallback providers
        return ListProvidersResponse(
            providers=[],
            count=0
        )


def _get_provider_documentation_url(provider: str) -> Optional[str]:
    """Get documentation URL for a provider"""
    urls = {
        "openai": "https://platform.openai.com/docs",
        "anthropic": "https://docs.anthropic.com",
        "google": "https://ai.google.dev/docs",
        "claude": "https://docs.anthropic.com",
        "gemini": "https://ai.google.dev/docs"
    }
    return urls.get(provider.lower())


@router.post("/{provider}/generate", response_model=GenerateTextResponse, summary="Gerar texto com provedor específico", tags=["ai"])
async def generate_text_with_provider(
    provider: ProviderEnum = Path(
        ...,
        description="Nome do provedor",
        example="openai",
    ),
    prompt: str = Query(
        ...,
        description="Texto de entrada para o modelo processar",
        example="Explique o conceito de machine learning em termos simples.",
    ),
    model: Optional[str] = Query(
        None,
        description="Modelo específico do provedor",
        example="gpt-4o",
    ),
    max_tokens: Optional[int] = Query(
        1000,
        description="Limite máximo de tokens na resposta",
        ge=1,
        le=8192,
        example=500,
    ),
    temperature: Optional[float] = Query(
        0.7,
        description="Controle de aleatoriedade (0.0-1.0)",
        ge=0.0,
        le=1.0,
        example=0.7,
    ),
    presence_penalty: Optional[float] = Query(
        None,
        description="Penalidade de presença (apenas OpenAI)",
        ge=-2.0,
        le=2.0,
        example=0.2,
    ),
    frequency_penalty: Optional[float] = Query(
        None,
        description="Penalidade de frequência (apenas OpenAI)",
        ge=-2.0,
        le=2.0,
        example=0.3,
    ),
    top_p: Optional[float] = Query(
        None,
        description="Probabilidade acumulada para amostragem de núcleo (0.0-1.0)",
        ge=0.0,
        le=1.0,
        example=0.95,
    ),
    top_k: Optional[int] = Query(
        None,
        description="Número de tokens mais prováveis a considerar",
        ge=1,
        le=100,
        example=40,
    ),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
    db_sync: Session = Depends(get_db_sync),
    unified_llm_service: UnifiedLLMService = Depends(get_llm_service),
) -> GenerateTextResponse:
    """
    Gerar texto usando um provedor específico
    
    Este endpoint permite especificar exatamente qual provedor usar.
    """
    start_time = time.time()
    
    try:
        logger.info(f"Generating text with provider {provider} for user {current_user.id}")
        
        # Use the unified service for text generation
        response = await unified_llm_service.generate_text_for_user(
            prompt=prompt,
            user_id=current_user.id,
            db_sync=db_sync,
            model=model,
            provider=provider,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
        )
        
        # Track metrics
        duration = time.time() - start_time
        await track_llm_metrics(
            db=db,
            user_id=current_user.id,
            provider=response.provider,
            model=response.model,
            tokens_used=response.usage.get("total_tokens", 0),
            duration=duration,
            operation="generate_with_provider"
        )
        
        return GenerateTextResponse(
            text=response.content,
            model=response.model,
            provider=response.provider,
            tokens_used=response.usage.get("total_tokens", 0),
            processing_time=duration,
            metadata=response.metadata
        )
        
    except Exception as e:
        logger.error(f"Error generating text with provider {provider}: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating text: {str(e)}")


@router.post("/{provider}/count-tokens", response_model=CountTokensResponse, summary="Contar tokens com provedor específico", tags=["ai"])
async def count_tokens_with_provider(
    provider: ProviderEnum = Path(
        ...,
        description="Nome do provedor",
        example="openai",
    ),
    text: str = Query(
        ...,
        description="Texto para contar os tokens",
        example="Este é um exemplo de texto para contar tokens.",
    ),
    model: Optional[str] = Query(
        None,
        description="Modelo específico a ser usado para a contagem",
        example="gpt-4o",
    ),
    current_user=Depends(get_current_user),
    unified_llm_service: UnifiedLLMService = Depends(get_llm_service),
) -> CountTokensResponse:
    """
    Contar tokens usando um provedor específico
    """
    try:
        # Validate provider exists in database
        available_providers = await unified_llm_service.get_available_providers()
        if provider not in available_providers:
            logger.warning(f"Provider {provider} not found in database")
            raise HTTPException(status_code=404, detail=f"Provider {provider} not found")
        
        # Validate model if specified
        if model:
            is_valid = await unified_llm_service.validate_model_provider(model, provider)
            if not is_valid:
                logger.warning(f"Model {model} not found for provider {provider} in database")
                raise HTTPException(status_code=404, detail=f"Model {model} not found for provider {provider}")
        
        # For now, use a simple estimation (4 characters = 1 token)
        # TODO: Implement proper token counting using provider-specific tokenizers
        estimated_tokens = len(text) // 4
        
        return CountTokensResponse(
            token_count=estimated_tokens,
            provider=provider,
            model=model
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error counting tokens with provider {provider}: {e}")
        raise HTTPException(status_code=500, detail=f"Error counting tokens: {str(e)}")


@router.get("/{provider}/models", response_model=ListModelsResponse, summary="Listar modelos de provedor específico", tags=["ai"])
async def list_models_for_provider(
    provider: ProviderEnum = Path(
        ...,
        description="Nome do provedor",
        example="openai",
    ),
    current_user=Depends(get_current_user),
    unified_llm_service: UnifiedLLMService = Depends(get_llm_service),
) -> ListModelsResponse:
    """
    Listar modelos disponíveis para um provedor específico
    """
    try:
        logger.info(f"Listing models for provider: {provider}")
        
        # Get models from unified service for specific provider
        models_data = await unified_llm_service.get_available_models(provider=provider)
        
        # Transform to response format
        models = [_transform_db_model_to_response(model) for model in models_data]
        
        # Group models by provider (even if it's just one provider)
        models_by_provider = {}
        for model in models:
            if model.provider not in models_by_provider:
                models_by_provider[model.provider] = []
            models_by_provider[model.provider].append(model)
        
        return ListModelsResponse(
            models=models_by_provider,
            count=len(models)
        )
        
    except Exception as e:
        logger.error(f"Error listing models for provider {provider}: {e}")
        # Return empty response when database is unavailable
        return _get_fallback_models_response(provider)


@router.get("/usage")
async def get_llm_usage(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
) -> Dict[str, Any]:
    """
    Obter estatísticas de uso de LLM do usuário
    """
    try:
        # Query usage statistics from database
        # This is a placeholder implementation
        return {
            "user_id": str(current_user.id),
            "total_requests": 0,
            "total_tokens": 0,
            "providers_used": [],
            "models_used": [],
            "last_request": None
        }
        
    except Exception as e:
        logger.error(f"Error getting LLM usage: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting usage statistics: {str(e)}")
