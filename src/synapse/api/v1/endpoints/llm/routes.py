"""
Endpoints da API para interação com LLMs.

Este módulo define os endpoints da API para interação com
Modelos de Linguagem de Grande Escala (LLMs).
"""

from typing import Dict, Any, List, Optional, Union
from fastapi import APIRouter, Depends, HTTPException, Body, Query, Path
from pydantic import BaseModel, Field

from synapse.api.deps import get_current_user
from synapse.core.llm import unified_service
from synapse.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()


class GenerateTextRequest(BaseModel):
    """Modelo para requisição de geração de texto."""
    
    prompt: str = Field(..., description="Texto de entrada para o modelo")
    provider: Optional[str] = Field(None, description="Provedor de LLM a ser usado")
    model: Optional[str] = Field(None, description="Modelo específico a ser usado")
    max_tokens: Optional[int] = Field(1000, description="Número máximo de tokens a gerar")
    temperature: Optional[float] = Field(0.7, description="Temperatura para amostragem (0.0-1.0)")
    top_p: Optional[float] = Field(0.95, description="Valor de top-p para amostragem nucleus")
    top_k: Optional[int] = Field(40, description="Valor de top-k para amostragem")
    use_cache: Optional[bool] = Field(True, description="Se deve usar o cache (se disponível)")
    
    class Config:
        schema_extra = {
            "example": {
                "prompt": "Explique o conceito de machine learning em termos simples.",
                "provider": "claude",
                "model": "claude-3-sonnet-20240229",
                "max_tokens": 500,
                "temperature": 0.7
            }
        }


class CountTokensRequest(BaseModel):
    """Modelo para requisição de contagem de tokens."""
    
    text: str = Field(..., description="Texto para contar tokens")
    provider: Optional[str] = Field(None, description="Provedor de LLM a ser usado")
    model: Optional[str] = Field(None, description="Modelo específico a ser usado")
    
    class Config:
        schema_extra = {
            "example": {
                "text": "Este é um exemplo de texto para contar tokens.",
                "provider": "claude"
            }
        }


@router.post("/generate", response_model=Dict[str, Any], tags=["llm"])
async def generate_text(
    request: GenerateTextRequest = Body(...),
    current_user = Depends(get_current_user)
):
    """
    Gera texto a partir de um prompt usando o provedor padrão ou especificado.
    
    - **prompt**: Texto de entrada para o modelo
    - **provider**: Provedor de LLM a ser usado (opcional)
    - **model**: Modelo específico a ser usado (opcional)
    - **max_tokens**: Número máximo de tokens a gerar (padrão: 1000)
    - **temperature**: Temperatura para amostragem (0.0-1.0) (padrão: 0.7)
    - **top_p**: Valor de top-p para amostragem nucleus (padrão: 0.95)
    - **top_k**: Valor de top-k para amostragem (padrão: 40)
    - **use_cache**: Se deve usar o cache (padrão: True)
    
    Retorna o texto gerado e metadados sobre a geração.
    """
    try:
        logger.info(f"Requisição de geração de texto recebida: {request.prompt[:50]}...")
        
        result = await unified_service.generate_text(
            prompt=request.prompt,
            provider=request.provider,
            model=request.model,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            top_p=request.top_p,
            top_k=request.top_k,
            use_cache=request.use_cache
        )
        
        return result
    except Exception as e:
        logger.error(f"Erro ao gerar texto: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/count-tokens", response_model=Dict[str, Any], tags=["llm"])
async def count_tokens(
    request: CountTokensRequest = Body(...),
    current_user = Depends(get_current_user)
):
    """
    Conta o número de tokens em um texto.
    
    - **text**: Texto para contar tokens
    - **provider**: Provedor de LLM a ser usado (opcional)
    - **model**: Modelo específico a ser usado (opcional)
    
    Retorna a contagem de tokens e metadados.
    """
    try:
        logger.info(f"Requisição de contagem de tokens recebida: {request.text[:50]}...")
        
        result = await unified_service.count_tokens(
            text=request.text,
            provider=request.provider,
            model=request.model
        )
        
        return result
    except Exception as e:
        logger.error(f"Erro ao contar tokens: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models", response_model=Dict[str, Any], tags=["llm"])
