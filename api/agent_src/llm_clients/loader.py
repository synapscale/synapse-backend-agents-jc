"""
Carregador de Clientes LLM (LLM Loader)
Arquivo: src/llm_clients/loader.py

Este módulo é responsável por carregar e instanciar o cliente LLM apropriado
(ex: OpenAI, Gemini, Claude, Groq, HuggingFace) com base na configuração fornecida pelo agente.

Ele atua como uma fábrica que abstrai a lógica de seleção e inicialização
dos diferentes clientes LLM, permitindo que o código do agente permaneça agnóstico
ao provedor LLM específico que está sendo usado.

Boas Práticas e Considerações AI-Friendly:
- **Configuração Centralizada:** A decisão de qual LLM usar é baseada em arquivos de
  configuração (ex: `config.yaml` do agente e `config/.env` para API keys),
  tornando a troca de LLMs uma questão de alteração de configuração, não de código.
- **Desacoplamento:** O loader desacopla o agente da implementação específica do cliente LLM.
  O agente apenas solicita um "cliente LLM" e o loader se encarrega de fornecer a instância correta.
- **Extensibilidade:** Para adicionar suporte a um novo provedor LLM, basta:
    1. Criar uma nova classe de cliente que herde de `BaseLLMClient` (em `src/llm_clients/`).
    2. Registrar o novo cliente no dicionário `LLM_PROVIDER_MAP` neste loader.
    3. Adicionar as opções de configuração relevantes (ex: API key no `.env`, nome do provedor no YAML).
- **Tratamento de Erros de Configuração:** O loader deve lidar graciosamente com configurações
  inválidas ou ausentes, levantando exceções claras (ex: `LLMConfigurationError`).
- **Referência Cruzada:**
    - Importa `BaseLLMClient` e exceções de `src/llm_clients/base_client.py`.
    - Importa os clientes LLM específicos (ex: `OpenAIClient`, `GeminiClient`) de seus
      respectivos módulos em `src/llm_clients/`.
    - Será utilizado pelo `MainAgent` (e subagentes) em `src/agents/` para obter uma instância
      do cliente LLM configurado.
"""
import os
from typing import Dict, Type, Optional, Any, List # Adicionado List para ChatMessage no __main__

from .base_client import BaseLLMClient, LLMConfigurationError, ChatMessage # Adicionado ChatMessage
from .openai_client import OpenAIClient
from .gemini_client import GeminiClient
from .anthropic_client import AnthropicClient
from .groq_client import GroqClient
from .huggingface_client import HuggingFaceClient

# Importar o logger configurado (se existir um central)
# from my_vertical_agent.src.utils.logger import get_logger
# logger = get_logger(__name__)

# Mapeamento de nomes de provedores (como definidos na config YAML) para suas classes de cliente.
LLM_PROVIDER_MAP: Dict[str, Type[BaseLLMClient]] = {
    "openai": OpenAIClient,
    "google_gemini": GeminiClient,
    "anthropic_claude": AnthropicClient,
    "groq": GroqClient,
    "huggingface": HuggingFaceClient,
    # Adicionar outros provedores aqui conforme são implementados
}

def load_llm_client(llm_config: Dict[str, Any]) -> BaseLLMClient:
    """
    Carrega e instancia um cliente LLM com base na configuração fornecida.

    A configuração `llm_config` é tipicamente lida do arquivo `config.yaml` do agente,
    que por sua vez pode referenciar variáveis de ambiente para API keys.

    Args:
        llm_config (Dict[str, Any]): Um dicionário contendo a configuração do LLM.
            Espera-se que contenha pelo menos:
            - `provider` (str): O nome do provedor LLM (ex: "openai", "google_gemini").
            - `model_name` (str): O nome/identificador do modelo a ser usado.
            - `api_key_env_var` (Optional[str]): O nome da variável de ambiente que contém a API key.
                                                Se não fornecido, o construtor do cliente tentará obter a key
                                                de uma variável de ambiente padrão (ex: OPENAI_API_KEY).
            - `api_key` (Optional[str]): A API key diretamente. Se fornecida, tem precedência sobre api_key_env_var.
            - `client_specific_configs` (Optional[Dict[str, Any]]): Parâmetros específicos para o construtor do cliente
                                                               (ex: timeout, max_retries, base_url).

    Returns:
        BaseLLMClient: Uma instância do cliente LLM configurado.

    Raises:
        LLMConfigurationError: Se o provedor não for suportado, a API key não for encontrada (se obrigatória),
                               ou a configuração for inválida.
    """
    provider_name = llm_config.get("provider")
    model_name = llm_config.get("model_name")
    
    # Prioriza api_key direta, depois api_key_env_var, depois o cliente tenta sua env_var padrão.
    direct_api_key = llm_config.get("api_key")
    api_key_env_var_name = llm_config.get("api_key_env_var")
    
    client_specific_configs = llm_config.get("client_specific_configs", {})

    # logger.info(f"Tentando carregar cliente LLM para provedor: {provider_name}, modelo: {model_name}")
    print(f"DEBUG: LLMLoader - Tentando carregar LLM: Provedor={provider_name}, Modelo={model_name}")

    if not provider_name:
        raise LLMConfigurationError("O campo 'provider' do LLM não foi especificado na configuração.")
    if not model_name:
        raise LLMConfigurationError(f"O campo 'model_name' para o provedor {provider_name} não foi especificado.")

    client_class = LLM_PROVIDER_MAP.get(provider_name.lower())
    if not client_class:
        supported_providers = ", ".join(LLM_PROVIDER_MAP.keys()) or "Nenhum"
        raise LLMConfigurationError(
            f"Provedor LLM não suportado: {provider_name}. Provedores suportados: {supported_providers}. "
            f"Verifique se o cliente para {provider_name} está implementado e registrado no LLMLoader."
        )

    final_api_key: Optional[str] = direct_api_key
    if not final_api_key and api_key_env_var_name:
        final_api_key = os.getenv(api_key_env_var_name)
        if not final_api_key:
            print(f"AVISO: LLMLoader - Variável de ambiente {api_key_env_var_name} para {provider_name} não definida ou vazia.")
    
    # logger.debug(f"Instanciando cliente {client_class.__name__} com modelo {model_name}, API Key: {'Presente' if final_api_key else 'Ausente/Padrão do Cliente'}, Configs: {client_specific_configs}")
    try:
        instance = client_class(
            api_key=final_api_key, 
            model_name=model_name, 
            **client_specific_configs
        )
        # logger.info(f"Cliente LLM {instance.get_provider_name()} carregado com sucesso para o modelo {instance.model_name}.")
        print(f"DEBUG: LLMLoader - Cliente {instance.get_provider_name()} carregado para modelo {instance.model_name}.")
        return instance
    except LLMConfigurationError as e_conf:
        raise e_conf
    except Exception as e:
        # logger.error(f"Erro ao instanciar o cliente LLM {client_class.__name__} para o provedor {provider_name}: {e}", exc_info=True)
        raise LLMConfigurationError(
            f"Falha ao instanciar o cliente LLM {client_class.__name__} para o provedor {provider_name}. "
            f"Verifique a configuração e as credenciais. Detalhes: {e}"
        ) from e

