"""
Endpoints da API para interação com LLMs.

Este módulo define os endpoints da API para interação com
Modelos de Linguagem de Grande Escala (LLMs).
"""

from typing import Dict, Any, List, Optional, Union
from fastapi import APIRouter, Depends, HTTPException, Body, Query, Path, Form
from pydantic import BaseModel, Field
from enum import Enum

from src.synapse.api.deps import get_current_user
from src.synapse.core.llm import unified_service
from src.synapse.logging import get_logger
from src.synapse.schemas.llm import LLMProvider
from src.synapse.api.v1.endpoints.llm.schemas import (
    GenerateTextRequest, 
    CountTokensRequest, 
    GenerateTextWithProviderRequest,
    GenerateTextResponse,
    CountTokensResponse,
    ListModelsResponse,
    ListProvidersResponse
)

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


@router.post("/generate", response_model=GenerateTextResponse, tags=["llm"])
async def generate_text(
    prompt: str = Query(
        ..., 
        description="Texto de entrada para o modelo processar",
        example="Explique o conceito de machine learning em termos simples."
    ),
    provider: Optional[ProviderEnum] = Query(
        None, 
        description="Provedor LLM a ser usado",
        example="openai"
    ),
    model: Optional[str] = Query(
        None, 
        description="Modelo específico do provedor",
        example="gpt-4o"
    ),
    max_tokens: Optional[int] = Query(
        1000, 
        description="Limite máximo de tokens na resposta",
        ge=1,
        le=8192,
        example=500
    ),
    temperature: Optional[float] = Query(
        0.7, 
        description="Controle de aleatoriedade (0.0-1.0)",
        ge=0.0,
        le=1.0,
        example=0.7
    ),
    top_p: Optional[float] = Query(
        None,
        description="Probabilidade acumulada para amostragem de núcleo (0.0-1.0)",
        ge=0.0,
        le=1.0,
        example=0.95
    ),
    top_k: Optional[int] = Query(
        None,
        description="Número de tokens mais prováveis a considerar",
        ge=1,
        le=100,
        example=40
    ),
    use_cache: Optional[bool] = Query(
        None,
        description="Se deve usar cache para respostas idênticas",
        example=True
    ),
    current_user = Depends(get_current_user)
):
    """
    Gera texto a partir de um prompt usando o provedor de LLM escolhido.
    
    ## Função
    Este endpoint permite gerar texto usando qualquer provedor de LLM disponível na plataforma.
    É o principal endpoint para interações com modelos de linguagem.
    
    ## Quando Usar
    - Quando precisar gerar conteúdo de texto baseado em um prompt
    - Quando quiser obter respostas de um LLM específico
    - Para criar resumos, explicações, traduções ou qualquer geração de texto
    
    ## Parâmetros Importantes
    - **prompt**: O texto que você envia para o modelo processar (obrigatório)
    - **provider**: Qual provedor de LLM usar (ex: openai, claude, gemini)
    - **model**: Modelo específico a ser usado (ex: gpt-4o, claude-3-opus)
    - **temperature**: Controla a aleatoriedade das respostas (0.0 = determinístico, 1.0 = muito aleatório)
    - **max_tokens**: Limite máximo de tokens na resposta
    
    ## Resultado Esperado
    Retorna um objeto JSON contendo:
    - O texto gerado pelo modelo
    - Informações sobre o provedor e modelo utilizados
    - Estatísticas de uso (tokens)
    - Metadados adicionais sobre a geração
    
    ## Exemplo de Uso
    ```python
    import requests
    
    url = "https://api.synapscale.com/api/v1/llm/generate"
    headers = {"Authorization": "Bearer seu_token"}
    params = {
        "prompt": "Explique o conceito de machine learning em termos simples.",
        "provider": "openai",
        "model": "gpt-4o",
        "max_tokens": 500,
        "temperature": 0.7
    }
    
    response = requests.post(url, params=params, headers=headers)
    print(response.json()["text"])
    ```
    """
    try:
        logger.info(f"Requisição de geração de texto recebida: {prompt[:50]}...")
        
        result = await unified_service.generate_text(
            prompt=prompt,
            provider=provider.value if provider else None,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            use_cache=use_cache
        )
        
        return result
    except Exception as e:
        logger.error(f"Erro ao gerar texto: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/count-tokens", response_model=CountTokensResponse, tags=["llm"])
