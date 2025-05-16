"""
Cliente LLM para Groq API
Arquivo: src/llm_clients/groq_client.py

Este módulo implementa o `GroqClient`, uma classe que herda de `BaseLLMClient`
e fornece uma interface para interagir com os modelos hospedados na API da Groq
(ex: Llama, Mixtral, Gemma).

Utiliza a biblioteca oficial `groq` para Python.

Groq é conhecido por sua alta performance (tokens/segundo) na inferência de LLMs.

Boas Práticas e Considerações AI-Friendly:
- **Tratamento de Erros Específico:** Captura exceções da biblioteca Groq
  e as mapeia para as exceções personalizadas de `BaseLLMClient`.
- **Suporte a Streaming:** Implementa os métodos de streaming.
- **Seleção de Modelo:** O `model_name` deve corresponder aos modelos disponíveis na Groq API.
- **Referência Cruzada:**
    - Herda de `BaseLLMClient`.
    - Será registrado no `LLM_PROVIDER_MAP` em `loader.py`.
    - A API key é esperada da variável de ambiente (ex: `GROQ_API_KEY`).
"""
import os
from typing import List, Dict, Any, Optional, Iterator, AsyncIterator

try:
    import groq
    from groq import Groq, AsyncGroq # Groq SDK
except ImportError:
    raise ImportError(
        "A biblioteca Groq não está instalada. Por favor, instale-a com: pip install groq"
    )

from .base_client import (
    BaseLLMClient, 
    ChatMessage, 
    LLMResponse, 
    LLMConfigurationError,
    LLMConnectionError,
    LLMResponseError,
    LLMTimeoutError
)

# Importar o logger configurado (se existir um central)
# from my_vertical_agent.src.utils.logger import get_logger
# logger = get_logger(__name__)

class GroqClient(BaseLLMClient):
    """
    Cliente LLM para interagir com os modelos via Groq API.
    """
    PROVIDER_NAME = "groq"

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None, **kwargs: Any):
        super().__init__(api_key=api_key, model_name=model_name, **kwargs)

        if not self.model_name:
            raise LLMConfigurationError("Nome do modelo Groq (model_name) não especificado. Ex: \"llama3-8b-8192\", \"mixtral-8x7b-32768\"")
        
        _api_key = self.api_key or os.getenv("GROQ_API_KEY")
        if not _api_key:
            raise LLMConfigurationError(
                "API key da Groq não fornecida nem encontrada na variável de ambiente GROQ_API_KEY."
            )
        
        try:
            self.sync_client = Groq(
                api_key=_api_key,
                timeout=self.client_specific_configs.get("timeout", 20.0),
                max_retries=self.client_specific_configs.get("max_retries", 2)
            )
            self.async_client = AsyncGroq(
                api_key=_api_key,
                timeout=self.client_specific_configs.get("timeout", 20.0),
                max_retries=self.client_specific_configs.get("max_retries", 2)
            )
            # logger.info(f"Cliente Groq inicializado para modelo: {self.model_name}")
            print(f"DEBUG: GroqClient inicializado para modelo: {self.model_name}")
        except Exception as e:
            # logger.error(f"Erro ao inicializar o cliente Groq: {e}", exc_info=True)
            raise LLMConfigurationError(f"Falha ao inicializar o cliente Groq. Detalhes: {e}") from e

    def get_provider_name(self) -> str:
        return self.PROVIDER_NAME

    def _prepare_request_params(self, messages: List[ChatMessage], temperature: float, max_tokens: Optional[int], stop_sequences: Optional[List[str]], stream: bool, **kwargs: Any) -> Dict[str, Any]:
        params = {
            "model": self.model_name,
            "messages": messages, # Groq usa o mesmo formato de mensagens que OpenAI
            "temperature": temperature,
            "stream": stream,
            **kwargs
        }
        if max_tokens is not None:
            params["max_tokens"] = max_tokens
        if stop_sequences is not None:
            params["stop"] = stop_sequences
        return params

    def generate_response(
        self,
        messages: List[ChatMessage],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stop_sequences: Optional[List[str]] = None,
        **kwargs: Any
    ) -> LLMResponse:
        request_params = self._prepare_request_params(messages, temperature, max_tokens, stop_sequences, stream=False, **kwargs)
        # logger.debug(f"GroqClient - Enviando requisição (sync): {request_params}")
        print(f"DEBUG: GroqClient - Enviando requisição (sync): Modelo={request_params['model']}, Temp={request_params['temperature']}")
        try:
            completion = self.sync_client.chat.completions.create(**request_params)
            # logger.debug(f"GroqClient - Resposta recebida: {completion}")
            if completion.choices and completion.choices[0].message:
                response_content = completion.choices[0].message.content
                return response_content.strip() if response_content else ""
            else:
                raise LLMResponseError("Resposta da API Groq não contém choices ou message válidos.")
        except groq.APITimeoutError as e:
            raise LLMTimeoutError(f"Timeout na chamada à API Groq: {e}") from e
        except groq.APIConnectionError as e:
            raise LLMConnectionError(f"Erro de conexão com a API Groq: {e}") from e
        except groq.RateLimitError as e:
            raise LLMResponseError(f"Rate limit excedido na API Groq: {e}") from e
        except groq.APIStatusError as e:
            raise LLMResponseError(f"Erro da API Groq ({e.status_code}): {e.message if hasattr(e, 'message') else str(e)}") from e
        except Exception as e:
            self._handle_error(e, context="Groq generate_response")
            return ""

    async def generate_response_async(
        self,
        messages: List[ChatMessage],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stop_sequences: Optional[List[str]] = None,
        **kwargs: Any
    ) -> LLMResponse:
        request_params = self._prepare_request_params(messages, temperature, max_tokens, stop_sequences, stream=False, **kwargs)
        # logger.debug(f"GroqClient - Enviando requisição (async): {request_params}")
        print(f"DEBUG: GroqClient - Enviando requisição (async): Modelo={request_params['model']}, Temp={request_params['temperature']}")
        try:
            completion = await self.async_client.chat.completions.create(**request_params)
            # logger.debug(f"GroqClient - Resposta async recebida: {completion}")
            if completion.choices and completion.choices[0].message:
                response_content = completion.choices[0].message.content
                return response_content.strip() if response_content else ""
            else:
                raise LLMResponseError("Resposta assíncrona da API Groq não contém choices ou message válidos.")
        except groq.APITimeoutError as e:
            raise LLMTimeoutError(f"Timeout na chamada assíncrona à API Groq: {e}") from e
        # ... (outros tratamentos de erro específicos da Groq como na versão sync)
        except Exception as e:
            self._handle_error(e, context="Groq generate_response_async")
            return ""

    def stream_response(
        self,
        messages: List[ChatMessage],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stop_sequences: Optional[List[str]] = None,
        **kwargs: Any
    ) -> Iterator[LLMResponse]:
        request_params = self._prepare_request_params(messages, temperature, max_tokens, stop_sequences, stream=True, **kwargs)
        # logger.debug(f"GroqClient - Iniciando stream (sync): {request_params}")
        print(f"DEBUG: GroqClient - Iniciando stream (sync): Modelo={request_params['model']}, Temp={request_params['temperature']}")
        try:
            stream = self.sync_client.chat.completions.create(**request_params)
            for chunk in stream:
                # logger.debug(f"GroqClient - Chunk recebido: {chunk}")
                if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            self._handle_error(e, context="Groq stream_response")

    async def stream_response_async(
        self,
        messages: List[ChatMessage],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stop_sequences: Optional[List[str]] = None,
        **kwargs: Any
    ) -> AsyncIterator[LLMResponse]:
        request_params = self._prepare_request_params(messages, temperature, max_tokens, stop_sequences, stream=True, **kwargs)
        # logger.debug(f"GroqClient - Iniciando stream (async): {request_params}")
        print(f"DEBUG: GroqClient - Iniciando stream (async): Modelo={request_params['model']}, Temp={request_params['temperature']}")
        try:
            stream = await self.async_client.chat.completions.create(**request_params)
            async for chunk in stream:
                # logger.debug(f"GroqClient - Chunk async recebido: {chunk}")
                if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            self._handle_error(e, context="Groq stream_response_async")

