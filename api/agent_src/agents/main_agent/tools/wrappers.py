"""
Wrappers (Invólucros) de Ferramentas para o Agente Principal
Arquivo: src/agents/main_agent/tools/wrappers.py

Este módulo contém funções Python que atuam como "wrappers" (invólucros) para:
1. Chamar subagentes especializados.
2. Executar outras ferramentas definidas em `tools.yaml` (ex: busca na base de conhecimento).

Esses wrappers são a ponte entre a decisão do LLM do agente principal de usar uma ferramenta
e a execução real dessa ferramenta ou subagente. Eles abstraem a complexidade da chamada
e podem incluir lógica adicional como formatação de input/output, tratamento de erros específico
da ferramenta, etc.

Boas Práticas e Considerações AI-Friendly:
- Abstração: Wrappers simplificam a lógica do agente principal, que só precisa saber qual
  wrapper chamar com quais argumentos, sem se preocupar com os detalhes internos da ferramenta.
- Modularidade: Novas ferramentas ou subagentes podem ser integrados adicionando um novo wrapper
  e uma entrada em `tools.yaml`, sem modificar extensivamente o código do agente principal.
- Tratamento de Erros Específico: Cada wrapper pode ter seu próprio tratamento de erros,
  fornecendo feedback mais útil ao agente principal ou ao usuário.
- Logging Detalhado: Wrappers são um bom lugar para adicionar logging específico sobre o uso
  de ferramentas, inputs, outputs e quaisquer problemas encontrados.
- Clareza para o LLM: Embora o LLM interaja com as *descrições* das ferramentas em `tools.yaml`,
  a existência de wrappers bem definidos no backend torna o sistema mais robusto e manutenível.
"""
import os
import json
import importlib # Para carregamento dinâmico de módulos de subagentes
from typing import Dict, Any, Callable

# Importar o SupabaseVectorStore e OpenAIEmbeddings para a ferramenta de RAG
# O caminho pode precisar de ajuste dependendo da estrutura final do PYTHONPATH
from my_vertical_agent.src.agents.main_agent.data_connectors.supabase_vector import SupabaseVectorStore
from my_vertical_agent.src.agents.main_agent.data_connectors.embeddings_openai import OpenAIEmbeddings

# Importar o logger configurado (se existir um central)
# from my_vertical_agent.src.utils.logger import get_logger
# logger = get_logger(__name__)

