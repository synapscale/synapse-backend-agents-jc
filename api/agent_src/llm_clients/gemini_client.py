"""
Cliente LLM para Google Gemini
Arquivo: src/llm_clients/gemini_client.py

Este módulo implementa o `GeminiClient`, uma classe que herda de `BaseLLMClient`
e fornece uma interface para interagir com os modelos Google Gemini (ex: gemini-pro).

Utiliza a biblioteca `google-generativeai`.

Boas Práticas e Considerações AI-Friendly:
- **Tratamento de Erros Específico:** Captura exceções da biblioteca do Google
  e as mapeia para as exceções personalizadas de `BaseLLMClient`.
- **Suporte a Streaming:** Implementa os métodos de streaming.
- **Configuração de Segurança:** A API do Gemini permite configurar `safety_settings` para
  filtrar conteúdo prejudicial. O cliente deve permitir passar essas configurações.
- **Referência Cruzada:**
    - Herda de `BaseLLMClient`.
    - Será registrado no `LLM_PROVIDER_MAP` em `loader.py`.
    - A API key é esperada da variável de ambiente (ex: `GOOGLE_API_KEY`).
"""
import os
from typing import List, Dict, Any, Optional, Iterator, AsyncIterator

try:
    import google.generativeai as genai
    from google.generativeai.types import GenerationConfig, SafetySetting, HarmCategory, HarmBlockThreshold