if __name__ == "__main__":
    print("--- Testando GroqClient Diretamente (Requer GROQ_API_KEY configurada) ---")

    if not os.getenv("GROQ_API_KEY"):
        print("AVISO: A variável de ambiente GROQ_API_KEY não está definida. Os testes podem falhar.")

    try:
        # Modelos disponíveis na Groq: "llama3-8b-8192", "llama3-70b-8192", "mixtral-8x7b-32768", "gemma-7b-it"
        client = GroqClient(model_name="llama3-8b-8192") 
        print(f"Cliente Groq instanciado para modelo: {client.model_name}")

        sample_messages_groq: List[ChatMessage] = [
            {"role": "system", "content": "Você é um assistente eficiente e rápido."},
            {"role": "user", "content": "Qual a velocidade da luz no vácuo?"}
        ]

        # Teste de generate_response (síncrono)
        print("\nTestando generate_response (sync)...")
        try:
            response_sync = client.generate_response(sample_messages_groq, temperature=0.2, max_tokens=100)
            print(f"Resposta (sync): {response_sync}")
        except Exception as e_sync:
            print(f"Erro durante generate_response (sync): {type(e_sync).__name__} - {e_sync}")

        # Teste de stream_response (síncrono)
        print("\nTestando stream_response (sync)...")
        try:
            print("Resposta (stream sync): ", end="")
            for chunk_sync in client.stream_response(sample_messages_groq, temperature=0.2, max_tokens=100):
                print(chunk_sync, end="", flush=True)
            print("\n--- Fim do stream sync ---")
        except Exception as e_stream_sync:
            print(f"\nErro durante stream_response (sync): {type(e_stream_sync).__name__} - {e_stream_sync}")

        import asyncio
        async def run_groq_async_tests():
            print("\nTestando generate_response_async...")
            try:
                response_async = await client.generate_response_async(sample_messages_groq, temperature=0.2, max_tokens=100)
                print(f"Resposta (async): {response_async}")
            except Exception as e_async:
                print(f"Erro durante generate_response_async: {type(e_async).__name__} - {e_async}")

            print("\nTestando stream_response_async...")
            try:
                print("Resposta (stream async): ", end="")
                async for chunk_async in client.stream_response_async(sample_messages_groq, temperature=0.2, max_tokens=100):
                    print(chunk_async, end="", flush=True)
                print("\n--- Fim do stream async ---")
            except Exception as e_stream_async:
                print(f"\nErro durante stream_response_async: {type(e_stream_async).__name__} - {e_stream_async}")

        print("\nExecutando testes assíncronos do GroqClient...")
        asyncio.run(run_groq_async_tests())

    except LLMConfigurationError as lce:
        print(f"Erro de Configuração do Cliente Groq: {lce}")
    except Exception as e:
        print(f"Erro inesperado durante os testes do GroqClient: {type(e).__name__} - {e}")

    print("\n--- Testes do GroqClient concluídos. Verifique os resultados. ---")