def call_sub_agent(sub_agent_id: str, task_input: Dict[str, Any], main_agent_config: Dict[str, Any], session_id: str) -> str:
    """
    Wrapper genérico e dinâmico para instanciar e chamar um subagente especificado.

    Esta função tenta carregar dinamicamente o módulo e a classe do subagente
    com base no `sub_agent_id`, instancia-o e executa seu método `run()`.

    Args:
        sub_agent_id (str): O ID do subagente a ser chamado (ex: "sub_agent_1").
                              Este ID deve corresponder ao nome da pasta do subagente
                              em `src/agents/sub_agents/`.
        task_input (Dict[str, Any]): O dicionário de input para o subagente,
                                     que deve estar em conformidade com o `schema.yaml` do subagente.
        main_agent_config (Dict[str, Any]): A configuração do agente principal, que pode conter
                                            caminhos ou outras informações úteis para os subagentes.
        session_id (str): O ID da sessão atual, para ser passado ao subagente se ele precisar
                          de memória de chat ou contexto de sessão.

    Returns:
        str: A resposta do subagente como uma string (geralmente JSON ou texto formatado),
             ou uma mensagem de erro se a chamada falhar.
    """
    # logger.info(f"[Wrapper] Tentando chamar Subagente: {sub_agent_id} com input: {json.dumps(task_input)[:200]}...")
    print(f"DEBUG: [Wrapper] Chamando Subagente: {sub_agent_id} com input: {task_input}")

    try:
        # Constrói o caminho do módulo e o nome da classe dinamicamente.
        # Ex: sub_agent_id = "sub_agent_1" -> module = "...sub_agent_1.agent", class = "SubAgent1"
        module_path = f"my_vertical_agent.src.agents.sub_agents.{sub_agent_id}.agent"
        
        # Converte "sub_agent_1" para "SubAgent1"
        class_name_parts = [part.capitalize() for part in sub_agent_id.split("_")]
        class_name = "".join(class_name_parts)
        # logger.debug(f"[Wrapper] Carregando módulo {module_path} e classe {class_name} para subagente {sub_agent_id}")

        sub_agent_module = importlib.import_module(module_path)
        SubAgentClass = getattr(sub_agent_module, class_name)
        
        # Instancia o subagente. Assumimos que o construtor do subagente pode aceitar
        # `session_id` e `config_path` (ou ter padrões).
        # O `config_path` pode ser construído ou vir do `main_agent_config`.
        sub_agent_config_path = os.path.join("src", "agents", "sub_agents", sub_agent_id, "config.yaml")
        
        # logger.debug(f"[Wrapper] Instanciando {class_name} com session_id={session_id} e config_path={sub_agent_config_path}")
        sub_agent_instance = SubAgentClass(session_id=session_id, config_path=sub_agent_config_path)
        
        # Executa o método `run` do subagente com o input fornecido.
        # O método `run` do subagente deve retornar uma string (ex: JSON ou texto).
        response = sub_agent_instance.run(task_input)
        # logger.info(f"[Wrapper] Subagente {sub_agent_id} retornou: {str(response)[:200]}...")
        print(f"DEBUG: [Wrapper] Subagente {sub_agent_id} retornou: {response}")
        return str(response) # Garante que a resposta seja uma string

    except ModuleNotFoundError as e:
        error_msg = f"Erro Crítico: Módulo do subagente {sub_agent_id} não encontrado em {module_path}. Detalhes: {e}"
        # logger.error(error_msg, exc_info=True)
        print(f"ERRO: {error_msg}")
        return json.dumps({"error": "sub_agent_module_not_found", "details": error_msg})
    except AttributeError as e:
        error_msg = f"Erro Crítico: Classe {class_name} do subagente {sub_agent_id} não encontrada no módulo {module_path}. Detalhes: {e}"
        # logger.error(error_msg, exc_info=True)
        print(f"ERRO: {error_msg}")
        return json.dumps({"error": "sub_agent_class_not_found", "details": error_msg})
    except Exception as e:
        error_msg = f"Erro inesperado ao chamar o subagente {sub_agent_id}. Detalhes: {type(e).__name__} - {e}"
        # logger.error(error_msg, exc_info=True)
        print(f"ERRO: {error_msg}")
        import traceback
        traceback.print_exc() # Para depuração mais detalhada no console
        return json.dumps({"error": "sub_agent_call_failed", "details": error_msg})

