"""
Conector para Supabase como Vector Store (Armazenamento Vetorial)
Arquivo: src/agents/main_agent/data_connectors/supabase_vector.py

Este módulo fornece a classe `SupabaseVectorStore` para interagir com o Supabase
como um armazenamento vetorial para aplicações de RAG (Retrieval Augmented Generation).
Ele utiliza a classe `OpenAIEmbeddings` (de `embeddings_openai.py`) para gerar
os embeddings e a biblioteca `supabase-py` para comunicação com o Supabase.

A configuração é lida a partir de variáveis de ambiente, conforme definido em
`config/.env.example`.

Boas Práticas e Considerações AI-Friendly:
- **Separação de Responsabilidades:** Esta classe foca exclusivamente na interação com o
  Supabase como vector store. A geração de embeddings é delegada à classe `OpenAIEmbeddings`,
  promovendo modularidade.
- **Configuração Flexível via Variáveis de Ambiente:** Permite que URLs, chaves de API,
  nomes de tabelas e colunas sejam configurados externamente, facilitando a adaptação
  a diferentes ambientes (desenvolvimento, produção) e instâncias do Supabase.
- **Segurança de Chaves:** A distinção entre chave anônima (`SUPABASE_ANON_KEY`) para leitura
  e chave de serviço (`SUPABASE_SERVICE_KEY`) para escrita é importante. A classe tenta
  usar a chave anônima por padrão, mas permite a sobrescrita com a chave de serviço
  para operações de escrita (`add_documents`), o que é crucial se o Row Level Security (RLS)
  estiver ativo e restringir escritas anônimas.
- **Funções RPC no Supabase para Busca Vetorial:** A busca por similaridade é realizada
  chamando uma função RPC (Remote Procedure Call) no Supabase (ex: `match_documents`).
  Isso é uma prática recomendada pelo Supabase, pois permite que a lógica de busca vetorial
  (usando extensões como `pgvector`) seja otimizada no lado do banco de dados.
  O template inclui um exemplo de como criar tal função SQL.
  (Referência: https://supabase.com/docs/guides/ai/vector-embeddings#sql-functions)
- **Tratamento de Erros:** A classe inclui tratamento básico para erros de conexão,
  falhas na geração de embeddings e erros durante operações de escrita ou busca no Supabase.
  Em produção, um logging mais detalhado e estratégias de retry podem ser adicionados.
- **Metadados:** A capacidade de armazenar e recuperar metadados junto com o conteúdo textual
  e os vetores é crucial para RAG. Os metadados podem incluir fontes, categorias, datas,
  etc., que podem ser usados para filtrar resultados ou fornecer contexto adicional ao LLM.
- **Referência Cruzada:**
    - Utiliza `OpenAIEmbeddings` de `embeddings_openai.py` para gerar os vetores.
    - É invocado pelo wrapper `search_supabase_knowledge_base` em `tools/wrappers.py`,
      que por sua vez é mapeado para a ferramenta `search_knowledge_base_rag` em `tools/tools.yaml`.
    - O agente principal (`main_agent/agent.py`) orquestra o uso desta ferramenta para RAG.
"""
import os
import supabase # Biblioteca oficial supabase-py
from typing import List, Dict, Any, Optional, Tuple, Callable

# Import relativo para OpenAIEmbeddings dentro do mesmo pacote de conectores
from .embeddings_openai import OpenAIEmbeddings

# Importar o logger configurado (se existir um central)
# from my_vertical_agent.src.utils.logger import get_logger
# logger = get_logger(__name__)

