"""
Cliente LLM para Anthropic Claude
Arquivo: src/llm_clients/anthropic_client.py

Este módulo implementa o `AnthropicClient`, uma classe que herda de `BaseLLMClient`
e fornece uma interface para interagir com os modelos da Anthropic (Claude).

Utiliza a biblioteca oficial `anthropic` para Python.

Boas Práticas e Considerações AI-Friendly:
- **Tratamento de Erros Específico:** Captura exceções da biblioteca Anthropic
  e as mapeia para as exceções personalizadas de `BaseLLMClient`.
- **Suporte a Streaming:** Implementa os métodos de streaming.
- **Formato de Mensagens:** A API do Claude tem um formato específico para mensagens
  (especialmente para o `system` prompt e a alternância user/assistant).
- **Referência Cruzada:**
    - Herda de `BaseLLMClient`.
    - Será registrado no `LLM_PROVIDER_MAP` em `loader.py`.
    - A API key é esperada da variável de ambiente (ex: `ANTHROPIC_API_KEY`).
"""
import os
from typing import List, Dict, Any, Optional, Iterator, AsyncIterator

try:
    import anthropic
    from anthropic import Anthropic, AsyncAnthropic # Anthropic SDK
    # from anthropic.types import MessageParam, MessageStreamEvent, ContentBlockDeltaEvent, TextDelta
