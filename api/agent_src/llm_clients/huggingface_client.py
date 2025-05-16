"""
Cliente LLM para Hugging Face Hub (Modelos Diversos)
Arquivo: src/llm_clients/huggingface_client.py

Este módulo implementa o `HuggingFaceClient`, uma classe que herda de `BaseLLMClient`
e fornece uma interface para interagir com modelos hospedados no Hugging Face Hub
(ex: Llama, DeepSeek, Qwen, e outros modelos de código aberto) através da API de Inferência
ou bibliotecas compatíveis.

Utiliza a biblioteca `huggingface_hub` para interações com a API de Inferência.

Boas Práticas e Considerações AI-Friendly:
- **Flexibilidade de Modelo:** Permite usar uma vasta gama de modelos disponíveis no Hub.
- **API de Inferência vs. Local:** Este cliente foca na API de Inferência para simplicidade.
  Para inferência local com `transformers`, uma abordagem diferente seria necessária (mais complexa
  para um template genérico de "cliente" como este, pois envolve gerenciamento de downloads de modelos,
  hardware, etc.).
- **Tratamento de Erros:** Mapeia erros da API do Hugging Face para exceções padronizadas.
- **Referência Cruzada:**
    - Herda de `BaseLLMClient`.
    - Será registrado no `LLM_PROVIDER_MAP` em `loader.py`.
    - A API key (Hugging Face Token) é esperada da variável de ambiente (ex: `HUGGINGFACE_HUB_TOKEN`).
"""
import os
import json
from typing import List, Dict, Any, Optional, Iterator, AsyncIterator

try:
    from huggingface_hub import InferenceClient, HfFolder
    from huggingface_hub.hf_api import HfApi # Para listar modelos, se necessário