class SupabaseVectorStore:
    """
    Gerencia um armazenamento vetorial no Supabase para aplicações de RAG.

    Esta classe encapsula a lógica para:
    1. Conectar-se a uma instância do Supabase.
    2. Gerar embeddings para documentos usando um `embedding_generator` (padrão: OpenAIEmbeddings).
    3. Adicionar documentos (texto, metadados, embedding) a uma tabela no Supabase.
    4. Realizar buscas por similaridade vetorial usando uma função RPC no Supabase.
    """
    def __init__(
        self,
        supabase_url: Optional[str] = None,
        supabase_key: Optional[str] = None, # Chave anônima (anon key) por padrão
        embedding_function: Optional[Callable[[str], List[float]]] = None, # Função para gerar embeddings de consulta
        embedding_documents_function: Optional[Callable[[List[str]], List[List[float]]]] = None, # Função para gerar embeddings de documentos
        table_name: Optional[str] = None,
        vector_column_name: Optional[str] = None,
        content_column_name: Optional[str] = None,
        metadata_column_name: Optional[str] = None,
        similarity_threshold: Optional[float] = None, # Limiar padrão para busca
        match_count: Optional[int] = None # Contagem padrão de resultados para busca
    ):
        """
        Inicializa a instância do SupabaseVectorStore.

        Args:
            supabase_url (Optional[str]): URL do projeto Supabase. Carrega de `SUPABASE_URL` se None.
            supabase_key (Optional[str]): Chave API do Supabase (anônima ou de serviço).
                                          Carrega de `SUPABASE_ANON_KEY` se None.
            embedding_function (Optional[Callable[[str], List[float]]]): Função para gerar embedding de uma consulta.
                                                                      Se None, usa `OpenAIEmbeddings().embed_query`.
            embedding_documents_function (Optional[Callable[[List[str]], List[List[float]]]]): Função para gerar embeddings de múltiplos documentos.
                                                                                             Se None, usa `OpenAIEmbeddings().embed_documents`.
            table_name (Optional[str]): Nome da tabela no Supabase. Carrega de `SUPABASE_KB_TABLE_NAME` se None.
            vector_column_name (Optional[str]): Nome da coluna de vetores. Carrega de `SUPABASE_KB_VECTOR_COLUMN` se None.
            content_column_name (Optional[str]): Nome da coluna de conteúdo textual. Carrega de `SUPABASE_KB_CONTENT_COLUMN` se None.
            metadata_column_name (Optional[str]): Nome da coluna de metadados (JSONB). Carrega de `SUPABASE_KB_METADATA_COLUMN` se None.
            similarity_threshold (Optional[float]): Limiar de similaridade padrão para buscas. Carrega de `SUPABASE_KB_SIMILARITY_THRESHOLD` se None.
            match_count (Optional[int]): Número padrão de resultados para buscas. Carrega de `SUPABASE_KB_MATCH_COUNT` se None.

        Raises:
            ValueError: Se a URL ou a chave do Supabase não forem encontradas.
            ConnectionError: Se a conexão com o Supabase falhar.
        """
        _url = supabase_url or os.getenv("SUPABASE_URL")
        _key = supabase_key or os.getenv("SUPABASE_ANON_KEY") # Usar chave anônima por padrão para o cliente principal
        
        if not _url or not _key:
            # logger.error("URL ou Chave do Supabase não encontradas. Defina SUPABASE_URL e SUPABASE_ANON_KEY.")
            raise ValueError("URL ou Chave do Supabase não encontradas. Por favor, defina as variáveis de ambiente SUPABASE_URL e SUPABASE_ANON_KEY.")

        try:
            self.client: supabase.Client = supabase.create_client(_url, _key)
            # logger.info(f"Conectado com sucesso ao Supabase em {_url}")
            print(f"DEBUG: Conectado ao Supabase em {_url}")
        except Exception as e:
            # logger.error(f"Erro ao conectar ao Supabase: {e}", exc_info=True)
            raise ConnectionError(f"Falha ao conectar ao Supabase. Detalhes: {e}") from e

        if embedding_function is None or embedding_documents_function is None:
            # logger.info("Função de embedding não fornecida, inicializando OpenAIEmbeddings padrão.")
            print("DEBUG: Inicializando OpenAIEmbeddings padrão para SupabaseVectorStore.")
            default_embedder = OpenAIEmbeddings()
            self._embed_query = embedding_function or default_embedder.embed_query
            self._embed_documents = embedding_documents_function or default_embedder.embed_documents
        else:
            self._embed_query = embedding_function
            self._embed_documents = embedding_documents_function
            
        self.table_name = table_name or os.getenv("SUPABASE_KB_TABLE_NAME", "documents")
        self.vector_column_name = vector_column_name or os.getenv("SUPABASE_KB_VECTOR_COLUMN", "embedding")
        self.content_column_name = content_column_name or os.getenv("SUPABASE_KB_CONTENT_COLUMN", "content")
        self.metadata_column_name = metadata_column_name or os.getenv("SUPABASE_KB_METADATA_COLUMN", "metadata")
        
        self.default_similarity_threshold = similarity_threshold or float(os.getenv("SUPABASE_KB_SIMILARITY_THRESHOLD", "0.75"))
        self.default_match_count = match_count or int(os.getenv("SUPABASE_KB_MATCH_COUNT", "5"))
        
        # logger.info(f"SupabaseVectorStore inicializado para tabela {self.table_name}.")
        print(f"DEBUG: SupabaseVectorStore inicializado para tabela {self.table_name}.")

    def add_documents(
        self, 
        documents: List[Tuple[str, Dict[str, Any]]], 
        service_key_override: Optional[str] = None 
    ) -> bool:
        """
        Adiciona documentos (conteúdo textual e metadados) à tabela do Supabase após gerar seus embeddings.
        Requer uma chave de serviço (`SUPABASE_SERVICE_KEY`) para operações de escrita se o RLS
        estiver configurado para restringir inserções pela chave anônima.

        Args:
            documents (List[Tuple[str, Dict[str, Any]]]): Uma lista de tuplas, onde cada tupla contém
                (texto_do_documento, dicionario_de_metadados).
            service_key_override (Optional[str]): Chave de serviço do Supabase para usar nesta operação específica.
                                                  Se não fornecida, tenta usar `SUPABASE_SERVICE_KEY` do ambiente.

        Returns:
            bool: True se os documentos foram adicionados com sucesso, False caso contrário.
        """
        # logger.info(f"Tentando adicionar {len(documents)} documentos à tabela {self.table_name}.")
        _write_client = self.client # Usa o cliente inicializado (com anon key) por padrão
        
        _service_key = service_key_override or os.getenv("SUPABASE_SERVICE_KEY")
        if _service_key:
            # logger.info("Usando chave de serviço para operação de escrita.")
            print("DEBUG: Usando chave de serviço para add_documents.")
            try:
                _write_client = supabase.create_client(os.getenv("SUPABASE_URL"), _service_key)
            except Exception as e:
                # logger.error(f"Falha ao criar cliente Supabase com chave de serviço: {e}", exc_info=True)
                print(f"ERRO: Falha ao criar cliente Supabase com chave de serviço: {e}")
                return False
        else:
            # logger.warning("Chave de serviço (SUPABASE_SERVICE_KEY) não fornecida. A adição de documentos pode falhar se o RLS estiver ativo.")
            print("AVISO: Chave de serviço não fornecida. A adição de documentos pode falhar devido ao RLS.")

        texts_to_embed = [doc[0] for doc in documents]
        if not texts_to_embed:
            # logger.info("Nenhum texto fornecido para embutir e adicionar.")
            return True # Considera sucesso se não há nada a fazer
            
        try:
            embeddings = self._embed_documents(texts_to_embed)
        except Exception as e:
            # logger.error(f"Falha ao gerar embeddings para os documentos: {e}", exc_info=True)
            print(f"ERRO: Falha ao gerar embeddings: {e}")
            return False

        records_to_insert = []
        for i, (text, metadata) in enumerate(documents):
            if embeddings[i] is not None:
                records_to_insert.append({
                    self.content_column_name: text,
                    self.metadata_column_name: metadata,
                    self.vector_column_name: embeddings[i]
                })
            else:
                # logger.warning(f"Skipping document devido à falha na geração do embedding: {text[:50]}...")
                print(f"AVISO: Pulando documento (falha no embedding): {text[:50]}...")
        
        if not records_to_insert:
            # logger.info("Nenhum registro válido para inserir após a geração dos embeddings.")
            print("INFO: Nenhum registro válido para inserir.")
            return False

        try:
            # logger.debug(f"Inserindo {len(records_to_insert)} registros na tabela {self.table_name}.")
            response = _write_client.table(self.table_name).insert(records_to_insert).execute()
            
            # supabase-py v2+ retorna APIResponse. Em caso de sucesso em insert, response.data é uma lista dos dados inseridos.
            if response.data and not getattr(response, "error", None): 
                # logger.info(f"Adicionados {len(response.data)} documentos com sucesso ao Supabase.")
                print(f"DEBUG: Adicionados {len(response.data)} documentos com sucesso.")
                return True
            else:
                error_details = getattr(response, "error", "Erro desconhecido durante a inserção.")
                # logger.error(f"Erro ao adicionar documentos ao Supabase: {error_details}")
                print(f"ERRO: Ao adicionar documentos ao Supabase: {error_details}")
                return False

        except Exception as e:
            # logger.error(f"Exceção ao adicionar documentos ao Supabase: {e}", exc_info=True)
            print(f"EXCEÇÃO: Ao adicionar documentos ao Supabase: {e}")
            return False

    def similarity_search(
        self,
        query_text: str,
        match_count: Optional[int] = None,
        similarity_threshold: Optional[float] = None,
        rpc_function_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Realiza uma busca por similaridade na tabela do Supabase usando uma função RPC vetorial.
        É crucial que uma função RPC compatível (ex: `match_documents` ou `ivfflat_hnsw_match_documents`)
        esteja criada no seu esquema SQL do Supabase.
        Veja a documentação do Supabase AI para exemplos: 
        https://supabase.com/docs/guides/ai/vector-embeddings#sql-functions

        Args:
            query_text (str): O texto da consulta para a busca por similaridade.
            match_count (Optional[int]): Número de documentos similares a retornar.
                                         Usa `self.default_match_count` se None.
            similarity_threshold (Optional[float]): Limiar mínimo de similaridade para os resultados.
                                                    Usa `self.default_similarity_threshold` se None.
            rpc_function_name (Optional[str]): Nome da função RPC no Supabase para busca vetorial.
                                               Carrega de `SUPABASE_RPC_MATCH_FUNCTION` se None (padrão: "match_documents").

        Returns:
            List[Dict[str, Any]]: Uma lista de dicionários, onde cada dicionário representa um
                                  documento similar encontrado (incluindo conteúdo, metadados e score de similaridade).
                                  Retorna lista vazia em caso de erro ou se nada for encontrado.
        """
        # logger.debug(f"Realizando busca por similaridade para: {query_text[:100]}...")
        try:
            query_embedding = self._embed_query(query_text)
        except Exception as e:
            # logger.error(f"Falha ao gerar embedding para a consulta {query_text[:50]}...: {e}", exc_info=True)
            print(f"ERRO: Falha ao gerar embedding para consulta: {e}")
            return []

        _match_count = match_count if match_count is not None else self.default_match_count
        _similarity_threshold = similarity_threshold if similarity_threshold is not None else self.default_similarity_threshold
        _rpc_fn_name = rpc_function_name or os.getenv("SUPABASE_RPC_MATCH_FUNCTION", "match_documents")
        
        # Parâmetros para a chamada da função RPC no Supabase.
        # Estes nomes de parâmetros (`query_embedding`, `match_threshold`, `match_count`)
        # devem corresponder exatamente aos nomes dos argumentos da sua função SQL no Supabase.
        rpc_params = {
            'query_embedding': query_embedding,       # O vetor da consulta
            'match_threshold': _similarity_threshold, # O limiar de similaridade
            'match_count': _match_count             # O número de resultados a retornar
        }
        # logger.debug(f"Chamando função RPC {_rpc_fn_name} com parâmetros: {rpc_params}")
        print(f"DEBUG: Chamando RPC {_rpc_fn_name} com limiar={_similarity_threshold}, contagem={_match_count}")

        try:
            response = self.client.rpc(_rpc_fn_name, rpc_params).execute()
            
            if response.data and not getattr(response, "error", None):
                # logger.info(f"Busca por similaridade retornou {len(response.data)} resultados.")
                print(f"DEBUG: Busca RPC retornou {len(response.data)} resultados.")
                # A função RPC deve retornar campos como: id, content, metadata, similarity
                return response.data 
            elif getattr(response, "error", None):
                error_details = getattr(response, "error")
                # logger.error(f"Erro na chamada RPC {_rpc_fn_name} para busca por similaridade: {error_details}")
                print(f"ERRO: Na chamada RPC {_rpc_fn_name}: {error_details}")
                return []
            else:
                # logger.info("Nenhum documento similar encontrado ou erro não especificado na RPC.")
                print("INFO: Nenhum documento similar encontrado via RPC.")
                return []
        except Exception as e:
            # logger.error(f"Exceção durante a busca por similaridade via RPC {_rpc_fn_name}: {e}", exc_info=True)
            print(f"EXCEÇÃO: Durante busca RPC {_rpc_fn_name}: {e}")
            return []

# Bloco de exemplo para teste direto do módulo (executado com `python supabase_vector.py`)
if __name__ == "__main__":
    print("--- Testando SupabaseVectorStore Diretamente ---")

    # Para este teste funcionar, você PRECISA ter:
    # 1. Variáveis de ambiente configuradas em um arquivo .env na raiz do projeto ou no seu sistema:
    #    SUPABASE_URL, SUPABASE_ANON_KEY, OPENAI_API_KEY
    #    Opcional para escrita: SUPABASE_SERVICE_KEY
    #    Opcionais para configuração da tabela/RPC: SUPABASE_KB_TABLE_NAME, SUPABASE_KB_VECTOR_COLUMN, etc.
    #    SUPABASE_RPC_MATCH_FUNCTION (se diferente de "match_documents")
    # 2. Uma instância do Supabase com a extensão pgvector habilitada.
    # 3. Uma tabela criada (ex: "documents") com colunas para conteúdo, metadados e o vetor de embedding.
    #    Exemplo de DDL para a tabela (ajuste os nomes e o tamanho do vetor conforme necessário):
    #    CREATE TABLE documents (
    #      id BIGSERIAL PRIMARY KEY,
    #      content TEXT,
    #      metadata JSONB,
    #      embedding VECTOR(1536) -- Para text-embedding-ada-002 da OpenAI
    #    );
    # 4. Uma função RPC criada no Supabase para busca por similaridade. Exemplo (para similaridade de cosseno):
    #    CREATE OR REPLACE FUNCTION match_documents (
    #      query_embedding VECTOR(1536),
    #      match_threshold FLOAT,
    #      match_count INT
    #    )
    #    RETURNS TABLE (id BIGINT, content TEXT, metadata JSONB, similarity FLOAT)
    #    LANGUAGE plpgsql
    #    AS $$
    #    BEGIN
    #      RETURN QUERY
    #      SELECT
    #        docs.id,
    #        docs.content,
    #        docs.metadata,
    #        1 - (docs.embedding <=> query_embedding) AS similarity -- Cosseno: 1 - distância
    #      FROM documents AS docs
    #      WHERE 1 - (docs.embedding <=> query_embedding) > match_threshold
    #      ORDER BY docs.embedding <=> query_embedding ASC -- ASC para distância (mais próximo primeiro)
    #      LIMIT match_count;
    #    END;
    #    $$;
    #
    # Carregar .env (se estiver usando python-dotenv e o .env estiver na raiz do projeto)
    # from dotenv import load_dotenv
    # import pathlib
    # env_path = pathlib.Path(__file__).resolve().parent.parent.parent.parent / ".env"
    # if env_path.exists():
    #     load_dotenv(dotenv_path=env_path)
    #     print(f".env carregado de: {env_path}")
    # else:
    #     print(f"Arquivo .env não encontrado em: {env_path}. Certifique-se de que as variáveis de ambiente estão definidas.")

    try:
        print("Inicializando SupabaseVectorStore...")
        vector_store = SupabaseVectorStore()
        print(f"Usando tabela Supabase: {vector_store.table_name}, função RPC: {os.getenv("SUPABASE_RPC_MATCH_FUNCTION", "match_documents")}")

        # --- Teste de Adição de Documentos (Opcional - Requer SUPABASE_SERVICE_KEY) ---
        # Descomente para testar. CUIDADO: Isso irá escrever na sua tabela Supabase.
        # print("\n--- Testando Adição de Documentos (Requer SUPABASE_SERVICE_KEY) ---")
        # service_key_for_test = os.getenv("SUPABASE_SERVICE_KEY")
        # if service_key_for_test:
        #     docs_to_add_test = [
        #         ("O céu é azul durante o dia.", {"source": "observacao_diurna", "tags": ["natureza", "cor"]}),
        #         ("A grama geralmente é verde.", {"source": "jardim_botanico", "tags": ["natureza", "cor", "plantas"]}),
        #         ("Supabase facilita o desenvolvimento backend.", {"source": "documentacao_supabase", "tags": ["tecnologia", "backend", "supabase"]})
        #     ]
        #     print(f"Adicionando {len(docs_to_add_test)} documentos...")
        #     added_successfully = vector_store.add_documents(docs_to_add_test, service_key_override=service_key_for_test)
        #     if added_successfully:
        #         print("Documentos adicionados com sucesso!")
        #     else:
        #         print("Falha ao adicionar documentos. Verifique os logs e a configuração do Supabase.")
        # else:
        #     print("SUPABASE_SERVICE_KEY não configurada. Pulando teste de adição de documentos.")

        # --- Teste de Busca por Similaridade ---
        print("\n--- Testando Busca por Similaridade ---")
        query_example = "Qual a cor do céu?"
        print(f"Buscando por: {query_example}")
        search_results = vector_store.similarity_search(query_text=query_example, match_count=2, similarity_threshold=0.5)
        
        if search_results:
            print(f"Encontrados {len(search_results)} documentos similares para a consulta:")
            for i, doc in enumerate(search_results):
                print(f"  Resultado {i+1}:")
                print(f"    ID: {doc.get('id', 'N/A')}")
                # Ajuste os nomes das colunas se sua função RPC retornar nomes diferentes
                print(f"    Conteúdo: {doc.get(vector_store.content_column_name, doc.get('content', 'N/A'))[:100]}...") 
                print(f"    Metadados: {doc.get(vector_store.metadata_column_name, doc.get('metadata', {}))}")
                print(f"    Similaridade: {doc.get('similarity', 'N/A')}")
        else:
            print(f"Nenhum documento encontrado para a consulta: {query_example}.")
            print("Dicas: Verifique se há dados na sua tabela, se a função RPC está correta e se o limiar de similaridade é adequado.")

        print("\n--- Teste de SupabaseVectorStore concluído. Verifique os resultados. ---")

    except ValueError as ve:
        print(f"ERRO DE CONFIGURAÇÃO: {ve}")
        print("Por favor, verifique suas variáveis de ambiente (ex: SUPABASE_URL, SUPABASE_ANON_KEY, OPENAI_API_KEY).")
    except ConnectionError as ce:
        print(f"ERRO DE CONEXÃO COM SUPABASE: {ce}")
    except Exception as e:
        print(f"ERRO INESPERADO DURANTE O TESTE: {type(e).__name__} - {e}")
        import traceback
        traceback.print_exc()

