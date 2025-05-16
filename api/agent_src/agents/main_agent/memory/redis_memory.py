"""
Implementação da Memória de Chat usando Redis.

Este módulo fornece a classe `RedisChatMemory` para interagir com um servidor Redis,
permitindo o armazenamento e a recuperação do histórico de mensagens de chat.
Isso é essencial para manter a continuidade e o contexto em conversas longas
com o agente de IA.

A configuração da conexão com o Redis (host, porta, senha, etc.) é lida a partir
de variáveis de ambiente, conforme definido em `config/.env.example` e referenciado
pelo arquivo de configuração `src/agents/main_agent/memory/config.yaml`.

Boas Práticas e Considerações AI-Friendly:
- **Persistência de Contexto:** Manter o histórico da conversa permite que o agente
  "lembre" de interações anteriores, resultando em diálogos mais coerentes e relevantes.
- **Gerenciamento de Janela de Contexto:** A capacidade de limitar o número de mensagens
  recuperadas (`limit` no método `get_history`) é crucial para não exceder a janela
  de contexto do LLM, o que poderia levar a erros ou perda de informação relevante.
- **Eficiência:** Redis, sendo um banco de dados em memória, oferece alta performance para
  as operações de leitura e escrita frequentes exigidas pela memória de chat.
- **TTL (Time-To-Live):** Definir um TTL para as chaves de sessão ajuda a gerenciar o uso
  de memória no Redis, expirando automaticamente sessões inativas.
- **Estrutura de Mensagem:** As mensagens são armazenadas como dicionários JSON, permitindo
  flexibilidade para incluir metadados (ex: "role", "content", "timestamp").
"""
import redis
import os
import json
from typing import List, Dict, Any, Optional

# Importar o logger configurado para o projeto, se disponível, para consistência.
# from my_vertical_agent.src.utils.logger import get_logger # Supondo que exista um logger central
# logger = get_logger(__name__)

