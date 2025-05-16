"""
Cliente LLM para OpenAI (GPT)
Arquivo: src/llm_clients/openai_client.py

Este módulo implementa o `OpenAIClient`, uma classe que herda de `BaseLLMClient`
e fornece uma interface para interagir com os modelos da OpenAI (como GPT-3.5, GPT-4).

Utiliza a biblioteca oficial `openai` para Python.

Boas Práticas e Considerações AI-Friendly:
- **Tratamento de Erros Específico:** Captura exceções específicas da biblioteca OpenAI
  (ex: `openai.APIError`, `openai.RateLimitError`) e as mapeia para as exceções
  personalizadas definidas em `BaseLLMClient` (ex: `LLMConnectionError`, `LLMResponseError`)
  para um tratamento de erro uniforme no nível do agente.
- **Suporte a Streaming:** Implementa os métodos `stream_response` e `stream_response_async`
  para permitir que o agente receba respostas em tempo real.
- **Configuração Flexível:** Permite a configuração de parâmetros como `base_url` (para
  proxies ou endpoints compatíveis com OpenAI), `timeout`, etc., através do construtor.
- **Referência Cruzada:**
    - Herda de `BaseLLMClient` de `src/llm_clients/base_client.py`.
    - Será registrado no `LLM_PROVIDER_MAP` em `src/llm_clients/loader.py`.
    - A API key é esperada da variável de ambiente definida em `config/.env.example`
      e referenciada na configuração YAML do modelo do agente.
"""
import os
from typing import List, Dict, Any, Optional, Iterator, AsyncIterator

# Tenta importar a biblioteca openai. Se não estiver instalada, levanta um erro informativo.
try:
    import openai
    from openai import OpenAI, AsyncOpenAI # OpenAI SDK v1.x+