async def list_models(
    provider: Optional[str] = Query(None, description="Filtrar por provedor específico"),
    current_user = Depends(get_current_user)
):
    """
    Lista todos os modelos disponíveis.
    
    - **provider**: Filtrar por provedor específico (opcional)
    
    Retorna a lista de modelos agrupados por provedor.
    """
    try:
        logger.info(f"Requisição de listagem de modelos recebida, provedor: {provider or 'todos'}")
        
        result = await unified_service.list_models(provider=provider)
        
        return result
    except Exception as e:
        logger.error(f"Erro ao listar modelos: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/providers", response_model=Dict[str, Any], tags=["llm"])
async def list_providers():
    """
    Lista todos os provedores disponíveis.
    
    Retorna a lista de provedores disponíveis e suas capacidades.
    """
    try:
        logger.info("Requisição de listagem de provedores recebida")
        
        result = unified_service.list_providers()
        
        return result
    except Exception as e:
        logger.error(f"Erro ao listar provedores: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/providers-test", response_model=Dict[str, Any], tags=["llm"])
async def list_providers_test():
    """
    Endpoint de teste para listar provedores sem autenticação.
    """
    try:
        logger.info("Requisição de teste de listagem de provedores recebida")
        
        result = unified_service.list_providers()
        
        return result
    except Exception as e:
        logger.error(f"Erro ao listar provedores (teste): {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/test-providers", response_model=Dict[str, Any], tags=["llm"])
async def test_list_providers():
    """
    Endpoint temporário para testar listagem de provedores sem autenticação.
    """
    try:
        logger.info("Requisição de teste de listagem de provedores recebida")
        
        result = unified_service.list_providers()
        
        return result
    except Exception as e:
        logger.error(f"Erro ao listar provedores (teste): {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{provider}/generate", response_model=Dict[str, Any], tags=["llm"])
async def generate_text_with_provider(
    provider: str = Path(..., description="Nome do provedor"),
    request: GenerateTextRequest = Body(...),
    current_user = Depends(get_current_user)
):
    """
    Gera texto a partir de um prompt usando o provedor especificado.
    
    - **provider**: Nome do provedor (ex: "claude", "gemini")
    - **prompt**: Texto de entrada para o modelo
    - **model**: Modelo específico a ser usado (opcional)
    - **max_tokens**: Número máximo de tokens a gerar (padrão: 1000)
    - **temperature**: Temperatura para amostragem (0.0-1.0) (padrão: 0.7)
    - **top_p**: Valor de top-p para amostragem nucleus (padrão: 0.95)
    - **top_k**: Valor de top-k para amostragem (padrão: 40)
    - **use_cache**: Se deve usar o cache (padrão: True)
    
    Retorna o texto gerado e metadados sobre a geração.
    """
    try:
        logger.info(f"Requisição de geração de texto com provedor {provider} recebida: {request.prompt[:50]}...")
        
        # Sobrescrever o provedor na requisição com o do path
        request_dict = request.dict()
        request_dict["provider"] = provider
        
        result = await unified_service.generate_text(**request_dict)
        
        return result
    except Exception as e:
        logger.error(f"Erro ao gerar texto com provedor {provider}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{provider}/count-tokens", response_model=Dict[str, Any], tags=["llm"])
async def count_tokens_with_provider(
    provider: str = Path(..., description="Nome do provedor"),
    request: CountTokensRequest = Body(...),
    current_user = Depends(get_current_user)
):
    """
    Conta o número de tokens em um texto usando o provedor especificado.
    
    - **provider**: Nome do provedor (ex: "claude", "gemini")
    - **text**: Texto para contar tokens
    - **model**: Modelo específico a ser usado (opcional)
    
    Retorna a contagem de tokens e metadados.
    """
    try:
        logger.info(f"Requisição de contagem de tokens com provedor {provider} recebida: {request.text[:50]}...")
        
        result = await unified_service.count_tokens(
            text=request.text,
            provider=provider,
            model=request.model
        )
        
        return result
    except Exception as e:
        logger.error(f"Erro ao contar tokens com provedor {provider}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{provider}/models", response_model=Dict[str, Any], tags=["llm"])
async def list_models_for_provider(
    provider: str = Path(..., description="Nome do provedor"),
    current_user = Depends(get_current_user)
):
    """
    Lista os modelos disponíveis para o provedor especificado.
    
    - **provider**: Nome do provedor (ex: "claude", "gemini")
    
    Retorna a lista de modelos para o provedor.
    """
    try:
        logger.info(f"Requisição de listagem de modelos para provedor {provider} recebida")
        
        result = await unified_service.list_models(provider=provider)
        
        return result
    except Exception as e:
        logger.error(f"Erro ao listar modelos para provedor {provider}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