def search_supabase_knowledge_base(query: str, vector_store_instance: Optional[SupabaseVectorStore] = None) -> str:
    """
    Wrapper para realizar uma busca na base de conhecimento vetorial (Supabase).

    Esta função encapsula a lógica de interação com a instância `SupabaseVectorStore`.

    Args:
        query (str): A string de consulta para a busca na base de conhecimento.
        vector_store_instance (Optional[SupabaseVectorStore]): Uma instância já inicializada
            de `SupabaseVectorStore`. Se não fornecida, tentará inicializar uma.

    Returns:
        str: Uma string JSON contendo os resultados da busca (lista de documentos encontrados)
             ou uma mensagem de erro em formato JSON.
    """
    # logger.info(f"[Wrapper] Realizando busca na KB com query: {query[:100]}...")
    print(f"DEBUG: [Wrapper] Buscando na KB: {query}")

    if not vector_store_instance:
        # logger.info("[Wrapper] Instância de SupabaseVectorStore não fornecida, tentando inicializar uma nova.")
        print("DEBUG: [Wrapper] Instância de SupabaseVectorStore não fornecida, inicializando...")
        try:
            # Carrega configurações do Supabase e OpenAI Embeddings das variáveis de ambiente
            # (conforme .env.example)
            supabase_url = os.getenv("SUPABASE_URL")
            supabase_key = os.getenv("SUPABASE_ANON_KEY") # Ou SERVICE_KEY se necessário para a tabela
            embedding_model_name = os.getenv("OPENAI_EMBEDDING_MODEL_NAME", "text-embedding-ada-002")
            openai_api_key = os.getenv("OPENAI_API_KEY")
            
            table_name = os.getenv("SUPABASE_KB_TABLE_NAME", "documents")
            vector_column = os.getenv("SUPABASE_KB_VECTOR_COLUMN", "embedding")
            content_column = os.getenv("SUPABASE_KB_CONTENT_COLUMN", "content")
            metadata_column = os.getenv("SUPABASE_KB_METADATA_COLUMN", "metadata")
            similarity_threshold = float(os.getenv("SUPABASE_KB_SIMILARITY_THRESHOLD", "0.75"))
            match_count = int(os.getenv("SUPABASE_KB_MATCH_COUNT", "5"))

            if not all([supabase_url, supabase_key, openai_api_key]):
                error_msg = "Variáveis de ambiente para Supabase ou OpenAI API Key não configuradas."
                # logger.error(f"[Wrapper] {error_msg}")
                print(f"ERRO: {error_msg}")
                return json.dumps({"error": "config_missing_rag", "details": error_msg})

            embeddings = OpenAIEmbeddings(api_key=openai_api_key, model_name=embedding_model_name)
            vector_store_instance = SupabaseVectorStore(
                supabase_url=supabase_url,
                supabase_key=supabase_key,
                embedding_function=embeddings.embed_query, # Passa a função de embedding
                table_name=table_name,
                vector_column_name=vector_column,
                content_column_name=content_column,
                metadata_column_name=metadata_column,
                similarity_threshold=similarity_threshold,
                match_count=match_count
            )
            # logger.info("[Wrapper] Nova instância de SupabaseVectorStore inicializada com sucesso.")
            print("DEBUG: [Wrapper] Nova instância de SupabaseVectorStore inicializada.")
        except Exception as e:
            error_msg = f"Falha ao inicializar SupabaseVectorStore no wrapper: {type(e).__name__} - {e}"
            # logger.error(f"[Wrapper] {error_msg}", exc_info=True)
            print(f"ERRO: {error_msg}")
            return json.dumps({"error": "rag_initialization_failed", "details": error_msg})

    try:
        # Realiza a busca por similaridade.
        # O método `similarity_search` deve retornar uma lista de dicionários (documentos).
        results = vector_store_instance.similarity_search(query_text=query)
        
        if results:
            # Formata os resultados para serem consumidos pelo LLM (ex: string JSON).
            # Incluir metadados pode ser útil para o LLM citar fontes ou entender melhor o contexto.
            formatted_results = json.dumps(results, indent=2, ensure_ascii=False)
            # logger.info(f"[Wrapper] Busca na KB bem-sucedida. Encontrados {len(results)} resultados.")
            print(f"DEBUG: [Wrapper] Busca na KB encontrou {len(results)} resultados.")
            return formatted_results
        else:
            # logger.info("[Wrapper] Busca na KB não retornou resultados.")
            print("DEBUG: [Wrapper] Busca na KB não retornou resultados.")
            return json.dumps({"message": "Nenhuma informação relevante encontrada na base de conhecimento para sua consulta.", "results": []})
    except Exception as e:
        error_msg = f"Erro durante a busca na base de conhecimento: {type(e).__name__} - {e}"
        # logger.error(f"[Wrapper] {error_msg}", exc_info=True)
        print(f"ERRO: {error_msg}")
        return json.dumps({"error": "rag_search_failed", "details": error_msg})

# Mapeamento de nomes de ferramentas (de tools.yaml) para suas funções wrapper.
# A lógica em `agent.py` usará este mapeamento para despachar as chamadas de ferramentas.
# As chaves aqui devem corresponder aos `name` das ferramentas em `tools.yaml`.
# As funções lambda garantem que os argumentos corretos sejam passados para os wrappers.
# `kwargs` é usado para passar instâncias (como `vector_store`) ou `session_id` que o wrapper pode precisar.
TOOL_WRAPPERS: Dict[str, Callable[..., str]] = {
    "roteador_sub_agente_analise_dados": 
        lambda task_input, main_config, **kwargs: call_sub_agent("sub_agent_1", task_input, main_config, kwargs.get("session_id", "default_session")),
    "roteador_sub_agente_busca_especializada": 
        lambda task_input, main_config, **kwargs: call_sub_agent("sub_agent_2", task_input, main_config, kwargs.get("session_id", "default_session")),
    "roteador_sub_agente_interacao_api_externa": 
        lambda task_input, main_config, **kwargs: call_sub_agent("sub_agent_3", task_input, main_config, kwargs.get("session_id", "default_session")),
    "roteador_sub_agente_geracao_conteudo_criativo": 
        lambda task_input, main_config, **kwargs: call_sub_agent("sub_agent_4", task_input, main_config, kwargs.get("session_id", "default_session")),
    "roteador_sub_agente_perfil_usuario_preferencias": 
        lambda task_input, main_config, **kwargs: call_sub_agent("sub_agent_5", task_input, main_config, kwargs.get("session_id", "default_session")),
    
    "search_knowledge_base_rag": 
        lambda task_input, main_config, **kwargs: search_supabase_knowledge_base(task_input.get("query", ""), kwargs.get("vector_store_instance"))
}

