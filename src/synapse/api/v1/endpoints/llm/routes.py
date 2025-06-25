"""
Endpoints da API para interação com LLMs
Criado por José - um desenvolvedor Full Stack
API completa para integração com modelos de linguagem

Este módulo define os endpoints da API para interação com
Modelos de Linguagem de Grande Escala (LLMs).
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from enum import Enum
from sqlalchemy.orm import Session

from synapse.api.deps import get_current_user, get_db
from synapse.core.llm import llm_service
from synapse.core.llm.user_variables_llm_service import user_variables_llm_service
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
    
    # Determine pricing information
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
    Fallback implementation using the original enum-based approach.
    
    Args:
        provider: Optional provider filter
        
    Returns:
        ListModelsResponse: Response using hardcoded model data
    """
    logger.warning("Using fallback models implementation due to database error")
    
    # Hardcoded model data for fallback (based on original enums)
    fallback_models = {
        "openai": [
            ModelInfo(
                id="gpt-4o",
                name="GPT-4o",
                provider="openai",
                capabilities=[ModelCapability.text, ModelCapability.vision, ModelCapability.function_calling],
                context_window=128000,
                pricing={"input": 0.005, "output": 0.015},
                status=ModelStatus.available
            ),
            ModelInfo(
                id="gpt-4-turbo",
                name="GPT-4 Turbo",
                provider="openai",
                capabilities=[ModelCapability.text, ModelCapability.vision],
                context_window=128000,
                pricing={"input": 0.01, "output": 0.03},
                status=ModelStatus.available
            ),
            ModelInfo(
                id="gpt-3.5-turbo",
                name="GPT-3.5 Turbo",
                provider="openai",
                capabilities=[ModelCapability.text],
                context_window=16385,
                pricing={"input": 0.001, "output": 0.002},
                status=ModelStatus.available
            ),
        ],
        "claude": [
            ModelInfo(
                id="claude-3-opus-20240229",
                name="Claude 3 Opus",
                provider="claude",
                capabilities=[ModelCapability.text, ModelCapability.vision, ModelCapability.reasoning],
                context_window=200000,
                pricing={"input": 0.015, "output": 0.075},
                status=ModelStatus.available
            ),
            ModelInfo(
                id="claude-3-sonnet-20240229",
                name="Claude 3 Sonnet",
                provider="claude",
                capabilities=[ModelCapability.text, ModelCapability.vision, ModelCapability.reasoning],
                context_window=200000,
                pricing={"input": 0.008, "output": 0.024},
                status=ModelStatus.available
            ),
            ModelInfo(
                id="claude-3-haiku",
                name="Claude 3 Haiku",
                provider="claude",
                capabilities=[ModelCapability.text, ModelCapability.reasoning],
                context_window=200000,
                pricing={"input": 0.0008, "output": 0.004},
                status=ModelStatus.available
            ),
        ],
        "gemini": [
            ModelInfo(
                id="gemini-1.5-pro",
                name="Gemini 1.5 Pro",
                provider="gemini",
                capabilities=[ModelCapability.text, ModelCapability.vision, ModelCapability.code],
                context_window=2097152,
                pricing={"input": 0.007, "output": 0.021},
                status=ModelStatus.available
            ),
            ModelInfo(
                id="gemini-1.5-flash",
                name="Gemini 1.5 Flash",
                provider="gemini",
                capabilities=[ModelCapability.text, ModelCapability.vision, ModelCapability.code],
                context_window=1048576,
                pricing={"input": 0.00035, "output": 0.00105},
                status=ModelStatus.available
            ),
        ],
    }
    
    # Filter by provider if specified
    if provider and provider in fallback_models:
        filtered_models = {provider: fallback_models[provider]}
    else:
        filtered_models = fallback_models
    
    total_count = sum(len(models) for models in filtered_models.values())
    
    return ListModelsResponse(models=filtered_models, count=total_count)


