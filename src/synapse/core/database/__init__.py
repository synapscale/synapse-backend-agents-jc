"""
Async Database Configuration for Service Layer.

This module provides async database configuration for the service layer,
while maintaining compatibility with the existing synchronous database layer.
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import MetaData, text
import logging
from typing import AsyncGenerator

# Import from the centralized config
from synapse.core.config import settings

logger = logging.getLogger(__name__)

# Get database configuration
db_config = settings.get_database_config()

# Convert synchronous URL to async URL for PostgreSQL
sync_url = db_config["url"]
if sync_url.startswith("postgresql://"):
    ASYNC_DATABASE_URL = sync_url.replace("postgresql://", "postgresql+asyncpg://")
elif sync_url.startswith("postgresql+psycopg2://"):
    ASYNC_DATABASE_URL = sync_url.replace(
        "postgresql+psycopg2://", "postgresql+asyncpg://"
    )
else:
    ASYNC_DATABASE_URL = sync_url

DATABASE_SCHEMA = db_config["schema"]

if not ASYNC_DATABASE_URL:
    raise ValueError("ASYNC_DATABASE_URL could not be configured")

if not DATABASE_SCHEMA:
    raise ValueError("DATABASE_SCHEMA not found in centralized configuration")

# Create async engine
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    pool_size=db_config["pool_size"],
    max_overflow=db_config["max_overflow"],
    pool_timeout=db_config["pool_timeout"],
    pool_recycle=db_config["pool_recycle"],
    echo=db_config["echo"],
)

# Create async session maker
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)

# Create async base for models (if needed for service layer)
async_metadata = MetaData(schema=DATABASE_SCHEMA)
AsyncBase = declarative_base(metadata=async_metadata)


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting an async database session for the service layer.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_async_db() -> None:
    """
    Initialize async database connection for service layer.
    """
    try:
        async with async_engine.begin() as conn:
            await conn.execute(text(f"SET search_path TO {DATABASE_SCHEMA}"))
            result = await conn.execute(
                text(f"SELECT COUNT(*) FROM {DATABASE_SCHEMA}.users")
            )
            count = result.scalar()
            logger.info(
                f"✅ Async database connected to schema {DATABASE_SCHEMA} - {count} users found"
            )

        logger.info("✅ Async database connection established successfully")
    except Exception as e:
        logger.error(f"❌ Error connecting to async database: {e}")

        # Check if in development
        if settings.ENVIRONMENT == "development":
            logger.warning("⚠️ Continuing in development mode without async database")
        else:
            raise


async def async_health_check() -> bool:
    """
    Check async database connection health.
    """
    try:
        async with async_engine.begin() as conn:
            await conn.execute(text(f"SELECT 1 FROM {DATABASE_SCHEMA}.users LIMIT 1"))
        return True
    except Exception as e:
        logger.error(f"❌ Async health check failed: {e}")
        return False


def get_async_connection_info() -> dict:
    """
    Return async database connection information.
    """
    return {
        "async_database_url": ASYNC_DATABASE_URL,
        "database_schema": DATABASE_SCHEMA,
        "environment": settings.ENVIRONMENT,
        "pool_size": db_config["pool_size"],
        "max_overflow": db_config["max_overflow"],
        "pool_timeout": db_config["pool_timeout"],
        "pool_recycle": db_config["pool_recycle"],
        "echo": db_config["echo"],
    }
