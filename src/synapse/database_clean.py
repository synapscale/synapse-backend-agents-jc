"""
Configuração do banco de dados SQLAlchemy para PostgreSQL
"""
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import logging

from src.synapse.config import settings

logger = logging.getLogger(__name__)

# Configuração SQLAlchemy
engine = None
SessionLocal = None
Base = declarative_base()


def get_database_url() -> str:
    """Obtém a URL do banco de dados configurada"""
    return settings.DATABASE_URL


async def connect_database():
    """Conecta ao banco de dados PostgreSQL via SQLAlchemy"""
    global engine, SessionLocal

    try:
        database_url = get_database_url()

        # Criar engine com configurações otimizadas
        engine = create_engine(
            database_url,
            echo=settings.DEBUG,
            pool_size=settings.DATABASE_POOL_SIZE,
            max_overflow=settings.DATABASE_MAX_OVERFLOW,
            pool_pre_ping=True,
            pool_recycle=300
        )

        # Criar SessionLocal
        SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=engine
        )

        # Testar conexão
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1 as test"))
            test_value = result.scalar()

        logger.info("✅ Conectado ao banco PostgreSQL via SQLAlchemy")
        logger.info(f"✅ Teste de conexão bem-sucedido: {test_value}")

        return engine
    except Exception as e:
        logger.error(f"❌ Erro ao conectar ao banco de dados: {e}")
        logger.error(f"DATABASE_URL: {database_url[:50]}...")
        raise


async def disconnect_database():
    """Desconecta do banco de dados"""
    global engine

    if engine:
        try:
            engine.dispose()
            logger.info("✅ Desconectado do banco de dados")
        except Exception as e:
            logger.error(f"❌ Erro ao desconectar do banco de dados: {e}")


def get_db_session() -> Session:
    """Retorna uma sessão do banco de dados SQLAlchemy"""
    global SessionLocal

    if not SessionLocal:
        error = "Database not connected. Call connect_database() first."
        raise Exception(error)

    return SessionLocal()


# Dependency para FastAPI (SQLAlchemy)
def get_db() -> Generator[Session, None, None]:
    """Dependency para obter sessão do banco de dados SQLAlchemy"""
    db = get_db_session()
    try:
        yield db
    finally:
        db.close()


async def health_check() -> bool:
    """Verifica a saúde da conexão com o banco"""
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1 as health_check"))
            return result.scalar() == 1
    except Exception as e:
        logger.error(f"❌ Health check falhou: {e}")
        return False


def create_tables():
    """Criar todas as tabelas no banco de dados usando SQLAlchemy"""
    global engine

    if not engine:
        error = "Database not connected. Call connect_database() first."
        raise Exception(error)

    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Tabelas criadas com sucesso")
    except Exception as e:
        logger.error(f"❌ Erro ao criar tabelas: {e}")
        raise


def drop_tables():
    """Remover todas as tabelas do banco de dados usando SQLAlchemy"""
    global engine

    if not engine:
        error = "Database not connected. Call connect_database() first."
        raise Exception(error)

    try:
        Base.metadata.drop_all(bind=engine)
        logger.info("✅ Tabelas removidas com sucesso")
    except Exception as e:
        logger.error(f"❌ Erro ao remover tabelas: {e}")
        raise