@router.post("/generate", response_model=LLMResponse, tags=["ai"])
async def generate_text(
    request: GenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    unified_llm_service: UnifiedLLMService = Depends(get_llm_service),
):
    """
    Gera texto usando LLM com API key específica do usuário (se disponível)
    
    Automaticamente usa API keys pessoais do usuário quando configuradas,
    com fallback para API keys globais do sistema.
    """
    try:
        # Validate model and provider against database before processing
        try:
            is_valid = await unified_llm_service.validate_model_provider(
                model_name=request.model,
                provider=request.provider
            )
            
            if not is_valid:
                logger.warning(f"Invalid model/provider combination for user {current_user.id}: {request.model}/{request.provider}")
                # Try fallback validation with enums if configured
                try:
                    model_enum = ModelEnum(request.model)
                    provider_enum = ProviderEnum(request.provider)
                    # If we reach here, the enums are valid, but we should still log this as a fallback
                    logger.info(f"Using enum fallback validation for {request.model}/{request.provider}")
                except ValueError:
                    raise HTTPException(
                        status_code=400,
                        detail={
                            "error": True,
                            "error_type": "invalid_model_provider",
                            "message": f"Invalid model/provider combination: {request.model}/{request.provider}",
                            "is_retryable": False,
                            "suggested_action": "Check available models using /llm/models endpoint"
                        }
                    )
        except Exception as validation_error:
            # If database validation fails, log and continue with existing enum validation
            logger.warning(f"Database validation failed for user {current_user.id}, using enum fallback: {str(validation_error)}")
            try:
                model_enum = ModelEnum(request.model)
                provider_enum = ProviderEnum(request.provider)
                logger.info(f"Enum fallback validation succeeded for {request.model}/{request.provider}")
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": True,
                        "error_type": "invalid_model_provider",
                        "message": f"Invalid model/provider combination: {request.model}/{request.provider}",
                        "is_retryable": False,
                        "suggested_action": "Check available models using /llm/models endpoint"
                    }
                )

        start_time = time.time()
        response = await user_variables_llm_service.generate_text_for_user(
            prompt=request.prompt,
            user_id=str(current_user.id),
            db=db,
            model=request.model,
            provider=request.provider,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            top_p=request.top_p,
            frequency_penalty=request.frequency_penalty,
            presence_penalty=request.presence_penalty,
        )
        latency_ms = int((time.time() - start_time) * 1000)
        
        # Check if the response contains an error
        if hasattr(response, 'metadata') and response.metadata and response.metadata.get('error'):
            error_type = response.metadata.get('error_type', 'unknown_error')
            is_retryable = response.metadata.get('is_retryable', False)
            suggested_action = response.metadata.get('suggested_action', 'Please try again later.')
            
            # Map error types to appropriate HTTP status codes
            status_code = 500  # Default to internal server error
            
            if error_type in ['authentication_error', 'permission_denied']:
                status_code = 401
            elif error_type in ['invalid_request', 'unprocessable_entity']:
                status_code = 400
            elif error_type in ['model_not_found']:
                status_code = 404
            elif error_type in ['rate_limit_exceeded']:
                status_code = 429
            elif error_type in ['quota_exceeded']:
                status_code = 402  # Payment Required
            elif error_type in ['timeout_error', 'connection_error', 'internal_server_error']:
                status_code = 503  # Service Unavailable
            
            # Create detailed error response
            error_detail = {
                "error": True,
                "error_type": error_type,
                "message": response.metadata.get('error_message', str(response.content)),
                "is_retryable": is_retryable,
                "suggested_action": suggested_action,
                "provider": request.provider,
                "model": request.model,
                "timestamp": datetime.now().isoformat()
            }
            
            # Add retry-after header for rate limits
            headers = {}
            if error_type == 'rate_limit_exceeded':
                headers['Retry-After'] = '60'
            
            logger.error(f"LLM service returned error for user {current_user.id}: {error_type}", extra=error_detail)
            raise HTTPException(status_code=status_code, detail=error_detail, headers=headers)
        
        # Registro automático de UsageLog e BillingEvent
        try:
            llm_obj = db.query(LLM).filter(
                LLM.provider == request.provider,
                LLM.name == request.model,
                LLM.is_active == True
            ).first()
            llm_id = llm_obj.id if llm_obj else None
            usage = response.usage or {}
            usage_log = UsageLog(
                user_id=current_user.id,
                llm_id=llm_id,
                input_tokens=usage.get("prompt_tokens", 0),
                output_tokens=usage.get("completion_tokens", 0),
                total_tokens=usage.get("total_tokens", 0),
                cost_usd=llm_obj.calculate_cost(usage.get("prompt_tokens", 0), usage.get("completion_tokens", 0)) if llm_obj else 0.0,
                latency_ms=latency_ms,
                api_status_code=200,
                api_request_payload=request.dict(),
                api_response_metadata=response.metadata,
                user_api_key_used=response.metadata.get("user_api_key", False) if hasattr(response, "metadata") else False,
                model_settings={
                    "model": request.model,
                    "provider": request.provider,
                    "max_tokens": request.max_tokens,
                    "temperature": request.temperature,
                    "top_p": request.top_p,
                    "frequency_penalty": request.frequency_penalty,
                    "presence_penalty": request.presence_penalty,
                },
                status="success",
            )
            db.add(usage_log)
            db.commit()
            db.refresh(usage_log)
            billing_event = BillingEvent(
                user_id=current_user.id,
                event_type="usage",
                amount_usd=usage_log.cost_usd,
                related_usage_log_id=usage_log.id,
                status="completed",
            )
            db.add(billing_event)
            db.commit()
            
            # Registrar métricas de LLM
            track_llm_metrics(
                provider=request.provider or "openai",
                model=request.model or "gpt-4o",
                endpoint="/generate",
                status="success",
                duration=latency_ms / 1000.0,  # converter para segundos
                input_tokens=usage.get("prompt_tokens", 0),
                output_tokens=usage.get("completion_tokens", 0),
                cost=usage_log.cost_usd
            )
        except Exception as logerr:
            logger.error(f"Erro ao registrar UsageLog/BillingEvent: {logerr}")
        return response
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except ValidationError as e:
        logger.warning(f"Validation error for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail={
                "error": True,
                "error_type": "validation_error",
                "message": "Invalid request parameters",
                "details": str(e),
                "is_retryable": False,
                "suggested_action": "Check your request parameters and try again."
            }
        )
    except LLMServiceError as e:
        logger.error(f"LLM service error for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail={
                "error": True,
                "error_type": "service_error",
                "message": "LLM service is temporarily unavailable",
                "details": str(e),
                "is_retryable": True,
                "suggested_action": "Please try again in a few minutes."
            }
        )
    except Exception as e:
        logger.error(f"Unexpected error during text generation for user {current_user.id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": True,
                "error_type": "internal_error",
                "message": "An unexpected error occurred during text generation",
                "details": str(e),
                "is_retryable": False,
                "suggested_action": "Please try again or contact support if the issue persists."
            }
        )