async def count_tokens(
    text: str = Query(
        ...,
        description="Texto para contar os tokens",
        example="Este é um exemplo de texto para contar tokens."
    ),
    provider: Optional[ProviderEnum] = Query(
        None,
        description="Provedor LLM a ser usado para a contagem",
        example="openai"
    ),
    model: Optional[str] = Query(
        None,
        description="Modelo específico a ser usado para a contagem",
        example="gpt-4o"
    ),
    current_user = Depends(get_current_user)
):
    """
    Conta o número de tokens em um texto usando o tokenizador do provedor especificado.
    
    ## Função
    Este endpoint calcula quantos tokens existem em um texto, usando o mesmo tokenizador 
    que o modelo de LLM utilizaria. Isso é útil para estimar custos e verificar limites.
    
    ## Quando Usar
    - Antes de enviar textos muito longos para verificar se estão dentro dos limites do modelo
    - Para estimar custos de uso de APIs de LLM que cobram por token
    - Para otimizar prompts e garantir que caibam no contexto do modelo
    
    ## Parâmetros Importantes
    - **text**: O texto para contar os tokens (obrigatório)
    - **provider**: Qual provedor de LLM usar para a contagem (ex: openai, claude)
    - **model**: Modelo específico a ser usado para a contagem
    
    ## Resultado Esperado
    Retorna um objeto JSON contendo:
    - O número total de tokens no texto
    - Informações sobre o provedor e modelo utilizados para a contagem
    - Metadados adicionais sobre a tokenização
    
    ## Exemplo de Uso
    ```python
    import requests
    
    url = "https://api.synapscale.com/api/v1/llm/count-tokens"
    headers = {"Authorization": "Bearer seu_token"}
    params = {
        "text": "Este é um exemplo de texto para contar tokens.",
        "provider": "openai"
    }
    
    response = requests.post(url, params=params, headers=headers)
    print(f"Número de tokens: {response.json()['token_count']}")
    ```
    """
    try:
        logger.info(f"Requisição de contagem de tokens recebida: {text[:50]}...")
        
        result = await unified_service.count_tokens(
            text=text,
            provider=provider.value if provider else None,
            model=model
        )
        
        return result
    except Exception as e:
        logger.error(f"Erro ao contar tokens: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models", response_model=ListModelsResponse, tags=["llm"])
async def list_models(
    provider: Optional[ProviderEnum] = Query(
        None, 
        description="Filtrar por provedor específico",
        example="openai"
    ),
    current_user = Depends(get_current_user)
):
    """
    Lista todos os modelos de LLM disponíveis na plataforma.
    
    ## Função
    Este endpoint retorna informações detalhadas sobre todos os modelos de LLM 
    disponíveis para uso, incluindo suas capacidades e características.
    
    ## Quando Usar
    - Quando precisar descobrir quais modelos estão disponíveis
    - Para comparar capacidades entre diferentes modelos
    - Antes de fazer uma chamada de geração, para escolher o modelo mais adequado
    
    ## Parâmetros Importantes
    - **provider**: Filtrar a lista para mostrar apenas modelos de um provedor específico (opcional)
    
    ## Resultado Esperado
    Retorna um objeto JSON contendo:
    - Lista de modelos disponíveis, agrupados por provedor
    - Para cada modelo: ID, nome, capacidades, tamanho de contexto, etc.
    - Status de disponibilidade de cada modelo
    
    ## Exemplo de Uso
    ```python
    import requests
    
    # Listar todos os modelos
    url = "https://api.synapscale.com/api/v1/llm/models"
    headers = {"Authorization": "Bearer seu_token"}
    
    response = requests.get(url, headers=headers)
    
    # Ou filtrar por provedor
    url = "https://api.synapscale.com/api/v1/llm/models?provider=openai"
    response = requests.get(url, headers=headers)
    
    for provider, models in response.json()["models"].items():
        print(f"Provedor: {provider}")
        for model in models:
            print(f"  - {model['name']}")
    ```
    """
    try:
        provider_value = provider.value if provider else None
        logger.info(f"Requisição de listagem de modelos recebida, provedor: {provider_value or 'todos'}")
        
        result = await unified_service.list_models(provider=provider_value)
        
        return result
    except Exception as e:
        logger.error(f"Erro ao listar modelos: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/providers", response_model=ListProvidersResponse, tags=["llm"])