if __name__ == "__main__":
    print("--- Testando LLMLoader (Requer Variáveis de Ambiente para API Keys Reais) ---")

    # Configurações de exemplo para cada provedor
    # NOTA: Para testes reais, as API keys DEVEM estar configuradas nas variáveis de ambiente corretas.
    # (ex: OPENAI_API_KEY, GOOGLE_API_KEY, ANTHROPIC_API_KEY, GROQ_API_KEY, HUGGINGFACE_HUB_TOKEN)

    test_configs = [
        {
            "provider": "openai", 
            "model_name": os.getenv("OPENAI_DEFAULT_MODEL_NAME", "gpt-3.5-turbo"), 
            # api_key_env_var: "OPENAI_API_KEY" # O cliente já busca OPENAI_API_KEY por padrão
            "client_specific_configs": {"timeout": 10}
        },
        {
            "provider": "google_gemini", 
            "model_name": os.getenv("GOOGLE_GEMINI_DEFAULT_MODEL_NAME", "gemini-pro"),
            # api_key_env_var: "GOOGLE_API_KEY"
        },
        {
            "provider": "anthropic_claude", 
            "model_name": os.getenv("ANTHROPIC_CLAUDE_DEFAULT_MODEL_NAME", "claude-3-haiku-20240307"),
            # api_key_env_var: "ANTHROPIC_API_KEY"
        },
        {
            "provider": "groq", 
            "model_name": os.getenv("GROQ_DEFAULT_MODEL_NAME", "llama3-8b-8192"),
            # api_key_env_var: "GROQ_API_KEY"
        },
        {
            "provider": "huggingface", 
            "model_name": os.getenv("HUGGINGFACE_DEFAULT_MODEL_ID", "mistralai/Mistral-7B-Instruct-v0.1"),
            # api_key_env_var: "HUGGINGFACE_HUB_TOKEN"
            "client_specific_configs": {"timeout": 45}
        },
        {
            "provider": "nonexistent_provider", 
            "model_name": "test-model"
        }
    ]

    sample_messages: List[ChatMessage] = [
        {"role": "user", "content": "Olá! Qual é o seu nome e capacidade principal? Responda brevemente."}
    ]

    for i, config in enumerate(test_configs):
        print(f"\n--- Teste {i+1}: Carregando Provedor ", config.get("provider"), "---")
        try:
            # Simular que as API keys estão no ambiente ou são buscadas pelo construtor do cliente
            # Se uma api_key_env_var específica fosse definida no config, o loader tentaria usá-la.
            # Como não está, cada cliente tentará sua variável de ambiente padrão (ex: OPENAI_API_KEY).
            
            client_instance = load_llm_client(config)
            print(f"Cliente carregado com sucesso: {client_instance.get_provider_name()}, Modelo: {client_instance.model_name}")
            
            # Teste de geração de resposta (pode falhar se a API key real não estiver configurada)
            # E para HuggingFace, o generate_response_async não é implementado.
            if client_instance.get_provider_name() != "huggingface": # HF sync pode ser problemático sem config completa
                try:
                    print("Gerando resposta...")
                    response = client_instance.generate_response(sample_messages, temperature=0.1, max_tokens=50)
                    print(f"Resposta do {client_instance.get_provider_name()}: {response}")
                except NotImplementedError:
                    print(f"generate_response não implementado para {client_instance.get_provider_name()}")
                except Exception as e_gen:
                    print(f"Erro ao gerar resposta com {client_instance.get_provider_name()}: {type(e_gen).__name__} - {e_gen} (Isso pode ser esperado se a API Key não estiver configurada)")
            else:
                 print(f"Skipping generate_response test for HuggingFace in this basic loader test.")

        except LLMConfigurationError as e_conf:
            print(f"Erro de Configuração ao carregar cliente: {e_conf}")
        except Exception as e_other:
            print(f"Erro Inesperado durante o teste do loader: {type(e_other).__name__} - {e_other}")

    print("\n--- Testes do LLMLoader concluídos. Verifique os resultados e as API Keys no seu ambiente. ---")