@router.post("/chat", response_model=LLMResponse, tags=["ai"])
async def chat_completion(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    unified_llm_service: UnifiedLLMService = Depends(get_llm_service),
):
    """
    Chat completion usando API key específica do usuário (se disponível)
    
    Automaticamente usa API keys pessoais do usuário quando configuradas,
    com fallback para API keys globais do sistema.
    """
    try:
        # Validate model and provider against database before processing
        try:
            is_valid = await unified_llm_service.validate_model_provider(
                model_name=request.model,
                provider=request.provider
            )
            
            if not is_valid:
                logger.warning(f"Invalid model/provider combination for user {current_user.id}: {request.model}/{request.provider}")
                # Try fallback validation with enums if configured
                try:
                    model_enum = ModelEnum(request.model)
                    provider_enum = ProviderEnum(request.provider)
                    # If we reach here, the enums are valid, but we should still log this as a fallback
                    logger.info(f"Using enum fallback validation for {request.model}/{request.provider}")
                except ValueError:
                    raise HTTPException(
                        status_code=400,
                        detail={
                            "error": True,
                            "error_type": "invalid_model_provider",
                            "message": f"Invalid model/provider combination: {request.model}/{request.provider}",
                            "is_retryable": False,
                            "suggested_action": "Check available models using /llm/models endpoint"
                        }
                    )
        except Exception as validation_error:
            # If database validation fails, log and continue with existing enum validation
            logger.warning(f"Database validation failed for user {current_user.id}, using enum fallback: {str(validation_error)}")
            try:
                model_enum = ModelEnum(request.model)
                provider_enum = ProviderEnum(request.provider)
                logger.info(f"Enum fallback validation succeeded for {request.model}/{request.provider}")
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": True,
                        "error_type": "invalid_model_provider",
                        "message": f"Invalid model/provider combination: {request.model}/{request.provider}",
                        "is_retryable": False,
                        "suggested_action": "Check available models using /llm/models endpoint"
                    }
                )

        start_time = time.time()
        response = await user_variables_llm_service.chat_completion_for_user(
            messages=request.messages,
            user_id=str(current_user.id),
            db=db,
            model=request.model,
            provider=request.provider,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            top_p=request.top_p,
            frequency_penalty=request.frequency_penalty,
            presence_penalty=request.presence_penalty,
        )
        latency_ms = int((time.time() - start_time) * 1000)
        
        # Check if the response contains an error
        if hasattr(response, 'metadata') and response.metadata and response.metadata.get('error'):
            error_type = response.metadata.get('error_type', 'unknown_error')
            is_retryable = response.metadata.get('is_retryable', False)
            suggested_action = response.metadata.get('suggested_action', 'Please try again later.')
            
            # Map error types to appropriate HTTP status codes
            status_code = 500  # Default to internal server error
            
            if error_type in ['authentication_error', 'permission_denied']:
                status_code = 401
            elif error_type in ['invalid_request', 'unprocessable_entity']:
                status_code = 400
            elif error_type in ['model_not_found']:
                status_code = 404
            elif error_type in ['rate_limit_exceeded']:
                status_code = 429
            elif error_type in ['quota_exceeded']:
                status_code = 402  # Payment Required
            elif error_type in ['timeout_error', 'connection_error', 'internal_server_error']:
                status_code = 503  # Service Unavailable
            
            # Create detailed error response
            error_detail = {
                "error": True,
                "error_type": error_type,
                "message": response.metadata.get('error_message', str(response.content)),
                "is_retryable": is_retryable,
                "suggested_action": suggested_action,
                "provider": request.provider,
                "model": request.model,
                "timestamp": datetime.now().isoformat()
            }
            
            # Add retry-after header for rate limits
            headers = {}
            if error_type == 'rate_limit_exceeded':
                headers['Retry-After'] = '60'
            
            logger.error(f"LLM service returned error for user {current_user.id}: {error_type}", extra=error_detail)
            raise HTTPException(status_code=status_code, detail=error_detail, headers=headers)
        
        # Registro automático de UsageLog e BillingEvent
        try:
            llm_obj = db.query(LLM).filter(
                LLM.provider == request.provider,
                LLM.name == request.model,
                LLM.is_active == True
            ).first()
            llm_id = llm_obj.id if llm_obj else None
            usage = response.usage or {}
            usage_log = UsageLog(
                user_id=current_user.id,
                llm_id=llm_id,
                input_tokens=usage.get("prompt_tokens", 0),
                output_tokens=usage.get("completion_tokens", 0),
                total_tokens=usage.get("total_tokens", 0),
                cost_usd=llm_obj.calculate_cost(usage.get("prompt_tokens", 0), usage.get("completion_tokens", 0)) if llm_obj else 0.0,
                latency_ms=latency_ms,
                api_status_code=200,
                api_request_payload=request.dict(),
                api_response_metadata=response.metadata,
                user_api_key_used=response.metadata.get("user_api_key", False) if hasattr(response, "metadata") else False,
                model_settings={
                    "model": request.model,
                    "provider": request.provider,
                    "max_tokens": request.max_tokens,
                    "temperature": request.temperature,
                    "top_p": request.top_p,
                    "frequency_penalty": request.frequency_penalty,
                    "presence_penalty": request.presence_penalty,
                },
                status="success",
            )
            db.add(usage_log)
            db.commit()
            db.refresh(usage_log)
            billing_event = BillingEvent(
                user_id=current_user.id,
                event_type="usage",
                amount_usd=usage_log.cost_usd,
                related_usage_log_id=usage_log.id,
                status="completed",
            )
            db.add(billing_event)
            db.commit()
            
            # Registrar métricas de LLM
            track_llm_metrics(
                provider=request.provider or "openai",
                model=request.model or "gpt-4o",
                endpoint="/chat",
                status="success",
                duration=latency_ms / 1000.0,  # converter para segundos
                input_tokens=usage.get("prompt_tokens", 0),
                output_tokens=usage.get("completion_tokens", 0),
                cost=usage_log.cost_usd
            )
        except Exception as logerr:
            logger.error(f"Erro ao registrar UsageLog/BillingEvent: {logerr}")
        return response
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except ValidationError as e:
        logger.warning(f"Validation error for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail={
                "error": True,
                "error_type": "validation_error",
                "message": "Invalid request parameters",
                "details": str(e),
                "is_retryable": False,
                "suggested_action": "Check your request parameters and try again."
            }
        )
    except LLMServiceError as e:
        logger.error(f"LLM service error for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail={
                "error": True,
                "error_type": "service_error",
                "message": "LLM service is temporarily unavailable",
                "details": str(e),
                "is_retryable": True,
                "suggested_action": "Please try again in a few minutes."
            }
        )
    except Exception as e:
        logger.error(f"Unexpected error during chat completion for user {current_user.id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": True,
                "error_type": "internal_error",
                "message": "An unexpected error occurred during chat completion",
                "details": str(e),
                "is_retryable": False,
                "suggested_action": "Please try again or contact support if the issue persists."
            }
        )


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
) -> CountTokensResponse:
    """
    Conta o número de tokens em um texto usando o tokenizador do provedor especificado.

    ## Função
    Este endpoint calcula quantos tokens existem em um texto, usando o mesmo tokenizador
    que o modelo de LLM utilizaria. Isso é útil para estimar custos e verificar limites.

    ## Quando Usar
    - Antes de enviar textos muito longos para verificar se estão dentro dos limites do modelo
    - Para estimar custos de uso de APIs de LLM que cobram por token
    - Para otimizar prompts e garantir que caibam no contexto do modelo
    
    Args:
        text: Texto para contar tokens
        provider: Provedor de LLM para tokenização
        model: Modelo específico para tokenização
        current_user: Usuário autenticado
        
    Returns:
        CountTokensResponse: Número de tokens e metadados
        
    Raises:
        HTTPException: 400 se parâmetros inválidos
        HTTPException: 500 se erro interno do servidor
    """
    try:
        logger.info(f"Contagem de tokens solicitada por usuário {current_user.id} - provider: {provider}, model: {model}")
        
        if not text:
            logger.warning(f"Texto vazio fornecido para contagem por usuário {current_user.id}")
            raise HTTPException(
                status_code=400,
                detail="Texto não pode estar vazio"
            )

        result = await llm_service.count_tokens(
            text=text,
            provider=provider.value if provider else None,
            model=model,
        )

        logger.info(f"Tokens contados para usuário {current_user.id}: {getattr(result, 'token_count', 0)}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao contar tokens para usuário {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get("/test-tags", summary="Teste de tags", tags=["ai"])
async def test_tags():
    """Endpoint de teste para verificar tags"""
    return {"message": "teste"}

@router.post("/count-tokens-original", response_model=CountTokensResponse, summary="Contar tokens de texto", tags=["ai"])
async def count_tokens(
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
) -> CountTokensResponse:
    """
    Conta o número de tokens em um texto usando o tokenizador do provedor especificado.

    ## Função
    Este endpoint calcula quantos tokens existem em um texto, usando o mesmo tokenizador
    que o modelo de LLM utilizaria. Isso é útil para estimar custos e verificar limites.

    ## Quando Usar
    - Antes de enviar textos muito longos para verificar se estão dentro dos limites do modelo
    - Para estimar custos de uso de APIs de LLM que cobram por token
    - Para otimizar prompts e garantir que caibam no contexto do modelo
    
    Args:
        text: Texto para contar tokens
        provider: Provedor de LLM para tokenização
        model: Modelo específico para tokenização
        current_user: Usuário autenticado
        
    Returns:
        CountTokensResponse: Número de tokens e metadados
        
    Raises:
        HTTPException: 400 se parâmetros inválidos
        HTTPException: 500 se erro interno do servidor
    """
    try:
        logger.info(f"Contagem de tokens solicitada por usuário {current_user.id} - provider: {provider}, model: {model}")
        
        if not text:
            logger.warning(f"Texto vazio fornecido para contagem por usuário {current_user.id}")
            raise HTTPException(
                status_code=400,
                detail="Texto não pode estar vazio"
            )

        result = await llm_service.count_tokens(
            text=text,
            provider=provider.value if provider else None,
            model=model,
        )

        logger.info(f"Tokens contados para usuário {current_user.id}: {getattr(result, 'token_count', 0)}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao contar tokens para usuário {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


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
    Lista todos os modelos de LLM disponíveis na plataforma.
    
    MIGRATED: Now uses database as source of truth via UnifiedLLMService,
    with fallback to hardcoded models for backward compatibility.
    
    Args:
        provider: Filtrar por provedor específico
        current_user: Usuário autenticado
        unified_llm_service: Serviço unificado de LLM (injetado)
        
    Returns:
        ListModelsResponse: Lista de modelos disponíveis
        
    Raises:
        HTTPException: 500 se erro interno do servidor
    """
    try:
        logger.info(f"Listagem de modelos solicitada por usuário {current_user.id} - provider: {provider}")
        
        # Try to get models from database via UnifiedLLMService
        try:
            provider_filter = provider.value if provider else None
            db_models = await unified_llm_service.get_available_models(provider=provider_filter)
            
            # Transform database models to API response format
            models_by_provider = {}
            for model_dict in db_models:
                model_provider = model_dict["provider"]
                if model_provider not in models_by_provider:
                    models_by_provider[model_provider] = []
                
                model_info = _transform_db_model_to_response(model_dict)
                models_by_provider[model_provider].append(model_info)
            
            total_count = sum(len(models) for models in models_by_provider.values())
            
            logger.info(f"Modelos do banco de dados listados para usuário {current_user.id}: {total_count} modelos")
            return ListModelsResponse(models=models_by_provider, count=total_count)
            
        except Exception as db_error:
            logger.error(f"Erro ao buscar modelos no banco de dados: {str(db_error)}")
            logger.info("Usando fallback para modelos hardcoded")
            
            # Fallback to hardcoded models implementation
            fallback_response = _get_fallback_models_response(provider=provider.value if provider else None)
            
            logger.info(f"Modelos fallback listados para usuário {current_user.id}: {fallback_response.count} modelos")
            return fallback_response
            
    except Exception as e:
        logger.error(f"Erro crítico ao listar modelos para usuário {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get("/providers", response_model=ListProvidersResponse, summary="Listar provedores", tags=["ai"])
async def list_providers(
    unified_llm_service: UnifiedLLMService = Depends(get_llm_service)
) -> ListProvidersResponse:
    """
    Lista todos os provedores de LLM disponíveis na plataforma.
    
    Retorna informações sobre cada provedor incluindo
    status de disponibilidade e modelos suportados.
    
    Returns:
        ListProvidersResponse: Lista de provedores disponíveis
        
    Raises:
        HTTPException: 500 se erro interno do servidor
    """
    try:
        logger.info("Listagem de provedores solicitada")
        
        # Try to get providers from database via UnifiedLLMService
        try:
            provider_names = await unified_llm_service.get_available_providers()
            
            # Transform provider names to ProviderInfo objects
            providers_info = []
            for provider_name in provider_names:
                # Get model count for this provider
                try:
                    models = await unified_llm_service.get_available_models(provider=provider_name)
                    models_count = len(models)
                except Exception:
                    models_count = 0
                
                # Create ProviderInfo object
                provider_info = ProviderInfo(
                    id=provider_name,
                    name=provider_name.capitalize(),
                    description=f"Provedor {provider_name.capitalize()} com modelos de linguagem",
                    models_count=models_count,
                    status=ProviderStatus.operational,
                    documentation_url=_get_provider_documentation_url(provider_name)
                )
                providers_info.append(provider_info)
            
            logger.info(f"Provedores listados com sucesso: {len(providers_info)} provedores encontrados")
            return ListProvidersResponse(
                providers=providers_info,
                count=len(providers_info)
            )
            
        except Exception as db_error:
            logger.warning(f"Erro ao buscar provedores do banco de dados: {db_error}. Usando fallback.")
            
            # Fallback to enum-based providers if database fails
            return _get_fallback_providers_response()
            
    except Exception as e:
        logger.error(f"Erro ao listar provedores: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


def _get_provider_documentation_url(provider: str) -> Optional[str]:
    """
    Get documentation URL for a provider.
    
    Args:
        provider: Provider name
        
    Returns:
        Documentation URL if available, None otherwise
    """
    docs_mapping = {
        "openai": "https://platform.openai.com/docs",
        "claude": "https://docs.anthropic.com",
        "anthropic": "https://docs.anthropic.com", 
        "gemini": "https://ai.google.dev/docs",
        "google": "https://ai.google.dev/docs",
        "llama": "https://llama.meta.com/docs",
        "meta": "https://llama.meta.com/docs",
        "grok": "https://docs.x.ai",
        "deepseek": "https://platform.deepseek.com/docs",
        "tess": None  # Add when documentation is available
    }
    return docs_mapping.get(provider.lower())


def _get_fallback_providers_response() -> ListProvidersResponse:
    """
    Get fallback providers response when database is unavailable.
    
    Returns:
        ListProvidersResponse with hardcoded provider information
    """
    logger.info("Usando resposta de fallback para provedores")
    
    # Hardcoded provider information for fallback
    fallback_providers = [
        ProviderInfo(
            id="openai",
            name="OpenAI",
            description="Provedor OpenAI com modelos GPT",
            models_count=3,  # gpt-4o, gpt-4-turbo, gpt-3.5-turbo
            status=ProviderStatus.operational,
            documentation_url="https://platform.openai.com/docs"
        ),
        ProviderInfo(
            id="claude",
            name="Claude",
            description="Provedor Claude da Anthropic",
            models_count=3,  # opus, sonnet, haiku
            status=ProviderStatus.operational,
            documentation_url="https://docs.anthropic.com"
        ),
        ProviderInfo(
            id="gemini",
            name="Gemini",
            description="Provedor Gemini do Google",
            models_count=2,  # pro, flash
            status=ProviderStatus.operational,
            documentation_url="https://ai.google.dev/docs"
        ),
        ProviderInfo(
            id="llama",
            name="Llama",
            description="Provedor Llama da Meta",
            models_count=3,  # 3-70b, 3-8b, 2-70b
            status=ProviderStatus.operational,
            documentation_url="https://llama.meta.com/docs"
        ),
        ProviderInfo(
            id="grok",
            name="Grok",
            description="Provedor Grok da xAI",
            models_count=1,  # grok-1
            status=ProviderStatus.operational,
            documentation_url="https://docs.x.ai"
        ),
        ProviderInfo(
            id="deepseek",
            name="DeepSeek",
            description="Provedor DeepSeek",
            models_count=2,  # chat, coder
            status=ProviderStatus.operational,
            documentation_url="https://platform.deepseek.com/docs"
        ),
        ProviderInfo(
            id="tess",
            name="Tess",
            description="Provedor Tess",
            models_count=1,
            status=ProviderStatus.operational,
            documentation_url=None
        )
    ]
    
    return ListProvidersResponse(
        providers=fallback_providers,
        count=len(fallback_providers)
    )


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
    unified_llm_service: UnifiedLLMService = Depends(get_llm_service),
) -> GenerateTextResponse:
    """
    Gera texto usando um provedor específico de LLM.
    
    Este endpoint força o uso de um provedor específico,
    útil quando você precisa de recursos exclusivos de um modelo.
    
    Args:
        provider: Provedor específico a ser usado
        prompt: Texto de entrada para geração
        model: Modelo específico do provedor
        max_tokens: Limite máximo de tokens
        temperature: Controle de aleatoriedade
        presence_penalty: Penalidade de presença (OpenAI)
        frequency_penalty: Penalidade de frequência (OpenAI)
        top_p: Probabilidade acumulada para amostragem
        top_k: Número de tokens mais prováveis
        current_user: Usuário autenticado
        
    Returns:
        GenerateTextResponse: Texto gerado e metadados
        
    Raises:
        HTTPException: 400 se parâmetros inválidos
        HTTPException: 404 se provedor não encontrado
        HTTPException: 500 se erro interno do servidor
    """
    try:
        logger.info(f"Geração de texto com provedor específico '{provider}' solicitada por usuário {current_user.id}")
        
        if not prompt or len(prompt.strip()) == 0:
            logger.warning(f"Prompt vazio fornecido por usuário {current_user.id}")
            raise HTTPException(
                status_code=400,
                detail="Prompt não pode estar vazio"
            )

        # Validate model and provider against database if model is specified
        if model:
            try:
                is_valid = await unified_llm_service.validate_model_provider(
                    model_name=model,
                    provider=provider.value
                )
                
                if not is_valid:
                    logger.warning(f"Invalid model/provider combination for user {current_user.id}: {model}/{provider.value}")
                    # Try fallback validation with enums
                    try:
                        model_enum = ModelEnum(model)
                        # If we reach here, the enum is valid, but we should still log this as a fallback
                        logger.info(f"Using enum fallback validation for {model}/{provider.value}")
                    except ValueError:
                        raise HTTPException(
                            status_code=400,
                            detail={
                                "error": True,
                                "error_type": "invalid_model_provider",
                                "message": f"Invalid model/provider combination: {model}/{provider.value}",
                                "is_retryable": False,
                                "suggested_action": f"Check available models for {provider.value} using /{provider.value}/models endpoint"
                            }
                        )
            except Exception as validation_error:
                # If database validation fails, log and continue with existing enum validation
                logger.warning(f"Database validation failed for user {current_user.id}, using enum fallback: {str(validation_error)}")
                if model:
                    try:
                        model_enum = ModelEnum(model)
                        logger.info(f"Enum fallback validation succeeded for {model}/{provider.value}")
                    except ValueError:
                        raise HTTPException(
                            status_code=400,
                            detail={
                                "error": True,
                                "error_type": "invalid_model_provider",
                                "message": f"Invalid model/provider combination: {model}/{provider.value}",
                                "is_retryable": False,
                                "suggested_action": f"Check available models for {provider.value} using /{provider.value}/models endpoint"
                            }
                        )

        result = await get_llm_service().generate_text(
            prompt=prompt,
            provider=provider.value,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            presence_penalty=presence_penalty,
            frequency_penalty=frequency_penalty,
            top_p=top_p,
            top_k=top_k,
        )

        # Check if the result contains an error
        if hasattr(result, 'metadata') and result.metadata and result.metadata.get('error'):
            error_type = result.metadata.get('error_type', 'unknown_error')
            is_retryable = result.metadata.get('is_retryable', False)
            suggested_action = result.metadata.get('suggested_action', 'Please try again later.')
            
            # Map error types to appropriate HTTP status codes
            status_code = 500  # Default to internal server error
            
            if error_type in ['authentication_error', 'permission_denied']:
                status_code = 401
            elif error_type in ['invalid_request', 'unprocessable_entity']:
                status_code = 400
            elif error_type in ['model_not_found']:
                status_code = 404
            elif error_type in ['rate_limit_exceeded']:
                status_code = 429
            elif error_type in ['quota_exceeded']:
                status_code = 402  # Payment Required
            elif error_type in ['timeout_error', 'connection_error', 'internal_server_error']:
                status_code = 503  # Service Unavailable
            
            # Create detailed error response
            error_detail = {
                "error": True,
                "error_type": error_type,
                "message": result.metadata.get('error_message', str(result.content)),
                "is_retryable": is_retryable,
                "suggested_action": suggested_action,
                "provider": provider.value,
                "model": model,
                "timestamp": datetime.now().isoformat()
            }
            
            # Add retry-after header for rate limits
            headers = {}
            if error_type == 'rate_limit_exceeded':
                headers['Retry-After'] = '60'
            
            logger.error(f"LLM service returned error for user {current_user.id}: {error_type}", extra=error_detail)
            raise HTTPException(status_code=status_code, detail=error_detail, headers=headers)

        logger.info(f"Texto gerado com provedor '{provider}' para usuário {current_user.id}")
        return result
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except ValidationError as e:
        logger.warning(f"Validation error for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail={
                "error": True,
                "error_type": "validation_error",
                "message": "Invalid request parameters",
                "details": str(e),
                "is_retryable": False,
                "suggested_action": "Check your request parameters and try again."
            }
        )
    except LLMServiceError as e:
        logger.error(f"LLM service error for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail={
                "error": True,
                "error_type": "service_error",
                "message": "LLM service is temporarily unavailable",
                "details": str(e),
                "is_retryable": True,
                "suggested_action": "Please try again in a few minutes."
            }
        )
    except Exception as e:
        logger.error(f"Unexpected error during text generation for user {current_user.id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": True,
                "error_type": "internal_error",
                "message": "An unexpected error occurred",
                "is_retryable": False,
                "suggested_action": "Please try again or contact support if the issue persists."
            }
        )


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
) -> CountTokensResponse:
    """
    Conta tokens usando o tokenizador de um provedor específico.
    
    Útil quando você precisa da contagem exata de tokens
    para um provedor/modelo específico.
    
    Args:
        provider: Provedor específico para tokenização
        text: Texto para contar tokens
        model: Modelo específico para tokenização
        current_user: Usuário autenticado
        
    Returns:
        CountTokensResponse: Número de tokens e metadados
        
    Raises:
        HTTPException: 400 se parâmetros inválidos
        HTTPException: 404 se provedor não encontrado
        HTTPException: 500 se erro interno do servidor
    """
    try:
        logger.info(f"Contagem de tokens com provedor específico '{provider}' solicitada por usuário {current_user.id}")
        
        if not text:
            logger.warning(f"Texto vazio fornecido para contagem por usuário {current_user.id}")
            raise HTTPException(
                status_code=400,
                detail="Texto não pode estar vazio"
            )

        result = await get_llm_service().count_tokens(
            text=text,
            provider=provider.value,
            model=model,
        )

        logger.info(f"Tokens contados com provedor '{provider}' para usuário {current_user.id}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao contar tokens com provedor '{provider}' para usuário {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get("/{provider}/models", response_model=ListModelsResponse, summary="Listar modelos de provedor específico", tags=["ai"])
async def list_models_for_provider(
    provider: ProviderEnum = Path(
        ...,
        description="Nome do provedor",
        example="openai",
    ),
    current_user=Depends(get_current_user),
) -> ListModelsResponse:
    """
    Lista todos os modelos disponíveis para um provedor específico.
    
    Retorna informações detalhadas sobre modelos de um
    provedor específico, incluindo capacidades e limitações.
    
    Args:
        provider: Provedor específico
        current_user: Usuário autenticado
        
    Returns:
        ListModelsResponse: Lista de modelos do provedor
        
    Raises:
        HTTPException: 404 se provedor não encontrado
        HTTPException: 500 se erro interno do servidor
    """
    try:
        logger.info(f"Listagem de modelos para provedor '{provider}' solicitada por usuário {current_user.id}")
        
        result = await get_llm_service().list_models(provider=provider.value)

        logger.info(f"Modelos do provedor '{provider}' listados para usuário {current_user.id}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao listar modelos do provedor '{provider}' para usuário {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get("/usage")
async def get_llm_usage(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Obter estatísticas de uso de LLM do usuário"""
    # Implementação básica - você pode expandir conforme necessário
    return {
        "total_requests": 0,
        "total_tokens": 0,
        "this_month": {
            "requests": 0,
            "tokens": 0,
            "cost": 0.0
        },
        "providers": {},
        "models": {}
    }