except ImportError:
    raise ImportError(
        "A biblioteca huggingface_hub não está instalada. Por favor, instale-a com: pip install huggingface_hub"
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

# Importar o logger configurado
# from my_vertical_agent.src.utils.logger import get_logger
# logger = get_logger(__name__)

class HuggingFaceClient(BaseLLMClient):
    """
    Cliente LLM para interagir com modelos via Hugging Face Inference API.
    Suporta tarefas como text-generation e conversational.
    """
    PROVIDER_NAME = "huggingface"

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None, **kwargs: Any):
        super().__init__(api_key=api_key, model_name=model_name, **kwargs)

        if not self.model_name:
            raise LLMConfigurationError("ID do modelo Hugging Face (model_name) não especificado. Ex: \"mistralai/Mixtral-8x7B-Instruct-v0.1\"")
        
        # A API key é o Hugging Face User Access Token
        _api_key = self.api_key or os.getenv("HUGGINGFACE_HUB_TOKEN") or HfFolder.get_token()
        if not _api_key:
            # logger.warning("Token do Hugging Face Hub não fornecido nem encontrado. Algumas APIs podem não funcionar.")
            print("AVISO: HuggingFaceClient - Token do Hugging Face Hub (HUGGINGFACE_HUB_TOKEN) não encontrado. Algumas APIs podem ser restritas.")
            # A InferenceClient pode funcionar para modelos públicos sem token, mas é recomendado.

        try:
            # A InferenceClient pode receber o token diretamente.
            # Se o token for None, ela tentará usar o token logado globalmente (via huggingface-cli login)
            self.client = InferenceClient(model=self.model_name, token=_api_key, timeout=self.client_specific_configs.get("timeout", 30.0))
            # logger.info(f"Cliente Hugging Face inicializado para modelo: {self.model_name}")
            print(f"DEBUG: HuggingFaceClient inicializado para modelo: {self.model_name}")
        except Exception as e:
            # logger.error(f"Erro ao inicializar o cliente Hugging Face: {e}", exc_info=True)
            raise LLMConfigurationError(f"Falha ao inicializar o cliente Hugging Face. Detalhes: {e}") from e

    def get_provider_name(self) -> str:
        return self.PROVIDER_NAME

    def _prepare_hf_chat_payload(self, messages: List[ChatMessage], temperature: float, max_tokens: Optional[int], stop_sequences: Optional[List[str]], **kwargs: Any) -> Dict[str, Any]:
        """
        Prepara o payload para a API de conversação do Hugging Face.
        O formato exato pode variar um pouco dependendo do modelo, mas geralmente
        a API `conversational` espera um histórico de `past_user_inputs` e `generated_responses`,
        e o `text` atual do usuário.
        Para modelos de text-generation que suportam formato de chat (ex: Llama, Mixtral instruct),
        geralmente se formata o prompt inteiro como uma string única com tokens especiais.
        A `InferenceClient.chat_completion` tenta abstrair isso, aceitando um formato similar ao da OpenAI.
        """
        # Usando o formato esperado por `InferenceClient.chat_completion` que é similar ao OpenAI
        hf_messages = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            # Roles comuns: system, user, assistant
            hf_messages.append({"role": role, "content": content})
        
        payload = {
            "messages": hf_messages,
            "temperature": max(temperature, 0.01), # Temp 0 pode ser problemático para alguns modelos HF
            "max_tokens": max_tokens,
            # "stop_sequences": stop_sequences, # `chat_completion` pode não suportar `stop_sequences` diretamente.
                                              # Pode ser necessário usar `stop` como parâmetro de `generate_kwargs`.
            "stream": False, # Definido pelo método chamador
        }
        if stop_sequences:
             payload["stop"] = stop_sequences # Para `generate` e `generate_stream` em `text_generation`

        # Parâmetros adicionais podem ser passados via kwargs e adicionados aqui se relevantes
        # para `chat_completion` ou `text_generation`.
        # Ex: top_p, top_k, repetition_penalty
        # payload.update(kwargs) # Cuidado para não sobrescrever chaves importantes
        if "top_p" in kwargs: payload["top_p"] = kwargs["top_p"]
        if "top_k" in kwargs: payload["top_k"] = kwargs["top_k"]
        if "repetition_penalty" in kwargs: payload["repetition_penalty"] = kwargs["repetition_penalty"]
        
        return payload

    def generate_response(
        self,
        messages: List[ChatMessage],
        temperature: float = 0.7,
        max_tokens: Optional[int] = 512, # Default razoável para HF Inference API
        stop_sequences: Optional[List[str]] = None,
        **kwargs: Any
    ) -> LLMResponse:
        payload = self._prepare_hf_chat_payload(messages, temperature, max_tokens, stop_sequences, **kwargs)
        payload["stream"] = False
        
        # logger.debug(f"HuggingFaceClient - Enviando requisição (sync) para chat_completion: {self.model_name}")
        print(f"DEBUG: HuggingFaceClient - Enviando requisição (sync): Modelo={self.model_name}, Temp={payload["temperature"]}")
        try:
            # A API `chat_completion` é mais nova e visa compatibilidade com formato OpenAI.
            response = self.client.chat_completion(**payload)
            # logger.debug(f"HuggingFaceClient - Resposta recebida: {response}")
            
            # O objeto de resposta de `chat_completion` é similar ao da OpenAI:
            # response.choices[0].message.content
            if response.choices and response.choices[0].message and response.choices[0].message.content:
                return response.choices[0].message.content.strip()
            else:
                # Fallback para text_generation se chat_completion não funcionar ou não for adequada
                # logger.warning("HuggingFaceClient: chat_completion não retornou conteúdo esperado. Tentando text_generation.")
                # Para text_generation, precisamos formatar o prompt como uma string única.
                # Esta é uma simplificação; uma formatação de prompt robusta é complexa.
                prompt_str = "\n".join([f"{m["role"]}: {m["content"]}" for m in messages])
                gen_params = {
                    "temperature": payload["temperature"],
                    "max_new_tokens": payload["max_tokens"],
                    "return_full_text": False # Para obter apenas o texto gerado
                }
                if "stop" in payload: gen_params["stop_sequences"] = payload["stop"]
                if "top_p" in payload: gen_params["top_p"] = payload["top_p"]
                if "top_k" in payload: gen_params["top_k"] = payload["top_k"]
                if "repetition_penalty" in payload: gen_params["repetition_penalty"] = payload["repetition_penalty"]

                # logger.debug(f"HuggingFaceClient - Tentando text_generation com prompt: {prompt_str[:100]}...")
                text_gen_response = self.client.text_generation(prompt=prompt_str, **gen_params)
                if isinstance(text_gen_response, str):
                    return text_gen_response.strip()
                else:
                    raise LLMResponseError("Resposta da API Hugging Face (text_generation) não é uma string ou está vazia.")

        except Exception as e:
            # logger.error(f"Erro ao chamar API Hugging Face: {e}", exc_info=True)
            # Mapear erros específicos da huggingface_hub (ex: HfHubHTTPError) se necessário
            # from huggingface_hub.utils import HfHubHTTPError
            # if isinstance(e, HfHubHTTPError):
            #     if e.response.status_code == 401: raise LLMConfigurationError("HF Token inválido ou não autorizado.")
            #     if e.response.status_code == 429: raise LLMResponseError("Rate limit HF.")
            self._handle_error(e, context="HuggingFace generate_response")
            return ""

    async def generate_response_async(
        self,
        messages: List[ChatMessage],
        temperature: float = 0.7,
        max_tokens: Optional[int] = 512,
        stop_sequences: Optional[List[str]] = None,
        **kwargs: Any
    ) -> LLMResponse:
        # A biblioteca huggingface_hub.InferenceClient não tem métodos async diretos para chat_completion ou text_generation.
        # Para chamadas assíncronas, precisaríamos usar `aiohttp` manualmente ou uma lib async compatível.
        # Por simplicidade, este template pode levantar NotImplementedError ou executar a versão síncrona em um executor.
        # logger.warning("HuggingFaceClient.generate_response_async não é implementado de forma nativamente assíncrona. Executando sincronicamente.")
        # Para uma implementação async real, seria necessário refatorar usando httpx ou aiohttp.
        # Por enquanto, vamos chamar a síncrona (NÃO IDEAL PARA PRODUÇÃO ASYNC)
        # return self.generate_response(messages, temperature, max_tokens, stop_sequences, **kwargs)
        raise NotImplementedError("HuggingFaceClient.generate_response_async não possui implementação async nativa com InferenceClient. Considere executar a versão sync em um thread executor.")

    def stream_response(
        self,
        messages: List[ChatMessage],
        temperature: float = 0.7,
        max_tokens: Optional[int] = 512,
        stop_sequences: Optional[List[str]] = None,
        **kwargs: Any
    ) -> Iterator[LLMResponse]:
        payload = self._prepare_hf_chat_payload(messages, temperature, max_tokens, stop_sequences, **kwargs)
        # logger.debug(f"HuggingFaceClient - Iniciando stream (sync) para chat_completion: {self.model_name}")
        print(f"DEBUG: HuggingFaceClient - Iniciando stream (sync): Modelo={self.model_name}, Temp={payload["temperature"]}")
        try:
            # `chat_completion` com stream=True
            stream_payload = payload.copy()
            stream_payload["stream"] = True
            for chunk_obj in self.client.chat_completion(**stream_payload):
                # logger.debug(f"HuggingFaceClient - Chunk de stream recebido: {chunk_obj}")
                # O formato do chunk para chat_completion stream é similar ao da OpenAI
                if chunk_obj.choices and chunk_obj.choices[0].delta and chunk_obj.choices[0].delta.content:
                    yield chunk_obj.choices[0].delta.content
        except Exception as e_chat_stream:
            # logger.warning(f"HuggingFaceClient: Erro no stream de chat_completion ({e_chat_stream}). Tentando text_generation stream.")
            # Fallback para text_generation stream
            try:
                prompt_str = "\n".join([f"{m["role"]}: {m["content"]}" for m in messages])
                gen_params = {
                    "temperature": payload["temperature"],
                    "max_new_tokens": payload["max_tokens"],
                    "return_full_text": False
                }
                if "stop" in payload: gen_params["stop_sequences"] = payload["stop"]
                # ... (outros params de gen_params como em generate_response)

                # logger.debug(f"HuggingFaceClient - Tentando text_generation stream com prompt: {prompt_str[:100]}...")
                for chunk_text in self.client.text_generation(prompt=prompt_str, stream=True, **gen_params):
                    if isinstance(chunk_text, str):
                        yield chunk_text
                    # Alguns modelos podem retornar dicts com tokens, etc. Adaptar se necessário.
            except Exception as e_text_gen_stream:
                self._handle_error(e_text_gen_stream, context="HuggingFace stream_response (fallback text_generation)")

    async def stream_response_async(
        self,
        messages: List[ChatMessage],
        temperature: float = 0.7,
        max_tokens: Optional[int] = 512,
        stop_sequences: Optional[List[str]] = None,
        **kwargs: Any
    ) -> AsyncIterator[LLMResponse]:
        # Similar à versão async de generate_response, não há suporte async nativo.
        # logger.warning("HuggingFaceClient.stream_response_async não é implementado de forma nativamente assíncrona.")
        raise NotImplementedError("HuggingFaceClient.stream_response_async não possui implementação async nativa com InferenceClient.")

