"""
Cliente LLM Base Abstrato
Arquivo: src/llm_clients/base_client.py

Este módulo define a classe abstrata `BaseLLMClient` que serve como uma interface
comum para todas as implementações de clientes LLM específicos de provedores
(ex: OpenAI, Google Gemini, Anthropic Claude, Groq, etc.).

O objetivo é permitir que o sistema interaja com diferentes LLMs de forma
consistente, facilitando a troca de provedores ou modelos com alterações mínimas
no código do agente.

Cada cliente LLM específico deverá herdar desta classe e implementar os métodos
abstratos, como `generate_response` e, opcionalmente, `stream_response`.

Boas Práticas e Considerações AI-Friendly:
- **Interface Comum:** Garante que todos os LLMs possam ser chamados da mesma maneira,
  simplificando a lógica do agente.
- **Extensibilidade:** Facilita a adição de suporte a novos LLMs no futuro; basta
  criar uma nova classe de cliente que herde de `BaseLLMClient`.
- **Configuração Padronizada:** Embora a inicialização (`__init__`) possa variar
  ligeiramente entre clientes (devido a diferentes SDKs e parâmetros de autenticação),
  os métodos de interação principais devem ser consistentes.
- **Tratamento de Erros:** A classe base pode definir um conjunto comum de exceções
  personalizadas (ex: `LLMConnectionError`, `LLMResponseError`) que os clientes
  específicos podem levantar, permitindo um tratamento de erro uniforme no agente.
- **Streaming:** Suporte para streaming de respostas é crucial para interações em tempo real
  e uma melhor experiência do usuário. A interface deve prever isso.
- **Referência Cruzada:**
    - Esta classe base será herdada por clientes específicos como `OpenAIClient`,
      `GeminiClient`, etc., localizados em `src/llm_clients/`.
    - O `LLMLoader` em `src/llm_clients/loader.py` será responsável por instanciar
      o cliente LLM apropriado com base na configuração do agente.
    - O `MainAgent` (e subagentes) em `src/agents/` utilizará uma instância de um
      cliente derivado de `BaseLLMClient` para interagir com o LLM.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, AsyncIterator, Iterator, Union, Optional

# Definição de tipos comuns para mensagens de chat (pode ser expandido)
ChatMessage = Dict[str, str] # Ex: {"role": "user", "content": "Olá"}
LLMResponse = Union[str, Dict[str, Any]] # Resposta pode ser string ou um JSON mais complexo

class BaseLLMClient(ABC):
    """
    Classe base abstrata para todos os clientes LLM.

    Define a interface que os clientes LLM específicos do provedor devem implementar.
    """

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None, **kwargs: Any):
        """
        Construtor base para clientes LLM.

        Args:
            api_key (Optional[str]): A chave de API para o provedor LLM.
            model_name (Optional[str]): O nome/identificador do modelo LLM a ser usado.
            **kwargs: Argumentos adicionais específicos do provedor (ex: base_url, timeout).
        """
        self.api_key = api_key
        self.model_name = model_name
        self.client_specific_configs = kwargs
        # logger.info(f"BaseLLMClient inicializado para modelo: {model_name}")
        print(f"DEBUG: BaseLLMClient (ou derivado) inicializado para modelo: {model_name}")

    @abstractmethod
    def generate_response(
        self,
        messages: List[ChatMessage],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stop_sequences: Optional[List[str]] = None,
        **kwargs: Any
    ) -> LLMResponse:
        """
        Gera uma resposta completa (não-streaming) do LLM.

        Args:
            messages (List[ChatMessage]): Uma lista de mensagens representando o histórico
                                          da conversa e o prompt atual.
            temperature (float): Parâmetro de temperatura para controlar a aleatoriedade.
            max_tokens (Optional[int]): Número máximo de tokens a serem gerados.
            stop_sequences (Optional[List[str]]): Sequências de texto que, se geradas,
                                                  farão o LLM parar.
            **kwargs: Argumentos adicionais específicos do provedor para a chamada de geração.

        Returns:
            LLMResponse: A resposta gerada pelo LLM (pode ser uma string ou um dicionário).

        Raises:
            NotImplementedError: Se o método não for implementado pela subclasse.
            LLMConnectionError: Se houver problemas de conexão com a API do LLM.
            LLMResponseError: Se a API do LLM retornar um erro ou uma resposta inválida.
            LLMConfigurationError: Se houver um problema com a configuração do cliente.
        """
        raise NotImplementedError("O método generate_response deve ser implementado pela subclasse.")

    async def generate_response_async(
        self,
        messages: List[ChatMessage],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stop_sequences: Optional[List[str]] = None,
        **kwargs: Any
    ) -> LLMResponse:
        """
        Versão assíncrona de generate_response.
        Por padrão, levanta NotImplementedError. Subclasses devem sobrescrever se suportarem async.
        """
        raise NotImplementedError("O método generate_response_async não foi implementado por esta subclasse.")

    def stream_response(
        self,
        messages: List[ChatMessage],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stop_sequences: Optional[List[str]] = None,
        **kwargs: Any
    ) -> Iterator[LLMResponse]: # Ou Iterator[str] se sempre retornar chunks de texto
        """
        Gera uma resposta do LLM em modo streaming, retornando chunks da resposta à medida que são gerados.

        Args:
            messages (List[ChatMessage]): Histórico da conversa e prompt.
            temperature (float): Parâmetro de temperatura.
            max_tokens (Optional[int]): Máximo de tokens.
            stop_sequences (Optional[List[str]]): Sequências de parada.
            **kwargs: Argumentos adicionais específicos do provedor.

        Yields:
            LLMResponse: Chunks da resposta do LLM.

        Raises:
            NotImplementedError: Se o método não for implementado ou não suportado pela subclasse.
        """
        raise NotImplementedError("O método stream_response não foi implementado ou não é suportado por esta subclasse.")

    async def stream_response_async(
        self,
        messages: List[ChatMessage],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stop_sequences: Optional[List[str]] = None,
        **kwargs: Any
    ) -> AsyncIterator[LLMResponse]: # Ou AsyncIterator[str]
        """
        Versão assíncrona de stream_response.
        Por padrão, levanta NotImplementedError. Subclasses devem sobrescrever se suportarem async streaming.
        """
        raise NotImplementedError("O método stream_response_async não foi implementado ou não é suportado por esta subclasse.")

    @abstractmethod
    def get_provider_name(self) -> str:
        """
        Retorna o nome do provedor LLM (ex: "openai", "google", "anthropic").
        """
        raise NotImplementedError("O método get_provider_name deve ser implementado pela subclasse.")

    def _handle_error(self, error: Any, context: str = "LLM API call") -> None:
        """
        Método auxiliar para tratamento de erros comuns da API (pode ser sobrescrito).
        Idealmente, levantaria exceções personalizadas como LLMConnectionError, LLMResponseError.
        """
        # logger.error(f"Erro durante {context} com {self.get_provider_name()}: {error}", exc_info=True)
        print(f"ERRO: Durante {context} com {self.get_provider_name()}: {error}")
        # Exemplo: raise LLMResponseError(str(error)) from error
        raise Exception(f"Erro na chamada da API LLM ({self.get_provider_name()}): {error}") from error

# Exceções personalizadas (podem ser definidas em um módulo de exceções separado)
class LLMConfigurationError(Exception):
    """Erro relacionado à configuração do cliente LLM."""
    pass

class LLMConnectionError(Exception):
    """Erro de conexão com a API do LLM."""
    pass

class LLMResponseError(Exception):
    """Erro na resposta da API do LLM (ex: status code inválido, resposta malformada)."""
    pass

class LLMTimeoutError(LLMConnectionError):
    """Erro de timeout durante a chamada à API do LLM."""
    pass

if __name__ == "__main__":
    print("--- Testando a Definição de BaseLLMClient (Não Executável Diretamente) ---")
    
    # Esta classe é abstrata e não pode ser instanciada diretamente.
    # Para testar, você precisaria de uma implementação concreta.
    class MockLLMClient(BaseLLMClient):
        def generate_response(self, messages: List[ChatMessage], **kwargs) -> LLMResponse:
            print(f"MockLLMClient.generate_response chamado com: {messages}")
            return f"Resposta mock para: {messages[-1]["content"]}"
        
        def get_provider_name(self) -> str:
            return "mock_provider"

    try:
        mock_client = MockLLMClient(api_key="test_key", model_name="mock_model")
        print(f"Cliente MockLLMClient instanciado com sucesso: Provedor {mock_client.get_provider_name()}, Modelo {mock_client.model_name}")
        response = mock_client.generate_response([{"role": "user", "content": "Olá, mundo!"}])
        print(f"Resposta do MockLLMClient: {response}")

        # Testar chamada a método não implementado (stream_response)
        try:
            for _ in mock_client.stream_response([{"role": "user", "content": "Stream test"}]):
                pass
        except NotImplementedError as nie:
            print(f"Capturado erro esperado ao chamar stream_response não implementado: {nie}")

    except Exception as e:
        print(f"Erro inesperado durante o teste do MockLLMClient: {e}")

    print("\n--- BaseLLMClient e exceções personalizadas definidas. ---")