except ImportError:
    raise ImportError(
        "A biblioteca google-generativeai não está instalada. Por favor, instale-a com: pip install google-generativeai"
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

class GeminiClient(BaseLLMClient):
    """
    Cliente LLM para interagir com os modelos Google Gemini.
    """
    PROVIDER_NAME = "google_gemini"

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None, **kwargs: Any):
        super().__init__(api_key=api_key, model_name=model_name, **kwargs)

        if not self.model_name:
            raise LLMConfigurationError("Nome do modelo Gemini (model_name) não especificado. Ex: \"gemini-pro\"")
        
        _api_key = self.api_key or os.getenv("GOOGLE_API_KEY") # Variável de ambiente padrão para a lib do Google
        if not _api_key:
            raise LLMConfigurationError(
                "API key do Google não fornecida nem encontrada na variável de ambiente GOOGLE_API_KEY."
            )
        
        try:
            genai.configure(api_key=_api_key)
            self.client = genai.GenerativeModel(self.model_name)
            # logger.info(f"Cliente Gemini inicializado para modelo: {self.model_name}")
            print(f"DEBUG: GeminiClient inicializado para modelo: {self.model_name}")
        except Exception as e:
            # logger.error(f"Erro ao inicializar o cliente Gemini: {e}", exc_info=True)
            raise LLMConfigurationError(f"Falha ao inicializar o cliente Gemini. Detalhes: {e}") from e

    def get_provider_name(self) -> str:
        return self.PROVIDER_NAME

    def _prepare_chat_history(self, messages: List[ChatMessage]) -> List[Dict[str, Any]]:
        """
        Converte o formato ChatMessage para o formato de histórico esperado pelo Gemini.
        Gemini espera uma lista de {'role': 'user'/'model', 'parts': [text]}.
        O role 'system' não é diretamente suportado como uma mensagem no histórico de chat da mesma forma que OpenAI.
        Instruções de sistema podem ser passadas no `GenerativeModel(model_name, system_instruction=...)`
        ou como parte da primeira mensagem do usuário.
        """
        history = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            
            # Gemini usa 'user' e 'model' para roles no chat.
            # O role 'system' pode ser tratado como uma instrução inicial do usuário ou configurado no modelo.
            if role == "system":
                # Opção 1: Preceder a primeira mensagem do usuário com a instrução do sistema.
                # (Isso requer que o chamador garanta que a mensagem do sistema seja a primeira, se usada assim)
                # Ou, melhor, configurar `system_instruction` no GenerativeModel se a API suportar para o modelo específico.
                # Por simplicidade aqui, vamos assumir que a mensagem do sistema é convertida para 'user'
                # ou que o `system_instruction` foi usado na inicialização do modelo.
                # logger.warning("GeminiClient: Role 'system' será tratado como 'user' no histórico de chat. Considere usar system_instruction no modelo.")
                print("AVISO: GeminiClient - Role 'system' tratado como 'user'. Use system_instruction no modelo se disponível.")
                history.append({"role": "user", "parts": [content]})
            elif role == "assistant":
                history.append({"role": "model", "parts": [content]})
            elif role == "user":
                history.append({"role": "user", "parts": [content]})
            else:
                # logger.warning(f"GeminiClient: Role desconhecido {role} encontrado, tratando como 'user'.")
                print(f"AVISO: GeminiClient - Role desconhecido {role}, tratando como 'user'.")
                history.append({"role": "user", "parts": [content]})
        return history

    def _prepare_generation_config(
        self, 
        temperature: float, 
        max_tokens: Optional[int],
        stop_sequences: Optional[List[str]],
        **kwargs: Any
    ) -> GenerationConfig:
        config_params = {"temperature": temperature}
        if max_tokens is not None:
            config_params["max_output_tokens"] = max_tokens
        if stop_sequences is not None:
            config_params["stop_sequences"] = stop_sequences
        
        # Adicionar outros parâmetros de kwargs se forem válidos para GenerationConfig
        # Ex: top_p, top_k
        if "top_p" in kwargs: config_params["top_p"] = kwargs["top_p"]
        if "top_k" in kwargs: config_params["top_k"] = kwargs["top_k"]
        
        return GenerationConfig(**config_params)
    
    def _parse_safety_settings(self, safety_kwargs: Dict[str, Any]) -> Optional[List[SafetySetting]]:
        """ Parsea safety_settings de kwargs, se fornecido. """
        # Exemplo de como safety_settings pode ser passado em kwargs:
        # safety_settings_config = {
        #     "HARASSMENT": "BLOCK_NONE",
        #     "HATE_SPEECH": "BLOCK_MEDIUM_AND_ABOVE",
        #     "SEXUALLY_EXPLICIT": "BLOCK_ONLY_HIGH",
        #     "DANGEROUS_CONTENT": "BLOCK_LOW_AND_ABOVE"
        # }
        # kwargs = {"safety_settings": safety_settings_config}
        
        safety_settings_input = safety_kwargs.get("safety_settings")
        if not safety_settings_input or not isinstance(safety_settings_input, dict):
            return None

        parsed_settings = []
        for category_str, threshold_str in safety_settings_input.items():
            try:
                harm_category = HarmCategory[category_str.upper()]
                block_threshold = HarmBlockThreshold[threshold_str.upper()]
                parsed_settings.append(SafetySetting(category=harm_category, threshold=block_threshold))
            except KeyError:
                # logger.warning(f"GeminiClient: Categoria de segurança ou limiar inválido: {category_str}, {threshold_str}")
                print(f"AVISO: GeminiClient - Categoria/limiar de segurança inválido: {category_str}, {threshold_str}")
        return parsed_settings if parsed_settings else None

    def generate_response(
        self,
        messages: List[ChatMessage],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stop_sequences: Optional[List[str]] = None,
        **kwargs: Any
    ) -> LLMResponse:
        chat_history = self._prepare_chat_history(messages)
        # A última mensagem é o prompt atual, o resto é histórico.
        # A API send_message do Gemini não aceita um histórico diretamente, mas sim inicia um chat.
        # Para uma única chamada, podemos enviar todo o histórico como contexto.
        # Se o histórico for apenas a última mensagem do usuário, é mais simples.
        
        # Para chamadas de chat com histórico, o ideal é usar `model.start_chat(history=...)`
        # e depois `chat.send_message(...)`.
        # Para uma chamada única de `generate_content` que simula um chat, passamos o histórico.
        
        generation_config = self._prepare_generation_config(temperature, max_tokens, stop_sequences, **kwargs)
        safety_settings = self._parse_safety_settings(kwargs)
        
        # logger.debug(f"GeminiClient - Enviando requisição (sync): Modelo={self.model_name}, Temp={temperature}")
        print(f"DEBUG: GeminiClient - Enviando requisição (sync): Modelo={self.model_name}, Temp={temperature}")
        try:
            # Para `generate_content`, o histórico é passado como a lista de conteúdos.
            response = self.client.generate_content(
                contents=chat_history, 
                generation_config=generation_config,
                safety_settings=safety_settings,
                stream=False
            )
            # logger.debug(f"GeminiClient - Resposta recebida: {response}")
            # A resposta pode ter partes, e pode ter sido bloqueada por safety settings.
            if response.parts:
                return response.text.strip()
            elif response.prompt_feedback and response.prompt_feedback.block_reason:
                # logger.warning(f"GeminiClient: Resposta bloqueada. Razão: {response.prompt_feedback.block_reason}")
                raise LLMResponseError(f"Resposta do Gemini bloqueada devido a safety settings. Razão: {response.prompt_feedback.block_reason}")
            else:
                # logger.warning("GeminiClient: Resposta não contém partes e não foi explicitamente bloqueada. Resposta vazia ou inesperada.")
                return "" # Ou levantar um erro
        except Exception as e:
            # logger.error(f"Erro ao chamar API Gemini: {e}", exc_info=True)
            # Mapear erros específicos do google-generativeai para LLMConnectionError, LLMResponseError, etc.
            # Ex: google.api_core.exceptions.PermissionDenied, google.api_core.exceptions.DeadlineExceeded
            self._handle_error(e, context="Gemini generate_response")
            return ""

    async def generate_response_async(
        self,
        messages: List[ChatMessage],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stop_sequences: Optional[List[str]] = None,
        **kwargs: Any
    ) -> LLMResponse:
        chat_history = self._prepare_chat_history(messages)
        generation_config = self._prepare_generation_config(temperature, max_tokens, stop_sequences, **kwargs)
        safety_settings = self._parse_safety_settings(kwargs)

        # logger.debug(f"GeminiClient - Enviando requisição (async): Modelo={self.model_name}, Temp={temperature}")
        print(f"DEBUG: GeminiClient - Enviando requisição (async): Modelo={self.model_name}, Temp={temperature}")
        try:
            response = await self.client.generate_content_async(
                contents=chat_history,
                generation_config=generation_config,
                safety_settings=safety_settings,
                stream=False
            )
            # logger.debug(f"GeminiClient - Resposta async recebida: {response}")
            if response.parts:
                return response.text.strip()
            elif response.prompt_feedback and response.prompt_feedback.block_reason:
                raise LLMResponseError(f"Resposta assíncrona do Gemini bloqueada. Razão: {response.prompt_feedback.block_reason}")
            else:
                return ""
        except Exception as e:
            self._handle_error(e, context="Gemini generate_response_async")
            return ""

    def stream_response(
        self,
        messages: List[ChatMessage],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stop_sequences: Optional[List[str]] = None,
        **kwargs: Any
    ) -> Iterator[LLMResponse]:
        chat_history = self._prepare_chat_history(messages)
        generation_config = self._prepare_generation_config(temperature, max_tokens, stop_sequences, **kwargs)
        safety_settings = self._parse_safety_settings(kwargs)

        # logger.debug(f"GeminiClient - Iniciando stream (sync): Modelo={self.model_name}, Temp={temperature}")
        print(f"DEBUG: GeminiClient - Iniciando stream (sync): Modelo={self.model_name}, Temp={temperature}")
        try:
            stream = self.client.generate_content(
                contents=chat_history,
                generation_config=generation_config,
                safety_settings=safety_settings,
                stream=True
            )
            for chunk in stream:
                # logger.debug(f"GeminiClient - Chunk recebido: {chunk}")
                if chunk.parts:
                    yield chunk.text # Gemini SDK v0.3+ chunk.text já é o conteúdo do chunk
                elif chunk.prompt_feedback and chunk.prompt_feedback.block_reason:
                    # logger.warning(f"GeminiClient: Stream bloqueado durante a geração. Razão: {chunk.prompt_feedback.block_reason}")
                    raise LLMResponseError(f"Stream do Gemini bloqueado. Razão: {chunk.prompt_feedback.block_reason}")
                    # break # ou continue, dependendo de como quer tratar
        except Exception as e:
            self._handle_error(e, context="Gemini stream_response")

    async def stream_response_async(
        self,
        messages: List[ChatMessage],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stop_sequences: Optional[List[str]] = None,
        **kwargs: Any
    ) -> AsyncIterator[LLMResponse]:
        chat_history = self._prepare_chat_history(messages)
        generation_config = self._prepare_generation_config(temperature, max_tokens, stop_sequences, **kwargs)
        safety_settings = self._parse_safety_settings(kwargs)

        # logger.debug(f"GeminiClient - Iniciando stream (async): Modelo={self.model_name}, Temp={temperature}")
        print(f"DEBUG: GeminiClient - Iniciando stream (async): Modelo={self.model_name}, Temp={temperature}")
        try:
            stream = await self.client.generate_content_async(
                contents=chat_history,
                generation_config=generation_config,
                safety_settings=safety_settings,
                stream=True
            )
            async for chunk in stream:
                # logger.debug(f"GeminiClient - Chunk async recebido: {chunk}")
                if chunk.parts:
                    yield chunk.text
                elif chunk.prompt_feedback and chunk.prompt_feedback.block_reason:
                    raise LLMResponseError(f"Stream assíncrono do Gemini bloqueado. Razão: {chunk.prompt_feedback.block_reason}")
        except Exception as e:
            self._handle_error(e, context="Gemini stream_response_async")

