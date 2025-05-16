"""
Gerador de Embeddings OpenAI
Arquivo: src/agents/main_agent/data_connectors/embeddings_openai.py

Este módulo fornece a classe `OpenAIEmbeddings` para gerar embeddings (vetores numéricos
representando o significado semântico do texto) usando os modelos da OpenAI.
Conforme especificado pelo usuário, ele é configurado para usar o modelo
`text-embedding-ada-002` por padrão, mas pode ser alterado via variáveis de ambiente.

Os embeddings são um componente fundamental para sistemas de RAG (Retrieval Augmented Generation),
pois permitem que o sistema encontre documentos ou trechos de texto semanticamente
similares a uma consulta do usuário.

Boas Práticas e Considerações AI-Friendly:
- **Escolha do Modelo de Embedding:** `text-embedding-ada-002` é um modelo eficiente e de alta
  qualidade da OpenAI, adequado para a maioria das tarefas de RAG. A flexibilidade para
  configurar o nome do modelo via variável de ambiente (`OPENAI_EMBEDDING_MODEL_NAME`)
  permite fácil atualização ou experimentação com outros modelos.
- **Tratamento de Newlines:** A OpenAI recomenda substituir caracteres de nova linha (`\n`)
  por espaços antes de gerar embeddings, pois isso pode melhorar a qualidade.
  (Referência: https://cookbook.openai.com/examples/embedding_new_lines)
- **Gerenciamento de API Key:** A chave da API OpenAI é um dado sensível e deve ser gerenciada
  de forma segura, idealmente através de variáveis de ambiente (`OPENAI_API_KEY`),
  conforme implementado aqui.
- **Tratamento de Erros:** A classe inclui tratamento básico de erros para falhas na chamada
  da API OpenAI, retornando `None` para embeddings individuais ou para itens em um lote
  que falharam. Em um sistema de produção, um logging mais robusto e estratégias de retry
  podem ser necessários.
- **Batching (Processamento em Lote):** Embora o exemplo de `get_embeddings` itere sobre os textos,
  para um grande número de textos, as APIs de embedding geralmente suportam processamento em lote
  para maior eficiência. A SDK atual da OpenAI (`openai >= 1.0`) lida com isso de forma transparente
  ao passar uma lista de textos para `client.embeddings.create(input=[text_list], ...)`.
  A implementação aqui foi simplificada para clareza, mas para produção, o batching direto
  com a SDK é preferível para listas grandes.
- **Referência Cruzada:** Esta classe é usada principalmente por `SupabaseVectorStore`
  (em `supabase_vector.py`) para gerar os embeddings que serão armazenados e consultados.
  Também pode ser usada para embutir a consulta do usuário antes de buscar similaridade no
  vector store.
"""
import os
from openai import OpenAI # SDK oficial da OpenAI (versão >= 1.0.0)
from typing import List, Optional

# Importar o logger configurado (se existir um central)
# from my_vertical_agent.src.utils.logger import get_logger
# logger = get_logger(__name__)