async def list_providers():
    """
    Lista todos os provedores de LLM disponíveis na plataforma.
    
    ## Função
    Este endpoint retorna informações sobre todos os provedores de LLM 
    integrados à plataforma, incluindo seus status e capacidades.
    
    ## Quando Usar
    - Quando precisar saber quais provedores estão disponíveis
    - Para verificar o status operacional de cada provedor
    - Para comparar capacidades entre diferentes provedores
    
    ## Resultado Esperado
    Retorna um objeto JSON contendo:
    - Lista de provedores disponíveis
    - Para cada provedor: ID, nome, descrição, status
    - Número de modelos disponíveis por provedor
    - Links para documentação e websites oficiais
    
    ## Exemplo de Uso
    ```python
    import requests
    
    url = "https://api.synapscale.com/api/v1/llm/providers"
    headers = {"Authorization": "Bearer seu_token"}
    
    response = requests.get(url, headers=headers)
    
    for provider in response.json()["providers"]:
        print(f"{provider['name']}: {provider['status']}")
        print(f"  Modelos disponíveis: {provider['models_count']}")
    ```
    """
    try:
        logger.info("Requisição de listagem de provedores recebida")
        
        result = unified_service.list_providers()
        
        return result
    except Exception as e:
        logger.error(f"Erro ao listar provedores: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{provider}/generate", response_model=GenerateTextResponse, tags=["llm"])
async def generate_text_with_provider(
    provider: ProviderEnum = Path(
        ..., 
        description="Nome do provedor",
        example="openai"
    ),
    prompt: str = Query(
        ..., 
        description="Texto de entrada para o modelo processar",
        example="Explique o conceito de machine learning em termos simples."
    ),
    model: Optional[str] = Query(
        None, 
        description="Modelo específico do provedor",
        example="gpt-4o"
    ),
    max_tokens: Optional[int] = Query(
        1000, 
        description="Limite máximo de tokens na resposta",
        ge=1,
        le=8192,
        example=500
    ),
    temperature: Optional[float] = Query(
        0.7, 
        description="Controle de aleatoriedade (0.0-1.0)",
        ge=0.0,
        le=1.0,
        example=0.7
    ),
    presence_penalty: Optional[float] = Query(
        None,
        description="Penalidade de presença (apenas OpenAI)",
        ge=-2.0,
        le=2.0,
        example=0.2
    ),
    frequency_penalty: Optional[float] = Query(
        None,
        description="Penalidade de frequência (apenas OpenAI)",
        ge=-2.0,
        le=2.0,
        example=0.3
    ),
    top_p: Optional[float] = Query(
        None,
        description="Probabilidade acumulada para amostragem de núcleo (0.0-1.0)",
        ge=0.0,
        le=1.0,
        example=0.95
    ),
    top_k: Optional[int] = Query(
        None,
        description="Número de tokens mais prováveis a considerar",
        ge=1,
        le=100,
        example=40
    ),
    current_user = Depends(get_current_user)
):
    """
    Gera texto a partir de um prompt usando um provedor específico de LLM.
    
    ## Função
    Este endpoint permite gerar texto usando um provedor específico de LLM,
    com acesso a parâmetros específicos desse provedor.
    
    ## Quando Usar
    - Quando precisar usar parâmetros específicos de um provedor
    - Quando quiser garantir que um provedor específico seja usado
    - Para testar ou comparar resultados de um provedor específico
    
    ## Parâmetros Importantes
    - **provider**: O provedor de LLM a ser usado (especificado na URL)
    - **prompt**: O texto que você envia para o modelo processar (obrigatório)
    - **model**: Modelo específico a ser usado
    - **temperature**: Controla a aleatoriedade das respostas
    - **max_tokens**: Limite máximo de tokens na resposta
    - **presence_penalty**: Penalidade para tokens já presentes (OpenAI)
    - **frequency_penalty**: Penalidade para tokens frequentes (OpenAI)
    - **top_p**: Probabilidade acumulada para amostragem de núcleo
    - **top_k**: Número de tokens mais prováveis a considerar
    
    ## Resultado Esperado
    Retorna um objeto JSON contendo:
    - O texto gerado pelo modelo
    - Informações sobre o provedor e modelo utilizados
    - Estatísticas de uso (tokens)
    - Metadados adicionais sobre a geração
    
    ## Exemplo de Uso
    ```python
    import requests
    
    url = "https://api.synapscale.com/api/v1/llm/openai/generate"
    headers = {"Authorization": "Bearer seu_token"}
    params = {
        "prompt": "Explique o conceito de machine learning em termos simples.",
        "model": "gpt-4o",
        "max_tokens": 500,
        "temperature": 0.7,
        "presence_penalty": 0.2,
        "frequency_penalty": 0.3
    }
    
    response = requests.post(url, params=params, headers=headers)
    print(response.json()["text"])
    ```
    """
    try:
        logger.info(f"Requisição de geração de texto com provedor {provider.value} recebida: {prompt[:50]}...")
        
        # Construir dicionário de parâmetros específicos do provedor
        provider_params = {}
        if presence_penalty is not None:
            provider_params["presence_penalty"] = presence_penalty
        if frequency_penalty is not None:
            provider_params["frequency_penalty"] = frequency_penalty
        if top_p is not None:
            provider_params["top_p"] = top_p
        if top_k is not None:
            provider_params["top_k"] = top_k
        
        result = await unified_service.generate_text(
            prompt=prompt,
            provider=provider.value,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            **provider_params
        )
        
        return result
    except Exception as e:
        logger.error(f"Erro ao gerar texto com provedor {provider.value}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{provider}/count-tokens", response_model=CountTokensResponse, tags=["llm"])
