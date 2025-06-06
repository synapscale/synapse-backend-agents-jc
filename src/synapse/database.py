"""
Configuração do banco de dados com SQLAlchemy
Conexão direta com PostgreSQL
"""
from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import logging
import os

from src.synapse.config import settings

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Carregar variáveis de ambiente
DATABASE_URL = os.getenv("DATABASE_URL")
DATABASE_SCHEMA = os.getenv("DATABASE_SCHEMA", "synapscale_db")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")

# Criar engine do SQLAlchemy com o schema especificado
engine = create_engine(DATABASE_URL, pool_size=20, max_overflow=30, echo=settings.DATABASE_ECHO)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Criar base com o schema especificado
metadata = MetaData(schema=DATABASE_SCHEMA)
Base = declarative_base(metadata=metadata)

def get_db():
    """
    Dependency para obter uma sessão do banco de dados
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """
    Inicializa a conexão com o banco de dados
    """
    try:
        # Não vamos criar tabelas, pois elas já existem no schema
        # Base.metadata.create_all(bind=engine)
        with engine.connect() as conn:
            conn.execute(text(f"SET search_path TO {DATABASE_SCHEMA}"))
            result = conn.execute(text(f"SELECT COUNT(*) FROM {DATABASE_SCHEMA}.users"))
            count = result.scalar()
            logger.info(f"✅ Conectado ao schema {DATABASE_SCHEMA} - {count} usuários encontrados")
        logger.info(f"✅ Conexão com o banco de dados PostgreSQL estabelecida com sucesso")
    except Exception as e:
        logger.error(f"❌ Erro ao conectar ao banco de dados: {e}")
        raise

def health_check() -> bool:
    """
    Verifica a saúde da conexão com o banco
    """
    try:
        with engine.connect() as conn:
            conn.execute(text(f"SELECT 1 FROM {DATABASE_SCHEMA}.users LIMIT 1"))
        return True
    except Exception as e:
        logger.error(f"❌ Health check falhou: {e}")
        return False

def create_tables():
    """
    Criar todas as tabelas no banco de dados
    Nota: As tabelas já existem no schema, então esta função não faz nada
    """
    logger.warning(
        "⚠️  As tabelas já existem no schema, não é necessário criá-las"
    )

def drop_tables():
    """
    Remover todas as tabelas do banco de dados
    Nota: Esta função é perigosa e não deve ser usada em produção
    """
    logger.warning(
        "⚠️  Função de remoção de tabelas desativada para evitar perda de dados"
    )