class OpenAIEmbeddings:
    """
    Gera embeddings vetoriais para textos usando a API da OpenAI.

    Esta classe encapsula a lógica para se conectar à API da OpenAI e obter
    representações vetoriais de textos, que são cruciais para tarefas de
    busca semântica e RAG.
    """
    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None
    ):
        """
        Inicializa o cliente OpenAIEmbeddings.

        Args:
            api_key (Optional[str]): Chave da API OpenAI. Se não fornecida, tenta carregar
                                     da variável de ambiente `OPENAI_API_KEY`.
            model_name (Optional[str]): Nome do modelo de embedding da OpenAI a ser usado.
                                        Se não fornecido, tenta carregar da variável de ambiente
                                        `OPENAI_EMBEDDING_MODEL_NAME` (padrão: "text-embedding-ada-002").

        Raises:
            ValueError: Se a chave da API OpenAI não for encontrada.
        """
        # Carrega a chave da API e o nome do modelo das variáveis de ambiente se não fornecidos.
        # Isso permite configuração flexível sem hardcoding de credenciais.
        _api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model_name = model_name or os.getenv("OPENAI_EMBEDDING_MODEL_NAME", "text-embedding-ada-002")
        
        if not _api_key:
            # logger.error("Chave da API OpenAI não encontrada. Defina a variável de ambiente OPENAI_API_KEY.")
            raise ValueError("Chave da API OpenAI não encontrada. Por favor, defina a variável de ambiente OPENAI_API_KEY.")
        
        # Inicializa o cliente da API OpenAI.
        # A partir da versão 1.0.0 da biblioteca `openai`, a inicialização é feita desta forma.
        try:
            self.client = OpenAI(api_key=_api_key)
            # logger.info(f"Cliente OpenAIEmbeddings inicializado com sucesso para o modelo: {self.model_name}")
            print(f"DEBUG: Cliente OpenAIEmbeddings inicializado para modelo: {self.model_name}")
        except Exception as e:
            # logger.error(f"Erro ao inicializar o cliente OpenAI: {e}", exc_info=True)
            raise ConnectionError(f"Falha ao inicializar o cliente OpenAI. Detalhes: {e}") from e

    def embed_query(self, text: str) -> List[float]:
        """
        Gera um embedding para um único texto de consulta (query).
        Este método é frequentemente usado para embutir a pergunta do usuário antes de
        compará-la com os vetores na base de conhecimento.

        Args:
            text (str): O texto a ser embutido.

        Returns:
            List[float]: O vetor de embedding gerado.

        Raises:
            Exception: Se ocorrer um erro durante a chamada da API OpenAI.
        """
        # logger.debug(f"Gerando embedding para consulta (query): {text[:100]}...")
        try:
            # OpenAI recomenda substituir newlines por espaços para melhor performance/qualidade.
            # Referência: https://cookbook.openai.com/examples/embedding_new_lines
            processed_text = text.replace("\n", " ")
            
            response = self.client.embeddings.create(input=[processed_text], model=self.model_name)
            embedding_vector = response.data[0].embedding
            # logger.debug(f"Embedding gerado com sucesso para consulta. Dimensões: {len(embedding_vector)}")
            return embedding_vector
        except Exception as e:
            # logger.error(f"Erro ao gerar embedding para o texto: {text[:50]}... Detalhes: {e}", exc_info=True)
            # Em um cenário de produção, pode-se querer tentar novamente ou ter um fallback.
            # Por enquanto, relançamos a exceção para que o chamador possa lidar com ela.
            raise Exception(f"Falha ao gerar embedding via OpenAI para o texto: {text[:50]}... Erro: {e}") from e

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Gera embeddings para uma lista de textos (documentos).
        Este método é tipicamente usado para embutir os documentos que serão armazenados
        na base de conhecimento vetorial.

        Args:
            texts (List[str]): Uma lista de textos a serem embutidos.

        Returns:
            List[List[float]]: Uma lista de vetores de embedding, onde cada vetor corresponde
                               a um texto na lista de entrada.
        
        Raises:
            Exception: Se ocorrer um erro durante a chamada da API OpenAI para qualquer um dos textos.
                       (Nota: a API `create` com múltiplos inputs retorna uma lista de embeddings,
                        então o erro pode ser mais geral ou específico a um item do lote).
        """
        # logger.debug(f"Gerando embeddings para {len(texts)} documentos...")
        if not texts:
            return []
        
        try:
            # Processa newlines em todos os textos.
            processed_texts = [text.replace("\n", " ") for text in texts]
            
            # A API `embeddings.create` pode receber uma lista de strings diretamente.
            response = self.client.embeddings.create(input=processed_texts, model=self.model_name)
            
            # Extrai os embeddings da resposta.
            # A resposta `response.data` é uma lista de objetos Embedding, cada um com um atributo `embedding`.
            embedding_vectors = [item.embedding for item in response.data]
            # logger.debug(f"Embeddings gerados com sucesso para {len(embedding_vectors)}/{len(texts)} documentos.")
            return embedding_vectors
        except Exception as e:
            # logger.error(f"Erro ao gerar embeddings para o lote de {len(texts)} textos. Detalhes: {e}", exc_info=True)
            # Para simplificar, relançamos. Em produção, pode-se tentar embutir individualmente
            # ou retornar resultados parciais com placeholders para os que falharam.
            raise Exception(f"Falha ao gerar embeddings via OpenAI para o lote de textos. Erro: {e}") from e

# Bloco de exemplo para teste direto do módulo (executado com `python embeddings_openai.py`)
if __name__ == "__main__":
    print("--- Testando OpenAIEmbeddings Diretamente ---")
    
    # Certifique-se de que as variáveis de ambiente OPENAI_API_KEY e (opcionalmente)
    # OPENAI_EMBEDDING_MODEL_NAME estão configuradas no seu ambiente, ou crie um arquivo .env
    # na raiz do projeto e use `python-dotenv` para carregá-lo.
    # Exemplo com python-dotenv (instale com `pip install python-dotenv`):
    # from dotenv import load_dotenv
    # import pathlib
    # env_path = pathlib.Path(__file__).parent.parent.parent.parent / ".env"
    # load_dotenv(dotenv_path=env_path)
    # print(f"OPENAI_API_KEY loaded: {"SET" if os.getenv("OPENAI_API_KEY") else "NOT SET"}")

    try:
        embedder = OpenAIEmbeddings()
        print(f"Usando modelo de embedding: {embedder.model_name}")

        # Teste com um único texto (consulta)
        single_text_query = "Qual é o futuro da Inteligência Artificial Generativa?"
        print(f"\nTestando embed_query com: {single_text_query}")
        embedding_query = embedder.embed_query(single_text_query)
        print(f"  Embedding (primeiros 5D de {len(embedding_query)}D): {embedding_query[:5]}...")
        assert len(embedding_query) > 0, "O embedding da consulta não deveria estar vazio."

        # Teste com uma lista de textos (documentos)
        document_texts = [
            "A IA Generativa está transformando a criação de conteúdo.",
            "Modelos de linguagem grandes (LLMs) são a base de muitas aplicações de IA Generativa.",
            "Considerações éticas são cruciais no desenvolvimento de IA."
        ]
        print(f"\nTestando embed_documents com {len(document_texts)} textos:")
        embeddings_docs = embedder.embed_documents(document_texts)
        for i, emb_doc in enumerate(embeddings_docs):
            print(f"  Doc {i+1} (primeiros 5D de {len(emb_doc)}D): {emb_doc[:5]}...")
            assert len(emb_doc) > 0, f"O embedding do documento {i+1} não deveria estar vazio."
        assert len(embeddings_docs) == len(document_texts), "Número incorreto de embeddings de documentos gerados."

        print("\n--- Teste de OpenAIEmbeddings concluído com sucesso! ---")

    except ValueError as ve:
        print(f"ERRO DE CONFIGURAÇÃO: {ve}")
        print("Por favor, verifique suas variáveis de ambiente (ex: OPENAI_API_KEY).")
    except ConnectionError as ce:
        print(f"ERRO DE CONEXÃO COM OPENAI: {ce}")
    except Exception as e:
        print(f"ERRO INESPERADO DURANTE O TESTE: {type(e).__name__} - {e}")
        import traceback
        traceback.print_exc()