async def count_tokens_with_provider(
    provider: ProviderEnum = Path(
        ..., 
        description="Nome do provedor",
        example="openai"
    ),
    text: str = Query(
        ...,
        description="Texto para contar os tokens",
        example="Este é um exemplo de texto para contar tokens."
    ),
    model: Optional[str] = Query(
        None,
        description="Modelo específico a ser usado para a contagem",
        example="gpt-4o"
    ),
    current_user = Depends(get_current_user)
):
    """
    Conta o número de tokens em um texto usando o tokenizador de um provedor específico.
    
    ## Função
    Este endpoint calcula quantos tokens existem em um texto, usando o tokenizador
    de um provedor específico de LLM.
    
    ## Quando Usar
    - Quando precisar contar tokens usando um tokenizador específico
    - Para verificar diferenças de contagem entre diferentes provedores
    - Para estimar custos de uso de um provedor específico
    
    ## Parâmetros Importantes
    - **provider**: O provedor de LLM a ser usado (especificado na URL)
    - **text**: O texto para contar os tokens (obrigatório)
    - **model**: Modelo específico a ser usado para a contagem
    
    ## Resultado Esperado
    Retorna um objeto JSON contendo:
    - O número total de tokens no texto
    - Informações sobre o provedor e modelo utilizados para a contagem
    - Metadados adicionais sobre a tokenização
    
    ## Exemplo de Uso
    ```python
    import requests
    
    url = "https://api.synapscale.com/api/v1/llm/openai/count-tokens"
    headers = {"Authorization": "Bearer seu_token"}
    params = {
        "text": "Este é um exemplo de texto para contar tokens.",
        "model": "gpt-4o"
    }
    
    response = requests.post(url, params=params, headers=headers)
    print(f"Número de tokens: {response.json()['token_count']}")
    ```
    """
    try:
        logger.info(f"Requisição de contagem de tokens com provedor {provider.value} recebida: {text[:50]}...")
        
        result = await unified_service.count_tokens(
            text=text,
            provider=provider.value,
            model=model
        )
        
        return result
    except Exception as e:
        logger.error(f"Erro ao contar tokens com provedor {provider.value}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{provider}/models", response_model=ListModelsResponse, tags=["llm"])
async def list_models_for_provider(
    provider: ProviderEnum = Path(
        ..., 
        description="Nome do provedor",
        example="openai"
    ),
    current_user = Depends(get_current_user)
):
    """
    Lista todos os modelos disponíveis para um provedor específico.
    
    ## Função
    Este endpoint retorna informações detalhadas sobre todos os modelos
    disponíveis para um provedor específico de LLM.
    
    ## Quando Usar
    - Quando precisar saber quais modelos estão disponíveis para um provedor específico
    - Para comparar capacidades entre diferentes modelos do mesmo provedor
    - Antes de fazer uma chamada de geração, para escolher o modelo mais adequado
    
    ## Parâmetros Importantes
    - **provider**: O provedor de LLM a ser consultado (especificado na URL)
    
    ## Resultado Esperado
    Retorna um objeto JSON contendo:
    - Lista de modelos disponíveis para o provedor especificado
    - Para cada modelo: ID, nome, capacidades, tamanho de contexto, etc.
    - Status de disponibilidade de cada modelo
    
    ## Exemplo de Uso
    ```python
    import requests
    
    url = "https://api.synapscale.com/api/v1/llm/openai/models"
    headers = {"Authorization": "Bearer seu_token"}
    
    response = requests.get(url, headers=headers)
    
    for model in response.json()["models"]["openai"]:
        print(f"Modelo: {model['name']}")
        print(f"  Capacidades: {', '.join(model['capabilities'])}")
    ```
    """
    try:
        logger.info(f"Requisição de listagem de modelos para provedor {provider.value} recebida")
        
        result = await unified_service.list_models(provider=provider.value)
        
        return result
    except Exception as e:
        logger.error(f"Erro ao listar modelos para provedor {provider.value}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
