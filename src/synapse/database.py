"""
Configuração do banco de dados com SQLAlchemy
Conexão direta com PostgreSQL - SISTEMA COMPLETAMENTE CENTRALIZADO
"""
from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import logging
from typing import Generator

# Importar do sistema centralizado
from synapse.core.config_new import settings

# Usar logging centralizado
logger = logging.getLogger(__name__)

# Obter configuração COMPLETA do banco do sistema centralizado
db_config = settings.get_database_config()

DATABASE_URL = db_config["url"]
DATABASE_SCHEMA = db_config["schema"]

# Validação usando settings centralizados
if not DATABASE_URL:
    raise ValueError("DATABASE_URL não encontrada nas configurações centralizadas")

if not DATABASE_SCHEMA:
    raise ValueError("DATABASE_SCHEMA não encontrada nas configurações centralizadas")

# Engine usando configuração centralizada
engine = create_engine(
    DATABASE_URL,
    pool_size=db_config["pool_size"],
    max_overflow=db_config["max_overflow"],
    pool_timeout=db_config["pool_timeout"],
    pool_recycle=db_config["pool_recycle"],
    echo=db_config["echo"]
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

metadata = MetaData(schema=DATABASE_SCHEMA)
Base = declarative_base(metadata=metadata)

def get_db() -> Generator:
    """
    Dependency para obter uma sessão do banco de dados
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db() -> None:
    """
    Inicializa a conexão com o banco de dados usando configurações centralizadas
    """
    try:
        Base.metadata.create_all(bind=engine)

        with engine.connect() as conn:
            conn.execute(text(f"SET search_path TO {DATABASE_SCHEMA}"))
            result = conn.execute(
                text(f"SELECT COUNT(*) FROM {DATABASE_SCHEMA}.users")
            )
            count = result.scalar()
            logger.info(
                f"✅ Conectado ao schema {DATABASE_SCHEMA} - {count} usuários encontrados"
            )

        logger.info("✅ Conexão com o banco de dados estabelecida com sucesso")
    except ValueError as ve:
        logger.error(f"❌ Erro de valor ao conectar ao banco de dados: {ve}")
        raise
    except Exception as e:
        logger.error(f"❌ Erro ao conectar ao banco de dados: {e}")
        
        # Verificar se está em desenvolvimento usando settings centralizados
        if settings.ENVIRONMENT == "development":
            logger.warning(
                "⚠️ Continuando em modo desenvolvimento sem banco de dados"
            )
        else:
            raise

def health_check() -> bool:
    """
    Verifica a saúde da conexão com o banco usando configurações centralizadas
    """
    try:
        with engine.connect() as conn:
            conn.execute(text(f"SELECT 1 FROM {DATABASE_SCHEMA}.users LIMIT 1"))
        return True
    except Exception as e:
        logger.error(f"❌ Health check falhou: {e}")
        return False

def create_tables() -> None:
    """
    Criar todas as tabelas no banco de dados
    Controlado por configuração centralizada
    """
    # Verificar se deve criar tabelas baseado na configuração
    if hasattr(settings, 'AUTO_CREATE_TABLES') and settings.AUTO_CREATE_TABLES:
        try:
            Base.metadata.create_all(bind=engine)
            logger.info("✅ Tabelas criadas com sucesso")
        except Exception as e:
            logger.error(f"❌ Erro ao criar tabelas: {e}")
            raise
    else:
        logger.info("⚠️ Criação automática de tabelas desabilitada nas configurações")

def drop_tables() -> None:
    """
    Remover todas as tabelas do banco de dados
    Controlado por configuração centralizada de segurança
    """
    # Verificar se está em desenvolvimento E se drop está habilitado
    if (settings.ENVIRONMENT == "development" and 
        hasattr(settings, 'ALLOW_DROP_TABLES') and 
        settings.ALLOW_DROP_TABLES):
        try:
            Base.metadata.drop_all(bind=engine)
            logger.warning("⚠️ Tabelas removidas com sucesso (DESENVOLVIMENTO)")
        except Exception as e:
            logger.error(f"❌ Erro ao remover tabelas: {e}")
            raise
    else:
        logger.error(
            "❌ Remoção de tabelas bloqueada pelas configurações de segurança"
        )
        raise ValueError(
            "Drop tables não permitido em produção ou configuração não habilitada"
        )

def get_connection_info() -> dict:
    """
    Retorna informações da conexão usando configurações centralizadas
    """
    return {
        "database_url": DATABASE_URL,
        "database_schema": DATABASE_SCHEMA,
        "environment": settings.ENVIRONMENT,
        "pool_size": db_config["pool_size"],
        "max_overflow": db_config["max_overflow"],
        "pool_timeout": db_config["pool_timeout"],
        "pool_recycle": db_config["pool_recycle"],
        "echo": db_config["echo"]
    }

def test_connection() -> bool:
    """
    Testa a conexão com o banco usando configurações centralizadas
    """
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.scalar()
        logger.info("✅ Teste de conexão bem-sucedido")
        return True
    except Exception as e:
        logger.error(f"❌ Teste de conexão falhou: {e}")
        return False