except ImportError:
    raise ImportError(
        "A biblioteca OpenAI não está instalada. Por favor, instale-a com: pip install openai"
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

class OpenAIClient(BaseLLMClient):
    """
    Cliente LLM para interagir com os modelos da OpenAI.
    """
    PROVIDER_NAME = "openai"

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None, **kwargs: Any):
        """
        Inicializa o cliente OpenAI.

        Args:
            api_key (Optional[str]): Chave de API da OpenAI. Se None, a biblioteca OpenAI tentará
                                     encontrá-la na variável de ambiente OPENAI_API_KEY.
            model_name (Optional[str]): Nome do modelo OpenAI a ser usado (ex: "gpt-3.5-turbo", "gpt-4").
            **kwargs: Argumentos adicionais para o cliente OpenAI, como:
                      - base_url (str): Para usar um endpoint alternativo compatível com OpenAI.
                      - timeout (float): Timeout para as requisições.
                      - max_retries (int): Número máximo de tentativas.
        """
        super().__init__(api_key=api_key, model_name=model_name, **kwargs)
        
        if not self.model_name:
            raise LLMConfigurationError("Nome do modelo OpenAI (model_name) não especificado.")

        # A biblioteca OpenAI v1.x+ usa OPENAI_API_KEY por padrão se api_key não for passado explicitamente.
        # No entanto, é bom ser explícito se a chave foi fornecida ao construtor.
        # Se api_key é None aqui, o OpenAI() usará a variável de ambiente.
        try:
            self.sync_client = OpenAI(
                api_key=self.api_key, # Pode ser None, a lib OpenAI tentará var de ambiente
                base_url=self.client_specific_configs.get("base_url"),
                timeout=self.client_specific_configs.get("timeout", 20.0), # Padrão de 20s
                max_retries=self.client_specific_configs.get("max_retries", 2) # Padrão de 2 retries
            )
            self.async_client = AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.client_specific_configs.get("base_url"),
                timeout=self.client_specific_configs.get("timeout", 20.0),
                max_retries=self.client_specific_configs.get("max_retries", 2)
            )
            # logger.info(f"Cliente OpenAI inicializado para modelo: {self.model_name}")
            print(f"DEBUG: OpenAIClient inicializado para modelo: {self.model_name}")
        except Exception as e:
            # logger.error(f"Erro ao inicializar o cliente OpenAI: {e}", exc_info=True)
            raise LLMConfigurationError(f"Falha ao inicializar o cliente OpenAI. Detalhes: {e}") from e

    def get_provider_name(self) -> str:
        return self.PROVIDER_NAME

    def _prepare_request_params(self, messages: List[ChatMessage], temperature: float, max_tokens: Optional[int], stop_sequences: Optional[List[str]], stream: bool, **kwargs: Any) -> Dict[str, Any]:
        params = {
            "model": self.model_name,
            "messages": messages,
            "temperature": temperature,
            "stream": stream,
            **kwargs # Permite passar quaisquer outros parâmetros suportados pela API
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
        """
        Gera uma resposta completa do modelo OpenAI.
        """
        request_params = self._prepare_request_params(messages, temperature, max_tokens, stop_sequences, stream=False, **kwargs)
        # logger.debug(f"OpenAIClient - Enviando requisição para generate_response: {request_params}")
        print(f"DEBUG: OpenAIClient - Enviando requisição (sync): Modelo={request_params["model"]}, Temp={request_params["temperature"]}")
        try:
            completion = self.sync_client.chat.completions.create(**request_params)
            # logger.debug(f"OpenAIClient - Resposta recebida: {completion}")
            # A resposta da API v1.x é um objeto ChatCompletion
            # O conteúdo da mensagem está em completion.choices[0].message.content
            if completion.choices and completion.choices[0].message:
                response_content = completion.choices[0].message.content
                # Pode-se retornar o objeto completion inteiro ou apenas o conteúdo
                # Para consistência com BaseLLMClient, vamos focar no conteúdo textual ou um dict simples.
                # Se precisar de mais dados (usage, finish_reason), adapte LLMResponse e este retorno.
                return response_content.strip() if response_content else ""
            else:
                raise LLMResponseError("Resposta da API OpenAI não contém choices ou message válidos.")
        except openai.APITimeoutError as e:
            # logger.error(f"Timeout na API OpenAI: {e}", exc_info=True)
            raise LLMTimeoutError(f"Timeout na chamada à API OpenAI: {e}") from e
        except openai.APIConnectionError as e:
            # logger.error(f"Erro de conexão com API OpenAI: {e}", exc_info=True)
            raise LLMConnectionError(f"Erro de conexão com a API OpenAI: {e}") from e
        except openai.RateLimitError as e:
            # logger.error(f"Rate limit excedido na API OpenAI: {e}", exc_info=True)
            raise LLMResponseError(f"Rate limit excedido na API OpenAI: {e}") from e # Pode ser um tipo de erro específico
        except openai.APIStatusError as e: # Erros de status HTTP (4xx, 5xx)
            # logger.error(f"Erro de status da API OpenAI ({e.status_code}): {e.response}", exc_info=True)
            raise LLMResponseError(f"Erro da API OpenAI ({e.status_code}): {e.message}") from e
        except Exception as e:
            # logger.error(f"Erro inesperado ao chamar API OpenAI: {e}", exc_info=True)
            self._handle_error(e, context="OpenAI generate_response") # Re-levanta como Exception genérica ou LLMResponseError
            return "" # Fallback para satisfazer o tipo de retorno, mas o erro já foi levantado

    async def generate_response_async(
        self,
        messages: List[ChatMessage],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stop_sequences: Optional[List[str]] = None,
        **kwargs: Any
    ) -> LLMResponse:
        """
        Gera uma resposta completa do modelo OpenAI de forma assíncrona.
        """
        request_params = self._prepare_request_params(messages, temperature, max_tokens, stop_sequences, stream=False, **kwargs)
        # logger.debug(f"OpenAIClient - Enviando requisição para generate_response_async: {request_params}")
        print(f"DEBUG: OpenAIClient - Enviando requisição (async): Modelo={request_params["model"]}, Temp={request_params["temperature"]}")
        try:
            completion = await self.async_client.chat.completions.create(**request_params)
            # logger.debug(f"OpenAIClient - Resposta async recebida: {completion}")
            if completion.choices and completion.choices[0].message:
                response_content = completion.choices[0].message.content
                return response_content.strip() if response_content else ""
            else:
                raise LLMResponseError("Resposta assíncrona da API OpenAI não contém choices ou message válidos.")
        except openai.APITimeoutError as e:
            raise LLMTimeoutError(f"Timeout na chamada assíncrona à API OpenAI: {e}") from e
        except openai.APIConnectionError as e:
            raise LLMConnectionError(f"Erro de conexão assíncrona com a API OpenAI: {e}") from e
        except openai.RateLimitError as e:
            raise LLMResponseError(f"Rate limit excedido na chamada assíncrona à API OpenAI: {e}") from e
        except openai.APIStatusError as e:
            raise LLMResponseError(f"Erro da API OpenAI assíncrona ({e.status_code}): {e.message}") from e
        except Exception as e:
            self._handle_error(e, context="OpenAI generate_response_async")
            return ""

    def stream_response(
        self,
        messages: List[ChatMessage],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stop_sequences: Optional[List[str]] = None,
        **kwargs: Any
    ) -> Iterator[LLMResponse]:
        """
        Gera uma resposta em streaming do modelo OpenAI.
        Retorna um iterador de strings (chunks de conteúdo).
        """
        request_params = self._prepare_request_params(messages, temperature, max_tokens, stop_sequences, stream=True, **kwargs)
        # logger.debug(f"OpenAIClient - Iniciando stream_response: {request_params}")
        print(f"DEBUG: OpenAIClient - Iniciando stream (sync): Modelo={request_params["model"]}, Temp={request_params["temperature"]}")
        try:
            stream = self.sync_client.chat.completions.create(**request_params)
            for chunk in stream:
                # logger.debug(f"OpenAIClient - Chunk recebido: {chunk}")
                if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
        except openai.APITimeoutError as e:
            raise LLMTimeoutError(f"Timeout durante streaming da API OpenAI: {e}") from e
        except openai.APIConnectionError as e:
            raise LLMConnectionError(f"Erro de conexão durante streaming da API OpenAI: {e}") from e
        except openai.APIStatusError as e: # Erros de status HTTP (4xx, 5xx)
            raise LLMResponseError(f"Erro da API OpenAI durante streaming ({e.status_code}): {e.message}") from e
        except Exception as e:
            self._handle_error(e, context="OpenAI stream_response")
            # Se um erro ocorrer no meio do stream, o iterador pode parar abruptamente.
            # O tratamento de erro no agente que consome este iterador deve estar ciente disso.

    async def stream_response_async(
        self,
        messages: List[ChatMessage],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stop_sequences: Optional[List[str]] = None,
        **kwargs: Any
    ) -> AsyncIterator[LLMResponse]:
        """
        Gera uma resposta em streaming do modelo OpenAI de forma assíncrona.
        Retorna um iterador assíncrono de strings (chunks de conteúdo).
        """
        request_params = self._prepare_request_params(messages, temperature, max_tokens, stop_sequences, stream=True, **kwargs)
        # logger.debug(f"OpenAIClient - Iniciando stream_response_async: {request_params}")
        print(f"DEBUG: OpenAIClient - Iniciando stream (async): Modelo={request_params["model"]}, Temp={request_params["temperature"]}")
        try:
            stream = await self.async_client.chat.completions.create(**request_params)
            async for chunk in stream:
                # logger.debug(f"OpenAIClient - Chunk async recebido: {chunk}")
                if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
        except openai.APITimeoutError as e:
            raise LLMTimeoutError(f"Timeout durante streaming assíncrono da API OpenAI: {e}") from e
        except openai.APIConnectionError as e:
            raise LLMConnectionError(f"Erro de conexão durante streaming assíncrono da API OpenAI: {e}") from e
        except openai.APIStatusError as e:
            raise LLMResponseError(f"Erro da API OpenAI durante streaming assíncrono ({e.status_code}): {e.message}") from e
        except Exception as e:
            self._handle_error(e, context="OpenAI stream_response_async")

if __name__ == "__main__":
    print("--- Testando OpenAIClient Diretamente (Requer OPENAI_API_KEY configurada) ---")
    
    # Certifique-se de que a variável de ambiente OPENAI_API_KEY está definida.
    if not os.getenv("OPENAI_API_KEY"):
        print("AVISO: A variável de ambiente OPENAI_API_KEY não está definida. Os testes podem falhar.")
        # Para testes locais sem uma chave real, você pode mockar a API ou usar um endpoint compatível.

    try:
        # Teste com um modelo que provavelmente existe, como gpt-3.5-turbo
        # Se você tiver acesso ao gpt-4, pode usar "gpt-4-turbo-preview" ou similar.
        client = OpenAIClient(model_name="gpt-3.5-turbo") # A API key será pega da var de ambiente
        print(f"Cliente OpenAI instanciado para modelo: {client.model_name}")

        sample_messages: List[ChatMessage] = [
            {"role": "system", "content": "Você é um assistente prestativo."},
            {"role": "user", "content": "Olá! Qual é a capital da França?"}
        ]

        # Teste de generate_response (síncrono)
        print("\nTestando generate_response (sync)...")
        try:
            response_sync = client.generate_response(sample_messages, temperature=0.5, max_tokens=50)
            print(f"Resposta (sync): {response_sync}")
        except Exception as e_sync:
            print(f"Erro durante generate_response (sync): {type(e_sync).__name__} - {e_sync}")

        # Teste de stream_response (síncrono)
        print("\nTestando stream_response (sync)...")
        try:
            print("Resposta (stream sync): ", end="")
            for chunk_sync in client.stream_response(sample_messages, temperature=0.5, max_tokens=50):
                print(chunk_sync, end="", flush=True)
            print("\n--- Fim do stream sync ---")
        except Exception as e_stream_sync:
            print(f"\nErro durante stream_response (sync): {type(e_stream_sync).__name__} - {e_stream_sync}")

        # Para testar os métodos assíncronos, você precisaria de um loop de eventos asyncio.
        import asyncio

        async def run_async_tests():
            # Teste de generate_response_async
            print("\nTestando generate_response_async...")
            try:
                response_async = await client.generate_response_async(sample_messages, temperature=0.5, max_tokens=50)
                print(f"Resposta (async): {response_async}")
            except Exception as e_async:
                print(f"Erro durante generate_response_async: {type(e_async).__name__} - {e_async}")

            # Teste de stream_response_async
            print("\nTestando stream_response_async...")
            try:
                print("Resposta (stream async): ", end="")
                async for chunk_async in client.stream_response_async(sample_messages, temperature=0.5, max_tokens=50):
                    print(chunk_async, end="", flush=True)
                print("\n--- Fim do stream async ---")
            except Exception as e_stream_async:
                print(f"\nErro durante stream_response_async: {type(e_stream_async).__name__} - {e_stream_async}")

        print("\nExecutando testes assíncronos...")
        asyncio.run(run_async_tests())

    except LLMConfigurationError as lce:
        print(f"Erro de Configuração do Cliente OpenAI: {lce}")
    except Exception as e:
        print(f"Erro inesperado durante os testes do OpenAIClient: {type(e).__name__} - {e}")

    print("\n--- Testes do OpenAIClient concluídos. Verifique os resultados. ---")