if __name__ == "__main__":
    print("--- Testando HuggingFaceClient Diretamente (Requer HUGGINGFACE_HUB_TOKEN opcionalmente) ---")

    # É recomendado ter HUGGINGFACE_HUB_TOKEN configurado para evitar rate limits e acessar modelos privados.
    if not (os.getenv("HUGGINGFACE_HUB_TOKEN") or HfFolder.get_token()):
        print("AVISO: HUGGINGFACE_HUB_TOKEN não está definido. Testes podem usar acesso anônimo com limitações.")

    # Modelo de exemplo (pode precisar de um que seja gratuito e rápido para teste)
    # Modelos populares: "mistralai/Mixtral-8x7B-Instruct-v0.1", "meta-llama/Llama-2-7b-chat-hf"
    # Para teste rápido, um modelo menor como "gpt2" pode funcionar para text_generation, mas não para chat_completion.
    # Usaremos um modelo instruct que geralmente funciona bem com o formato de chat.
    # NOTA: A disponibilidade e performance de modelos na Inference API gratuita podem variar.
    test_model_id = "mistralai/Mistral-7B-Instruct-v0.1" # Ou outro modelo instruct popular
    
    try:
        client = HuggingFaceClient(model_name=test_model_id)
        print(f"Cliente HuggingFace instanciado para modelo: {client.model_name}")

        sample_messages_hf: List[ChatMessage] = [
            {"role": "user", "content": "Explique o conceito de Machine Learning em uma frase."}
        ]
        sample_messages_hf_chat: List[ChatMessage] = [
            {"role": "system", "content": "Você é um assistente conciso."},
            {"role": "user", "content": "Qual a capital da Itália?"}
        ]

        # Teste de generate_response (síncrono)
        print(f"\nTestando generate_response (sync) com {test_model_id}...")
        try:
            response_sync = client.generate_response(sample_messages_hf_chat, temperature=0.5, max_tokens=50)
            print(f"Resposta (sync): {response_sync}")
        except Exception as e_sync:
            print(f"Erro durante generate_response (sync): {type(e_sync).__name__} - {e_sync}")

        # Teste de stream_response (síncrono)
        print(f"\nTestando stream_response (sync) com {test_model_id}...")
        try:
            print("Resposta (stream sync): ", end="")
            for chunk_sync in client.stream_response(sample_messages_hf_chat, temperature=0.5, max_tokens=50):
                print(chunk_sync, end="", flush=True)
            print("\n--- Fim do stream sync ---")
        except Exception as e_stream_sync:
            print(f"\nErro durante stream_response (sync): {type(e_stream_sync).__name__} - {e_stream_sync}")
        
        print("\nLembre-se: Métodos Async para HuggingFaceClient não são implementados nativamente e levantarão NotImplementedError.")

    except LLMConfigurationError as lce:
        print(f"Erro de Configuração do Cliente HuggingFace: {lce}")
    except Exception as e:
        print(f"Erro inesperado durante os testes do HuggingFaceClient: {type(e).__name__} - {e}")

    print("\n--- Testes do HuggingFaceClient concluídos. Verifique os resultados. ---")