except ImportError:
    raise ImportError(
        "A biblioteca Anthropic não está instalada. Por favor, instale-a com: pip install anthropic"
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

class AnthropicClient(BaseLLMClient):
    """
    Cliente LLM para interagir com os modelos Anthropic Claude.
    """
    PROVIDER_NAME = "anthropic_claude"

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None, **kwargs: Any):
        super().__init__(api_key=api_key, model_name=model_name, **kwargs)

        if not self.model_name:
            raise LLMConfigurationError("Nome do modelo Anthropic Claude (model_name) não especificado. Ex: \"claude-3-opus-20240229\"")
        
        _api_key = self.api_key or os.getenv("ANTHROPIC_API_KEY")
        if not _api_key:
            raise LLMConfigurationError(
                "API key da Anthropic não fornecida nem encontrada na variável de ambiente ANTHROPIC_API_KEY."
            )
        
        try:
            self.sync_client = Anthropic(
                api_key=_api_key,
                timeout=self.client_specific_configs.get("timeout", 20.0),
                max_retries=self.client_specific_configs.get("max_retries", 2)
            )
            self.async_client = AsyncAnthropic(
                api_key=_api_key,
                timeout=self.client_specific_configs.get("timeout", 20.0),
                max_retries=self.client_specific_configs.get("max_retries", 2)
            )
            # logger.info(f"Cliente Anthropic Claude inicializado para modelo: {self.model_name}")
            print(f"DEBUG: AnthropicClient inicializado para modelo: {self.model_name}")
        except Exception as e:
            # logger.error(f"Erro ao inicializar o cliente Anthropic: {e}", exc_info=True)
            raise LLMConfigurationError(f"Falha ao inicializar o cliente Anthropic. Detalhes: {e}") from e

    def get_provider_name(self) -> str:
        return self.PROVIDER_NAME

    def _prepare_messages_and_system_prompt(self, messages: List[ChatMessage]) -> tuple[Optional[str], List[Dict[str, str]]]:
        """
        Prepara as mensagens para o formato da API Claude.
        A API Claude espera um `system` prompt separado e uma lista de mensagens user/assistant alternadas.
        A primeira mensagem da lista `messages` deve ser do usuário.
        """
        system_prompt_content: Optional[str] = None
        claude_messages: List[Dict[str, str]] = []
        
        # Extrai o system prompt, se houver e for o primeiro.
        if messages and messages[0]["role"] == "system":
            system_prompt_content = messages[0]["content"]
            processed_messages = messages[1:]
        else:
            processed_messages = messages

        # Converte para o formato do Claude, garantindo alternância user/assistant
        # e que a primeira mensagem seja 'user'.
        # A API do Claude é um pouco mais rigorosa com isso.
        last_role = None
        for msg in processed_messages:
            role = msg.get("role")
            content = msg.get("content", "")
            
            if role == "user":
                if last_role == "user": # Não pode ter duas mensagens de user seguidas
                    # logger.warning("AnthropicClient: Duas mensagens de 'user' consecutivas. Combinando ou ignorando a anterior.")
                    # Aqui, poderíamos tentar combinar, mas por simplicidade, vamos apenas usar a última.
                    # Ou levantar um erro se isso for uma condição inválida para o agente.
                    claude_messages[-1]["content"] += "\n" + content # Simples concatenação
                else:
                    claude_messages.append({"role": "user", "content": content})
                last_role = "user"
            elif role == "assistant":
                if last_role == "assistant":
                    # logger.warning("AnthropicClient: Duas mensagens de 'assistant' consecutivas. Combinando.")
                    claude_messages[-1]["content"] += "\n" + content
                else:
                    claude_messages.append({"role": "assistant", "content": content})
                last_role = "assistant"
            # Ignora outros roles por enquanto ou os converte se necessário.

        if not claude_messages or claude_messages[0]["role"] != "user":
            # logger.error("AnthropicClient: A primeira mensagem para a API Claude (após o system prompt) deve ser do tipo 'user'.")
            raise LLMConfigurationError("A primeira mensagem para a API Claude (após system prompt) deve ser do tipo 'user'.")
            
        return system_prompt_content, claude_messages

    def _prepare_request_params(
        self, 
        claude_messages: List[Dict[str, str]], 
        system_prompt: Optional[str], 
        temperature: float, 
        max_tokens_to_sample: int, # Claude usa max_tokens_to_sample
        stop_sequences: Optional[List[str]], 
        **kwargs: Any
    ) -> Dict[str, Any]:
        params = {
            "model": self.model_name,
            "messages": claude_messages,
            "max_tokens": max_tokens_to_sample, # Nome do parâmetro para Claude
            "temperature": temperature,
            **kwargs # Outros params como top_p, top_k
        }
        if system_prompt is not None:
            params["system"] = system_prompt
        if stop_sequences is not None:
            params["stop_sequences"] = stop_sequences
        return params

    def generate_response(
        self,
        messages: List[ChatMessage],
        temperature: float = 0.7,
        max_tokens: Optional[int] = 2048, # Claude geralmente tem um padrão alto, mas é bom definir
        stop_sequences: Optional[List[str]] = None,
        **kwargs: Any
    ) -> LLMResponse:
        system_prompt, claude_messages = self._prepare_messages_and_system_prompt(messages)
        # Claude requer `max_tokens` (anteriormente `max_tokens_to_sample`)
        _max_tokens = max_tokens if max_tokens is not None else 2048 # Default para Claude
        
        request_params = self._prepare_request_params(claude_messages, system_prompt, temperature, _max_tokens, stop_sequences, **kwargs)
        # logger.debug(f"AnthropicClient - Enviando requisição (sync): {request_params}")
        print(f"DEBUG: AnthropicClient - Enviando requisição (sync): Modelo={request_params["model"]}, Temp={request_params["temperature"]}")
        try:
            response = self.sync_client.messages.create(**request_params)
            # logger.debug(f"AnthropicClient - Resposta recebida: {response}")
            # O conteúdo da resposta está em response.content, que é uma lista de blocos.
            # Geralmente, para chat, esperamos um único bloco de texto.
            if response.content and isinstance(response.content, list) and len(response.content) > 0:
                # Assumindo que o primeiro bloco de conteúdo é o texto principal
                if hasattr(response.content[0], "text"):
                    return response.content[0].text.strip()
            raise LLMResponseError("Resposta da API Anthropic não contém conteúdo de texto esperado.")
        except anthropic.APITimeoutError as e:
            raise LLMTimeoutError(f"Timeout na chamada à API Anthropic: {e}") from e
        except anthropic.APIConnectionError as e:
            raise LLMConnectionError(f"Erro de conexão com a API Anthropic: {e}") from e
        except anthropic.RateLimitError as e:
            raise LLMResponseError(f"Rate limit excedido na API Anthropic: {e}") from e
        except anthropic.APIStatusError as e:
            raise LLMResponseError(f"Erro da API Anthropic ({e.status_code}): {e.message}") from e
        except Exception as e:
            self._handle_error(e, context="Anthropic generate_response")
            return ""

    async def generate_response_async(
        self,
        messages: List[ChatMessage],
        temperature: float = 0.7,
        max_tokens: Optional[int] = 2048,
        stop_sequences: Optional[List[str]] = None,
        **kwargs: Any
    ) -> LLMResponse:
        system_prompt, claude_messages = self._prepare_messages_and_system_prompt(messages)
        _max_tokens = max_tokens if max_tokens is not None else 2048
        request_params = self._prepare_request_params(claude_messages, system_prompt, temperature, _max_tokens, stop_sequences, **kwargs)
        # logger.debug(f"AnthropicClient - Enviando requisição (async): {request_params}")
        print(f"DEBUG: AnthropicClient - Enviando requisição (async): Modelo={request_params["model"]}, Temp={request_params["temperature"]}")
        try:
            response = await self.async_client.messages.create(**request_params)
            # logger.debug(f"AnthropicClient - Resposta async recebida: {response}")
            if response.content and isinstance(response.content, list) and len(response.content) > 0:
                if hasattr(response.content[0], "text"):
                    return response.content[0].text.strip()
            raise LLMResponseError("Resposta assíncrona da API Anthropic não contém conteúdo de texto esperado.")
        except anthropic.APITimeoutError as e:
            raise LLMTimeoutError(f"Timeout na chamada assíncrona à API Anthropic: {e}") from e
        # ... (outros tratamentos de erro específicos da Anthropic como na versão sync)
        except Exception as e:
            self._handle_error(e, context="Anthropic generate_response_async")
            return ""

    def stream_response(
        self,
        messages: List[ChatMessage],
        temperature: float = 0.7,
        max_tokens: Optional[int] = 2048,
        stop_sequences: Optional[List[str]] = None,
        **kwargs: Any
    ) -> Iterator[LLMResponse]:
        system_prompt, claude_messages = self._prepare_messages_and_system_prompt(messages)
        _max_tokens = max_tokens if max_tokens is not None else 2048
        request_params = self._prepare_request_params(claude_messages, system_prompt, temperature, _max_tokens, stop_sequences, **kwargs)
        # logger.debug(f"AnthropicClient - Iniciando stream (sync): {request_params}")
        print(f"DEBUG: AnthropicClient - Iniciando stream (sync): Modelo={request_params["model"]}, Temp={request_params["temperature"]}")
        try:
            with self.sync_client.messages.stream(**request_params) as stream:
                for event in stream:
                    # logger.debug(f"AnthropicClient - Evento de stream sync: {type(event)}")
                    # O SDK mais recente usa eventos como ContentBlockDeltaEvent
                    if isinstance(event, anthropic.types.ContentBlockDeltaEvent) and isinstance(event.delta, anthropic.types.TextDelta):
                        yield event.delta.text
                    # Adicionar tratamento para outros tipos de eventos de stream se necessário (ex: message_stop)
        except Exception as e:
            self._handle_error(e, context="Anthropic stream_response")

    async def stream_response_async(
        self,
        messages: List[ChatMessage],
        temperature: float = 0.7,
        max_tokens: Optional[int] = 2048,
        stop_sequences: Optional[List[str]] = None,
        **kwargs: Any
    ) -> AsyncIterator[LLMResponse]:
        system_prompt, claude_messages = self._prepare_messages_and_system_prompt(messages)
        _max_tokens = max_tokens if max_tokens is not None else 2048
        request_params = self._prepare_request_params(claude_messages, system_prompt, temperature, _max_tokens, stop_sequences, **kwargs)
        # logger.debug(f"AnthropicClient - Iniciando stream (async): {request_params}")
        print(f"DEBUG: AnthropicClient - Iniciando stream (async): Modelo={request_params["model"]}, Temp={request_params["temperature"]}")
        try:
            async with self.async_client.messages.stream(**request_params) as stream:
                async for event in stream:
                    # logger.debug(f"AnthropicClient - Evento de stream async: {type(event)}")
                    if isinstance(event, anthropic.types.ContentBlockDeltaEvent) and isinstance(event.delta, anthropic.types.TextDelta):
                        yield event.delta.text
        except Exception as e:
            self._handle_error(e, context="Anthropic stream_response_async")