if __name__ == "__main__":
    print("--- Testando GeminiClient Diretamente (Requer GOOGLE_API_KEY configurada) ---")

    if not os.getenv("GOOGLE_API_KEY"):
        print("AVISO: A variável de ambiente GOOGLE_API_KEY não está definida. Os testes podem falhar.")

    try:
        # Use um modelo Gemini apropriado, ex: "gemini-pro" ou "gemini-1.5-flash-latest"
        client = GeminiClient(model_name="gemini-pro") 
        print(f"Cliente Gemini instanciado para modelo: {client.model_name}")

        sample_messages_gemini: List[ChatMessage] = [
            {"role": "user", "content": "Olá! Qual é a capital da Alemanha?"}
        ]
        # Exemplo com histórico e role system (que será convertido)
        sample_messages_hist: List[ChatMessage] = [
            {"role": "system", "content": "Aja como um geógrafo experiente."},
            {"role": "user", "content": "Qual o maior rio do mundo?"},
            {"role": "assistant", "content": "O maior rio do mundo em extensão é o Rio Amazonas."},
            {"role": "user", "content": "E em volume de água?"}
        ]

        # Teste de generate_response (síncrono)
        print("\nTestando generate_response (sync) para capital da Alemanha...")
        try:
            response_sync = client.generate_response(sample_messages_gemini, temperature=0.5, max_tokens=50)
            print(f"Resposta (sync): {response_sync}")
        except Exception as e_sync:
            print(f"Erro durante generate_response (sync): {type(e_sync).__name__} - {e_sync}")

        print("\nTestando generate_response (sync) com histórico para volume do rio...")
        try:
            response_sync_hist = client.generate_response(sample_messages_hist, temperature=0.7, max_tokens=100)
            print(f"Resposta (sync com histórico): {response_sync_hist}")
        except Exception as e_sync_hist:
            print(f"Erro durante generate_response (sync com histórico): {type(e_sync_hist).__name__} - {e_sync_hist}")

        # Teste de stream_response (síncrono)
        print("\nTestando stream_response (sync) para capital da Alemanha...")
        try:
            print("Resposta (stream sync): ", end="")
            for chunk_sync in client.stream_response(sample_messages_gemini, temperature=0.5, max_tokens=50):
                print(chunk_sync, end="", flush=True)
            print("\n--- Fim do stream sync ---")
        except Exception as e_stream_sync:
            print(f"\nErro durante stream_response (sync): {type(e_stream_sync).__name__} - {e_stream_sync}")

        import asyncio
        async def run_gemini_async_tests():
            print("\nTestando generate_response_async para capital da Alemanha...")
            try:
                response_async = await client.generate_response_async(sample_messages_gemini, temperature=0.5, max_tokens=50)
                print(f"Resposta (async): {response_async}")
            except Exception as e_async:
                print(f"Erro durante generate_response_async: {type(e_async).__name__} - {e_async}")

            print("\nTestando stream_response_async para capital da Alemanha...")
            try:
                print("Resposta (stream async): ", end="")
                async for chunk_async in client.stream_response_async(sample_messages_gemini, temperature=0.5, max_tokens=50):
                    print(chunk_async, end="", flush=True)
                print("\n--- Fim do stream async ---")
            except Exception as e_stream_async:
                print(f"\nErro durante stream_response_async: {type(e_stream_async).__name__} - {e_stream_async}")

        print("\nExecutando testes assíncronos do GeminiClient...")
        asyncio.run(run_gemini_async_tests())

    except LLMConfigurationError as lce:
        print(f"Erro de Configuração do Cliente Gemini: {lce}")
    except Exception as e:
        print(f"Erro inesperado durante os testes do GeminiClient: {type(e).__name__} - {e}")

    print("\n--- Testes do GeminiClient concluídos. Verifique os resultados. ---")

