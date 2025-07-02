"""
Database configuration and session management.
"""

import os
import logging
from typing import AsyncGenerator, Optional, Dict, Any, Generator
from contextlib import contextmanager
from sqlalchemy import MetaData, text, create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

logger = logging.getLogger(__name__)


# ============================
# CONFIGURAÇÃO CENTRALIZADA
# ============================
def get_database_config() -> Dict[str, Any]:
    """
    Retorna configuração completa do banco de dados usando config centralizada
    """
    try:
        from synapse.core.config import settings

        return settings.get_database_config()
    except ImportError:
        # Fallback para variáveis de ambiente diretas
        return {
            "url": os.getenv("DATABASE_URL"),
            "schema": os.getenv("DATABASE_SCHEMA", "synapscale_db"),
            "pool_size": int(os.getenv("DATABASE_POOL_SIZE", "20")),
            "max_overflow": int(os.getenv("DATABASE_MAX_OVERFLOW", "30")),
            "echo": os.getenv("DATABASE_ECHO", "false").lower() == "true",
            "pool_timeout": 30,
            "pool_recycle": 300,
        }


# Get database configuration
db_config = get_database_config()
DATABASE_URL = db_config["url"]
DATABASE_SCHEMA = db_config["schema"]
DATABASE_POOL_SIZE = db_config["pool_size"]
DATABASE_MAX_OVERFLOW = db_config["max_overflow"]
DATABASE_ECHO = db_config["echo"]

# Convert sync URL to async for PostgreSQL
if DATABASE_URL and DATABASE_URL.startswith("postgresql://"):
    # Replace postgresql:// with postgresql+asyncpg:// and handle SSL mode
    ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
    # Replace sslmode=require with ssl=require for asyncpg
    ASYNC_DATABASE_URL = ASYNC_DATABASE_URL.replace("sslmode=require", "ssl=require")
else:
    ASYNC_DATABASE_URL = DATABASE_URL

# ============================
# ASYNC DATABASE SETUP
# ============================

# Create async engine
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    pool_size=DATABASE_POOL_SIZE,
    max_overflow=DATABASE_MAX_OVERFLOW,
    echo=DATABASE_ECHO,
    pool_pre_ping=True,
    pool_recycle=300,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=True,
    autocommit=False,
)

# ============================
# SYNC DATABASE SETUP
# ============================

# Sync engine for existing code and context managers
if DATABASE_URL:
    sync_engine = create_engine(
        DATABASE_URL,
        pool_size=DATABASE_POOL_SIZE,
        max_overflow=DATABASE_MAX_OVERFLOW,
        echo=DATABASE_ECHO,
        pool_pre_ping=True,
        pool_recycle=300,
        connect_args={
            "options": f"-csearch_path={DATABASE_SCHEMA},public",
        },
    )

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

# ============================
# BASE AND METADATA
# ============================

# Create base class for models
Base = declarative_base()

# Metadata for schema operations
schema_metadata = MetaData(schema=DATABASE_SCHEMA)

# ============================
# DATABASE DEPENDENCIES
# ============================


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get async database session.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()


# Backwards-compatible alias (explicit async session)
get_db_async = get_async_db

# ----------------------------
# SYNC DATABASE DEPENDENCY
# ----------------------------


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a synchronous `Session`. Use this for code that relies on the classic `.query()` API and synchronous commit/rollback operations."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Alias kept for legacy imports
get_db_sync = get_db

# ============================
# DATABASE OPERATIONS
# ============================


async def init_db() -> None:
    """
    Initialize database connection and create tables if needed.
    """
    try:
        async with async_engine.begin() as conn:
            # Test connection
            await conn.execute(text("SELECT 1"))
            logger.info(f"✅ Database connection successful to: {DATABASE_SCHEMA}")

            # Create schema if it doesn't exist
            await conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {DATABASE_SCHEMA}"))
            logger.info(f"✅ Schema '{DATABASE_SCHEMA}' ensured")

    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise


async def close_db() -> None:
    """
    Close database connection.
    """
    try:
        await async_engine.dispose()
        if "sync_engine" in globals():
            sync_engine.dispose()
        logger.info("✅ Database connections closed")
    except Exception as e:
        logger.error(f"❌ Error closing database: {e}")


def test_database_connection() -> bool:
    """
    Testa conexão com o banco de dados de forma síncrona.
    """
    try:
        with sync_engine.connect() as connection:
            # Testar conexão básica
            result = connection.execute(text("SELECT 1"))
            result.fetchone()

            # Verificar se schema existe
            schema_check = connection.execute(
                text(
                    """
                SELECT schema_name 
                FROM information_schema.schemata 
                WHERE schema_name = :schema
                """
                ),
                {"schema": DATABASE_SCHEMA},
            )

            if schema_check.fetchone():
                logger.info("✅ Database connection test successful")
                return True
            else:
                logger.error(f"❌ Schema '{DATABASE_SCHEMA}' not found")
                return False

    except Exception as e:
        logger.error(f"❌ Database connection test failed: {e}")
        return False


def get_database_info() -> Optional[Dict[str, Any]]:
    """
    Obtém informações detalhadas do banco de dados.
    """
    try:
        with sync_engine.connect() as connection:
            # Informações básicas
            version_result = connection.execute(text("SELECT version()"))
            version = version_result.fetchone()[0]

            # Contar tabelas no schema
            tables_result = connection.execute(
                text(
                    """
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = :schema
                """
                ),
                {"schema": DATABASE_SCHEMA},
            )
            table_count = tables_result.fetchone()[0]

            # Informações de conexão
            connection_info = connection.execute(
                text(
                    "SELECT current_database(), current_user, inet_server_addr(), inet_server_port()"
                ),
            )
            db_name, user, host, port = connection_info.fetchone()

            return {
                "version": version.split(" ")[0:2],  # PostgreSQL version
                "database": db_name,
                "user": user,
                "host": host,
                "port": port,
                "schema": DATABASE_SCHEMA,
                "table_count": table_count,
                "async_pool": {
                    "size": async_engine.pool.size(),
                    "checked_in": async_engine.pool.checkedin(),
                    "checked_out": async_engine.pool.checkedout(),
                },
                "sync_pool": {
                    "size": sync_engine.pool.size(),
                    "checked_in": sync_engine.pool.checkedin(),
                    "checked_out": sync_engine.pool.checkedout(),
                },
            }

    except Exception as e:
        logger.error(f"❌ Failed to get database info: {e}")
        return None


# ----------------------------
# CONTEXT MANAGER (SYNC)
# ----------------------------


@contextmanager
def get_db_session():
    """
    Context manager para sessão síncrona do banco de dados.
    Útil para scripts ou serviços que precisam de controle manual de transações.
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


# ============================
# EXPORTS
# ============================

# Export main functions
__all__ = [
    "get_async_db",  # Async dependency
    "get_db",  # Sync dependency
    "get_db_sync",  # Sync alias
    "get_db_session",  # Context manager
    "init_db",
    "close_db",
    "test_database_connection",
    "get_database_info",
    "AsyncSessionLocal",
    "SessionLocal",
    "Base",
    "schema_metadata",
    "async_engine",
    "sync_engine",
]