if __name__ == "__main__":
    print("--- Testando AnthropicClient Diretamente (Requer ANTHROPIC_API_KEY configurada) ---")

    if not os.getenv("ANTHROPIC_API_KEY"):
        print("AVISO: A variável de ambiente ANTHROPIC_API_KEY não está definida. Os testes podem falhar.")

    try:
        # Use um modelo Claude apropriado, ex: "claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"
        client = AnthropicClient(model_name="claude-3-haiku-20240307") 
        print(f"Cliente Anthropic Claude instanciado para modelo: {client.model_name}")

        sample_messages_claude: List[ChatMessage] = [
            {"role": "system", "content": "Você é um poeta conciso."},
            {"role": "user", "content": "Escreva um haiku sobre a primavera."}
        ]
        
        sample_messages_claude_no_system: List[ChatMessage] = [
            {"role": "user", "content": "Qual a sua cor favorita e por quê?"}
        ]

        # Teste de generate_response (síncrono)
        print("\nTestando generate_response (sync) com system prompt...")
        try:
            response_sync = client.generate_response(sample_messages_claude, temperature=0.3, max_tokens=100)
            print(f"Resposta (sync):\n{response_sync}")
        except Exception as e_sync:
            print(f"Erro durante generate_response (sync): {type(e_sync).__name__} - {e_sync}")

        print("\nTestando generate_response (sync) sem system prompt...")
        try:
            response_sync_no_sys = client.generate_response(sample_messages_claude_no_system, temperature=0.7, max_tokens=150)
            print(f"Resposta (sync, no system):\n{response_sync_no_sys}")
        except Exception as e_sync_ns:
            print(f"Erro durante generate_response (sync, no system): {type(e_sync_ns).__name__} - {e_sync_ns}")

        # Teste de stream_response (síncrono)
        print("\nTestando stream_response (sync) com system prompt...")
        try:
            print("Resposta (stream sync): ", end="")
            for chunk_sync in client.stream_response(sample_messages_claude, temperature=0.3, max_tokens=100):
                print(chunk_sync, end="", flush=True)
            print("\n--- Fim do stream sync ---")
        except Exception as e_stream_sync:
            print(f"\nErro durante stream_response (sync): {type(e_stream_sync).__name__} - {e_stream_sync}")

        import asyncio
        async def run_anthropic_async_tests():
            print("\nTestando generate_response_async com system prompt...")
            try:
                response_async = await client.generate_response_async(sample_messages_claude, temperature=0.3, max_tokens=100)
                print(f"Resposta (async):\n{response_async}")
            except Exception as e_async:
                print(f"Erro durante generate_response_async: {type(e_async).__name__} - {e_async}")

            print("\nTestando stream_response_async com system prompt...")
            try:
                print("Resposta (stream async): ", end="")
                async for chunk_async in client.stream_response_async(sample_messages_claude, temperature=0.3, max_tokens=100):
                    print(chunk_async, end="", flush=True)
                print("\n--- Fim do stream async ---")
            except Exception as e_stream_async:
                print(f"\nErro durante stream_response_async: {type(e_stream_async).__name__} - {e_stream_async}")

        print("\nExecutando testes assíncronos do AnthropicClient...")
        asyncio.run(run_anthropic_async_tests())

    except LLMConfigurationError as lce:
        print(f"Erro de Configuração do Cliente Anthropic: {lce}")
    except Exception as e:
        print(f"Erro inesperado durante os testes do AnthropicClient: {type(e).__name__} - {e}")

    print("\n--- Testes do AnthropicClient concluídos. Verifique os resultados. ---")

