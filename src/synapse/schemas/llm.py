"""Esquemas para integração com modelos de linguagem (LLMs).

Este módulo contém os esquemas para requisições e respostas
relacionadas à geração de texto, contagem de tokens e informações
sobre modelos e provedores disponíveis.
"""

from enum import Enum
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field


class LLMCapability(str, Enum):
    """Capacidades dos modelos LLM."""

    TEXT = "text"
    VISION = "vision"
    FUNCTION_CALLING = "function_calling"
    CODE = "code"
    REASONING = "reasoning"
    EMBEDDING = "embedding"


class LLMProvider(str, Enum):
    """Provedores de LLM disponíveis."""
    
    OPENAI = "openai"
    CLAUDE = "claude"
    GEMINI = "gemini"
    LLAMA = "llama"
    GROK = "grok"
    DEEPSEEK = "deepseek"
    TESS = "tess"
    OTHER = "outro"


class OpenAIModel(str, Enum):
    """Modelos disponíveis da OpenAI."""
    
    GPT_4O = "gpt-4o"
    GPT_4_TURBO = "gpt-4-turbo"
    GPT_4 = "gpt-4"
    GPT_35_TURBO = "gpt-3.5-turbo"
    OTHER = "outro"


class ClaudeModel(str, Enum):
    """Modelos disponíveis da Anthropic Claude."""
    
    CLAUDE_3_OPUS = "claude-3-opus-20240229"
    CLAUDE_3_SONNET = "claude-3-sonnet-20240229"
    CLAUDE_3_HAIKU = "claude-3-haiku-20240307"
    OTHER = "outro"


class GeminiModel(str, Enum):
    """Modelos disponíveis do Google Gemini."""
    
    GEMINI_15_PRO = "gemini-1.5-pro"
    GEMINI_15_FLASH = "gemini-1.5-flash"
    GEMINI_10_PRO = "gemini-1.0-pro"
    OTHER = "outro"


class LlamaModel(str, Enum):
    """Modelos disponíveis do Llama."""
    
    LLAMA_3_70B = "llama-3-70b"
    LLAMA_3_8B = "llama-3-8b"
    LLAMA_2_70B = "llama-2-70b"
    OTHER = "outro"


class LLMModelInfo(BaseModel):
    """Informações sobre um modelo LLM."""

    id: str = Field(..., description="Identificador único do modelo")
    provider: str = Field(..., description="Provedor do modelo (ex: openai, claude)")
    name: str = Field(..., description="Nome amigável do modelo")
    capabilities: List[str] = Field(
        default_factory=list, description="Lista de capacidades do modelo"
    )
    context_window: int = Field(
        default=0, description="Tamanho máximo do contexto em tokens"
    )
    token_limit: int = Field(
        default=0, description="Limite de tokens na resposta"
    )
    description: Optional[str] = Field(
        None, description="Descrição detalhada do modelo"
    )
    pricing: Optional[Dict[str, float]] = Field(
        None, description="Informações de preço (por 1K tokens)"
    )


class LLMProviderInfo(BaseModel):
    """Informações sobre um provedor LLM."""

    id: str = Field(..., description="Identificador único do provedor")
    name: str = Field(..., description="Nome amigável do provedor")
    description: str = Field(..., description="Descrição do provedor")
    status: str = Field(..., description="Status do provedor (active, inactive)")
    models_count: int = Field(
        default=0, description="Número de modelos disponíveis"
    )
    website: Optional[str] = Field(
        None, description="Website do provedor"
    )
    documentation: Optional[str] = Field(
        None, description="Link para documentação"
    )


class LLMGenerateRequest(BaseModel):
    """Requisição para geração de texto."""

    prompt: str = Field(
        ..., description="Texto de entrada para o modelo (obrigatório)"
    )
    provider: Optional[LLMProvider] = Field(
        None, description="Provedor LLM a ser usado (opcional, padrão: openai)"
    )
    model: Optional[str] = Field(
        None, description="Modelo específico do provedor (opcional)"
    )
    temperature: Optional[float] = Field(
        0.7, description="Controle de aleatoriedade (0.0-1.0, padrão: 0.7)"
    )
    max_tokens: Optional[int] = Field(
        1000, description="Limite de tokens na resposta (padrão: 1000)"
    )
    top_p: Optional[float] = Field(
        1.0, description="Controle de diversidade via amostragem nucleus (0.0-1.0)"
    )
    frequency_penalty: Optional[float] = Field(
        0.0, description="Reduz repetições de palavras (-2.0 a 2.0)"
    )
    presence_penalty: Optional[float] = Field(
        0.0, description="Incentiva novos tópicos (-2.0 a 2.0)"
    )
    stop: Optional[Union[str, List[str]]] = Field(
        None, description="Sequências que indicam fim da geração"
    )
    stream: Optional[bool] = Field(
        False, description="Se verdadeiro, retorna tokens à medida que são gerados"
    )
    functions: Optional[List[Dict]] = Field(
        None, description="Funções disponíveis para function calling"
    )
    function_call: Optional[Union[str, Dict]] = Field(
        None, description="Controle de function calling"
    )
    response_format: Optional[Dict] = Field(
        None, description="Formato desejado para a resposta"
    )
    seed: Optional[int] = Field(
        None, description="Seed para determinismo"
    )
    tools: Optional[List[Dict]] = Field(
        None, description="Ferramentas disponíveis para o modelo"
    )
    tool_choice: Optional[Union[str, Dict]] = Field(
        None, description="Controle de escolha de ferramentas"
    )
    extra_params: Optional[Dict] = Field(
        None, description="Parâmetros adicionais específicos do provedor"
    )


class LLMGenerateResponse(BaseModel):
    """Resposta da geração de texto."""

    text: str = Field(..., description="Texto gerado")
    provider: str = Field(..., description="Provedor usado")
    model: str = Field(..., description="Modelo usado")
    usage: Dict[str, int] = Field(
        ..., description="Informações de uso (tokens)"
    )
    finish_reason: Optional[str] = Field(
        None, description="Razão de término da geração"
    )
    function_call: Optional[Dict] = Field(
        None, description="Detalhes da chamada de função, se aplicável"
    )
    tool_calls: Optional[List[Dict]] = Field(
        None, description="Detalhes das chamadas de ferramentas, se aplicável"
    )
    metadata: Optional[Dict] = Field(
        None, description="Metadados adicionais"
    )


class LLMCountTokensRequest(BaseModel):
    """Requisição para contagem de tokens."""

    text: str = Field(..., description="Texto para contar tokens")
    provider: Optional[LLMProvider] = Field(
        None, description="Provedor LLM (opcional, padrão: openai)"
    )
    model: Optional[str] = Field(
        None, description="Modelo específico do provedor (opcional)"
    )


class LLMCountTokensResponse(BaseModel):
    """Resposta da contagem de tokens."""

    token_count: int = Field(..., description="Número de tokens")
    provider: str = Field(..., description="Provedor usado")
    model: str = Field(..., description="Modelo usado")
    metadata: Optional[Dict] = Field(
        None, description="Metadados adicionais"
    )
