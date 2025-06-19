"""
Endpoints da API para interação com LLMs
Criado por José - um desenvolvedor Full Stack
API completa para integração com modelos de linguagem

Este módulo define os endpoints da API para interação com
Modelos de Linguagem de Grande Escala (LLMs).
"""

import logging
from typing import Optional, Dict, Any

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
)
from synapse.schemas.llm import (
    LLMGenerateRequest as GenerateRequest,
    LLMChatRequest as ChatRequest,
    LLMResponse
)
from synapse.schemas.user_variable import UserVariableCreate
from synapse.models.user import User

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


@router.post("/generate", response_model=LLMResponse, tags=["llm"])
async def generate_text(
    request: GenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Gera texto usando LLM com API key específica do usuário (se disponível)
    
    Automaticamente usa API keys pessoais do usuário quando configuradas,
    com fallback para API keys globais do sistema.
    """
    try:
        # Usar novo serviço que integra user_variables
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
        
        return response
    except Exception as e:
        logger.error(f"Erro na geração de texto: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat", response_model=LLMResponse, tags=["llm"])
async def chat_completion(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Chat completion usando API key específica do usuário (se disponível)
    
    Automaticamente usa API keys pessoais do usuário quando configuradas,
    com fallback para API keys globais do sistema.
    """
    try:
        # Usar novo serviço que integra user_variables
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
        
        return response
    except Exception as e:
        logger.error(f"Erro no chat completion: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/count-tokens", response_model=CountTokensResponse, summary="Contar tokens", tags=["llm", "Tokens"])
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


@router.get("/models", response_model=ListModelsResponse, summary="Listar modelos", tags=["llm"])
async def list_models(
    provider: Optional[ProviderEnum] = Query(
        None,
        description="Filtrar por provedor específico",
        example="openai",
    ),
    current_user=Depends(get_current_user),
) -> ListModelsResponse:
    """
    Lista todos os modelos de LLM disponíveis na plataforma.
    
    Retorna uma lista de modelos com informações sobre
    capacidades e limites de cada um.
    
    Args:
        provider: Filtrar por provedor específico
        current_user: Usuário autenticado
        
    Returns:
        ListModelsResponse: Lista de modelos disponíveis
        
    Raises:
        HTTPException: 500 se erro interno do servidor
    """
    try:
        logger.info(f"Listagem de modelos solicitada por usuário {current_user.id} - provider: {provider}")
        
        result = await llm_service.list_models(
            provider=provider.value if provider else None
        )

        logger.info(f"Modelos listados para usuário {current_user.id}: {len(getattr(result, 'models', []))} modelos")
        return result
    except Exception as e:
        logger.error(f"Erro ao listar modelos para usuário {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get("/providers", response_model=ListProvidersResponse, summary="Listar provedores", tags=["llm", "Providers"])
async def list_providers() -> ListProvidersResponse:
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
        result = llm_service.get_available_providers()
        return ListProvidersResponse(**result)
    except Exception as e:
        logger.error(f"Erro ao listar provedores: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.post("/{provider}/generate", response_model=GenerateTextResponse, summary="Gerar texto com provedor específico", tags=["llm"])
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

        result = await llm_service.generate_text(
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

        logger.info(f"Texto gerado com provedor '{provider}' para usuário {current_user.id}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao gerar texto com provedor '{provider}' para usuário {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.post("/{provider}/count-tokens", response_model=CountTokensResponse, summary="Contar tokens com provedor específico", tags=["llm", "Tokens"])
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

        result = await llm_service.count_tokens(
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


@router.get("/{provider}/models", response_model=ListModelsResponse, summary="Listar modelos de provedor específico", tags=["llm"])
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
        
        result = await llm_service.list_models(provider=provider.value)

        logger.info(f"Modelos do provedor '{provider}' listados para usuário {current_user.id}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao listar modelos do provedor '{provider}' para usuário {current_user.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")