# Bloco de exemplo para teste direto do módulo (executado com `python wrappers.py`)
if __name__ == "__main__":
    print("--- Testando Wrappers de Ferramentas (Subagentes Mockados e RAG) ---")

    # Carregar variáveis de ambiente (necessário para Supabase/OpenAI se não mockado)
    # from dotenv import load_dotenv
    # load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", "..", "..", "config", ".env"))
    # print(f"OPENAI_API_KEY loaded: {"SET" if os.getenv("OPENAI_API_KEY") else "NOT SET"}")
    # print(f"SUPABASE_URL loaded: {"SET" if os.getenv("SUPABASE_URL") else "NOT SET"}")

    mock_main_agent_config = {"description": "Configuração de teste do agente principal"}
    test_session_id = "test_wrapper_session_001"

    # --- Teste de chamada a subagente (mockado pela lógica em call_sub_agent) ---
    print("\n--- Testando call_sub_agent (mockado internamente) ---")
    sub_agent_input_data = {
        "query": "Resuma o relatório de vendas do último trimestre.",
        "main_agent_instruction": "Preciso de um resumo conciso para a diretoria."
    }
    # Para este teste, call_sub_agent tentará importar dinamicamente. 
    # Se os subagentes não estiverem completamente implementados ou o PYTHONPATH não estiver correto,
    # ele pode falhar ou retornar um erro JSON.
    # Para um teste mais controlado do wrapper em si, a lógica de `call_sub_agent` precisaria
    # de um mock mais explícito da instância do subagente.
    response_sa1 = TOOL_WRAPPERS["roteador_sub_agente_analise_dados"](
        task_input=sub_agent_input_data, 
        main_config=mock_main_agent_config, 
        session_id=test_session_id
    )
    print(f"Resposta do roteador_sub_agente_analise_dados: {response_sa1}")

    # --- Teste da busca na base de conhecimento (RAG) ---
    print("\n--- Testando search_supabase_knowledge_base (pode fazer chamada real se .env configurado) ---")
    kb_query_input = {"query": "O que é Engenharia de Prompt?"}
    
    # Para testar sem uma instância de SupabaseVectorStore real, você pode mocká-la:
    # class MockVectorStore:
    #     def similarity_search(self, query_text):
    #         print(f"MockVectorStore: Buscando por {query_text}")
    #         if "Engenharia de Prompt" in query_text:
    #             return [{"content": "Engenharia de Prompt é a arte de criar prompts eficazes para LLMs.", "metadata": {"source": "doc_A.pdf"}}]
    #         return []
    # mock_vs_instance = MockVectorStore()
    # response_kb = TOOL_WRAPPERS["search_knowledge_base_rag"](kb_query_input, mock_main_agent_config, vector_store_instance=mock_vs_instance)

    # Teste tentando inicializar o SupabaseVectorStore (requer .env configurado)
    response_kb = TOOL_WRAPPERS["search_knowledge_base_rag"](
        task_input=kb_query_input, 
        main_config=mock_main_agent_config, 
        vector_store_instance=None # Força a inicialização interna
    )
    print(f"Resposta do search_knowledge_base_rag (pode ser erro se .env não configurado):\n{response_kb}")

    kb_query_no_results = {"query": "asdfghjklqwertyuiop"} # Query que provavelmente não terá resultados
    response_kb_no = TOOL_WRAPPERS["search_knowledge_base_rag"](
        task_input=kb_query_no_results, 
        main_config=mock_main_agent_config, 
        vector_store_instance=None
    )
    print(f"Resposta do search_knowledge_base_rag (sem resultados esperados):\n{response_kb_no}")

    print("\n--- Testes dos Wrappers Concluídos (Verifique os outputs e erros) ---")