class RedisChatMemory:
    """
    Gerencia o histórico de chat de uma sessão específica usando o Redis como backend.

    Cada sessão de chat é armazenada como uma lista no Redis, onde cada elemento da lista
    é uma string JSON representando uma única mensagem.
    """
    def __init__(
        self,
        session_id: str,
        host: Optional[str] = None,  # Permite override em tempo de execução, se necessário
        port: Optional[int] = None,
        password: Optional[str] = None,
        db: Optional[int] = None,
        session_prefix: Optional[str] = None,
        ttl_seconds: Optional[int] = None
    ):
        """
        Inicializa a instância do RedisChatMemory e estabelece a conexão com o Redis.

        Os parâmetros de conexão, se não fornecidos diretamente, são obtidos de variáveis
        de ambiente. Os nomes dessas variáveis são definidos em
        `src/agents/main_agent/memory/config.yaml` (ex: `host_env_var: "REDIS_HOST"`).

        Args:
            session_id (str): O identificador único para a sessão de chat.
                              Este ID será usado para construir a chave no Redis.
            host (Optional[str]): Hostname ou IP do servidor Redis. 
                                  Padrão: valor da variável de ambiente definida em `config.yaml` (ex: REDIS_HOST).
            port (Optional[int]): Porta do servidor Redis.
                                  Padrão: valor da variável de ambiente definida em `config.yaml` (ex: REDIS_PORT).
            password (Optional[str]): Senha para autenticação no Redis.
                                      Padrão: valor da variável de ambiente definida em `config.yaml` (ex: REDIS_PASSWORD).
            db (Optional[int]): Número do banco de dados Redis a ser usado (0-15).
                                Padrão: valor da variável de ambiente definida em `config.yaml` (ex: REDIS_DB).
            session_prefix (Optional[str]): Prefixo para as chaves de sessão no Redis.
                                            Padrão: valor da variável de ambiente definida em `config.yaml` (ex: REDIS_SESSION_PREFIX).
            ttl_seconds (Optional[int]): Tempo de vida (TTL) para as chaves de sessão, em segundos.
                                         Padrão: valor da variável de ambiente definida em `config.yaml` (ex: REDIS_SESSION_TTL_SECONDS).

        Raises:
            ConnectionError: Se a conexão com o Redis falhar.
        """
        self.session_id = session_id
        
        # Carrega os nomes das variáveis de ambiente do arquivo de configuração (idealmente)
        # Para simplificar este exemplo, vamos assumir que os nomes das env vars são fixos ou passados.
        # Em um sistema completo, você carregaria memory/config.yaml aqui para obter os `_env_var` nomes.
        _host = host or os.getenv("REDIS_HOST", "localhost")
        _port = port or int(os.getenv("REDIS_PORT", "6379"))
        _password = password or os.getenv("REDIS_PASSWORD") # Retorna None se não definida, o que é ok para redis-py
        _db = db or int(os.getenv("REDIS_DB", "0"))
        
        self.session_prefix = session_prefix or os.getenv("REDIS_SESSION_PREFIX", "vertical_agent_chat_session_")
        self.ttl_seconds = ttl_seconds or int(os.getenv("REDIS_SESSION_TTL_SECONDS", "7200")) # Padrão 2 horas
        
        # Constrói a chave completa no Redis para esta sessão específica.
        self.redis_key = f"{self.session_prefix}{self.session_id}"

        try:
            # Inicializa o cliente Redis.
            # `decode_responses=True` garante que os dados lidos do Redis sejam strings Python (UTF-8),
            # não bytes, o que simplifica o manuseio de JSON.
            self.client = redis.Redis(
                host=_host,
                port=_port,
                password=_password,
                db=_db,
                charset="utf-8",
                decode_responses=True # Importante para não ter que decodificar bytes manualmente
            )
            # Verifica a conexão enviando um comando PING.
            self.client.ping()
            # logger.info(f"Conexão com Redis estabelecida com sucesso para sessão {self.session_id} em {_host}:{_port}")
            print(f"DEBUG: Conexão com Redis estabelecida para {self.redis_key}") # Temporário para depuração
        except redis.exceptions.ConnectionError as e:
            # logger.error(f"Falha ao conectar com Redis em {_host}:{_port} para sessão {self.session_id}: {e}", exc_info=True)
            print(f"ERRO: Falha ao conectar com Redis: {e}") # Temporário para depuração
            raise ConnectionError(f"Falha ao conectar com o servidor Redis em {_host}:{_port}. Detalhes: {e}") from e
        except Exception as e: # Captura outras exceções potenciais na inicialização do Redis
            # logger.error(f"Erro inesperado ao inicializar cliente Redis para sessão {self.session_id}: {e}", exc_info=True)
            print(f"ERRO: Erro inesperado ao inicializar Redis: {e}") # Temporário para depuração
            raise ConnectionError(f"Erro inesperado durante a inicialização do cliente Redis. Detalhes: {e}") from e

    def add_message(self, message: Dict[str, Any]) -> None:
        """
        Adiciona uma nova mensagem ao histórico de chat da sessão atual.

        As mensagens são serializadas para JSON e adicionadas ao início de uma lista Redis
        (usando LPUSH). Isso significa que as mensagens mais recentes ficam no topo da lista Redis.
        O TTL da chave da sessão é atualizado a cada nova mensagem para manter a sessão ativa.

        Args:
            message (Dict[str, Any]): Um dicionário representando a mensagem.
                                     Exemplo: `{"role": "user", "content": "Olá, mundo!"}`
                                     Espera-se que contenha pelo menos "role" e "content".
        """
        if not self.client:
            # logger.error(f"Cliente Redis não inicializado para sessão {self.session_id}. Não foi possível adicionar mensagem.")
            print(f"ERRO: Cliente Redis não inicializado para {self.redis_key}")
            # Considerar levantar uma exceção aqui se o cliente DEVE estar sempre disponível.
            return
        
        try:
            message_json = json.dumps(message) # Serializa a mensagem para uma string JSON.
            self.client.lpush(self.redis_key, message_json) # Adiciona ao início da lista.
            self.client.expire(self.redis_key, self.ttl_seconds) # Atualiza o TTL da chave da sessão.
            # logger.debug(f"Mensagem adicionada à sessão {self.session_id}: {message_json}")
        except redis.exceptions.RedisError as e:
            # logger.error(f"Erro ao adicionar mensagem à sessão {self.session_id} no Redis: {e}", exc_info=True)
            print(f"ERRO: Erro Redis ao adicionar mensagem para {self.redis_key}: {e}")
            # Decidir como lidar com o erro: logar, levantar exceção, etc.
        except json.JSONEncodeError as e:
            # logger.error(f"Erro ao serializar mensagem para JSON para sessão {self.session_id}: {message} - {e}", exc_info=True)
            print(f"ERRO: Erro JSON ao adicionar mensagem para {self.redis_key}: {e}")
            # Mensagem não pôde ser serializada, não tentar adicionar ao Redis.

    def get_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Recupera as últimas N mensagens do histórico de chat para a sessão atual.

        As mensagens são recuperadas do Redis e desserializadas de JSON.
        A ordem retornada é cronológica (a mensagem mais antiga primeiro), que é o formato
        tipicamente esperado pelos LLMs para o histórico de contexto.

        Args:
            limit (int): O número máximo de mensagens a serem recuperadas. 
                         Padrão é 10 (5 trocas de mensagens usuário/assistente).

        Returns:
            List[Dict[str, Any]]: Uma lista de dicionários de mensagens, ordenada cronologicamente
                                  (mais antiga primeiro). Retorna lista vazia em caso de erro
                                  ou se não houver histórico.
        """
        if not self.client:
            # logger.error(f"Cliente Redis não inicializado para sessão {self.session_id}. Não foi possível obter histórico.")
            print(f"ERRO: Cliente Redis não inicializado para {self.redis_key}")
            return []

        try:
            # LRANGE 0 (início) a limit-1 recupera as `limit` mensagens mais recentes (pois LPUSH adiciona à esquerda).
            messages_json_reversed = self.client.lrange(self.redis_key, 0, limit - 1)
            
            messages: List[Dict[str, Any]] = []
            for msg_json in messages_json_reversed:
                try:
                    messages.append(json.loads(msg_json)) # Desserializa cada mensagem.
                except json.JSONDecodeError as e:
                    # logger.warning(f"Erro ao desserializar mensagem da sessão {self.session_id} do Redis: {msg_json} - {e}")
                    print(f"AVISO: Erro JSON ao ler histórico de {self.redis_key}: {e}")
                    # Decide se continua ou para; aqui, optamos por pular a mensagem corrompida.
                    continue 
            
            # A lista `messages` está agora com as mais recentes primeiro.
            # Inverte para ter a ordem cronológica (mais antigas primeiro) para o LLM.
            # logger.debug(f"Histórico recuperado para sessão {self.session_id} (antes de inverter, {len(messages)} mensagens): {messages}")
            return messages[::-1] 
        except redis.exceptions.RedisError as e:
            # logger.error(f"Erro ao obter histórico da sessão {self.session_id} do Redis: {e}", exc_info=True)
            print(f"ERRO: Erro Redis ao obter histórico para {self.redis_key}: {e}")
            return []

    def clear_history(self) -> None:
        """
        Remove (deleta) todo o histórico de chat para a sessão atual do Redis.
        """
        if not self.client:
            # logger.error(f"Cliente Redis não inicializado para sessão {self.session_id}. Não foi possível limpar histórico.")
            print(f"ERRO: Cliente Redis não inicializado para {self.redis_key}")
            return
        
        try:
            self.client.delete(self.redis_key)
            # logger.info(f"Histórico da sessão {self.session_id} (chave: {self.redis_key}) limpo do Redis.")
        except redis.exceptions.RedisError as e:
            # logger.error(f"Erro ao limpar histórico da sessão {self.session_id} do Redis: {e}", exc_info=True)
            print(f"ERRO: Erro Redis ao limpar histórico para {self.redis_key}: {e}")

# Bloco de exemplo para teste direto do módulo (executado com `python redis_memory.py`)
if __name__ == "__main__":
    print("--- Testando RedisChatMemory Diretamente ---")
    
    # Para este teste funcionar, seu servidor Redis deve estar rodando e acessível,
    # e as variáveis de ambiente (REDIS_HOST, REDIS_PORT, etc.) devem estar configuradas
    # ou os valores padrão (localhost:6379) devem ser válidos.
    # Você pode criar um arquivo .env na raiz do projeto e usar `python-dotenv` para carregá-lo
    # ou definir as variáveis de ambiente no seu terminal antes de executar.
    # Exemplo com python-dotenv (instale com `pip install python-dotenv`):
    # from dotenv import load_dotenv
    # load_dotenv()

    test_session_id = "test_direct_redis_memory_001"
    print(f"ID da Sessão de Teste: {test_session_id}")

    try:
        # Instancia a memória para a sessão de teste.
        memory_instance = RedisChatMemory(session_id=test_session_id)
        print("Instância de RedisChatMemory criada.")

        # 1. Limpa qualquer histórico anterior desta sessão de teste (para um teste limpo)
        print(f"Limpando histórico anterior (se existir) para {test_session_id}...")
        memory_instance.clear_history()
        initial_history = memory_instance.get_history()
        print(f"Histórico inicial para {test_session_id}: {initial_history} (Esperado: [])")
        assert initial_history == [], "O histórico inicial não estava vazio após a limpeza."

        # 2. Adiciona algumas mensagens
        print("Adicionando mensagens de teste...")
        messages_to_add = [
            {"role": "user", "content": "Olá Agente!"},
            {"role": "assistant", "content": "Olá Usuário! Como posso te ajudar hoje?"},
            {"role": "user", "content": "Poderia me falar sobre a tecnologia Redis?"},
            {"role": "assistant", "content": "Claro! Redis é um repositório de estrutura de dados em memória, usado como banco de dados, cache e message broker."}
        ]
        for msg in messages_to_add:
            memory_instance.add_message(msg)
        print(f"{len(messages_to_add)} mensagens adicionadas.")

        # 3. Recupera o histórico
        retrieved_history_limit_default = memory_instance.get_history() # Pega com limite padrão (10)
        print(f"Histórico recuperado (limite padrão, {len(retrieved_history_limit_default)} mensagens, mais antigas primeiro):")
        for i, msg in enumerate(retrieved_history_limit_default):
            print(f"  {i+1}. {msg}")
        assert len(retrieved_history_limit_default) == len(messages_to_add), "Número incorreto de mensagens recuperadas (padrão)."
        assert retrieved_history_limit_default == messages_to_add, "Conteúdo do histórico recuperado (padrão) não corresponde ao adicionado."

        retrieved_history_limit_2 = memory_instance.get_history(limit=2)
        print(f"Histórico recuperado (limite 2, {len(retrieved_history_limit_2)} mensagens, mais antigas primeiro):")
        for i, msg in enumerate(retrieved_history_limit_2):
            print(f"  {i+1}. {msg}")
        assert len(retrieved_history_limit_2) == 2, "Número incorreto de mensagens recuperadas (limite 2)."
        # Espera-se que sejam as duas últimas mensagens adicionadas, mas em ordem cronológica.
        assert retrieved_history_limit_2 == messages_to_add[-2:], "Conteúdo do histórico recuperado (limite 2) não corresponde."
        
        # 4. Verifica o TTL (requer verificação manual no Redis ou espera e nova consulta)
        print(f"A chave da sessão '{memory_instance.redis_key}' no Redis deve ter um TTL de aproximadamente {memory_instance.ttl_seconds} segundos.")
        # ttl_check = memory_instance.client.ttl(memory_instance.redis_key)
        # print(f"TTL atual da chave (via redis-py): {ttl_check} (pode ser -1 se não houver TTL, -2 se não existir)")

        # 5. Limpa o histórico novamente
        print(f"Limpando histórico para {test_session_id}...")
        memory_instance.clear_history()
        final_history = memory_instance.get_history()
        print(f"Histórico final para {test_session_id}: {final_history} (Esperado: [])")
        assert final_history == [], "O histórico final não estava vazio após a limpeza."

        print("--- Teste de RedisChatMemory concluído com sucesso! ---")

    except ConnectionError as ce:
        print(f"ERRO DE CONEXÃO NO TESTE: {ce}")
        print("Por favor, verifique se o Redis está rodando e as variáveis de ambiente estão corretas.")
    except AssertionError as ae:
        print(f"FALHA NA ASSERÇÃO DO TESTE: {ae}")
    except Exception as e:
        print(f"ERRO INESPERADO DURANTE O TESTE: {e}")
        import traceback
        traceback.print_exc()

