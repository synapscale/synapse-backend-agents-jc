"""
Database configuration and session management.
"""

import os
import logging
from typing import AsyncGenerator
from sqlalchemy import MetaData, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base

logger = logging.getLogger(__name__)

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

# Convert sync URL to async for PostgreSQL
if DATABASE_URL and DATABASE_URL.startswith("postgresql://"):
    # Replace postgresql:// with postgresql+asyncpg:// and handle SSL mode
    ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
    # Replace sslmode=require with ssl=require for asyncpg
    ASYNC_DATABASE_URL = ASYNC_DATABASE_URL.replace("sslmode=require", "ssl=require")
else:
    ASYNC_DATABASE_URL = DATABASE_URL

# Database configuration
DATABASE_SCHEMA = os.getenv("DATABASE_SCHEMA", "synapscale_db")
DATABASE_POOL_SIZE = int(os.getenv("DATABASE_POOL_SIZE", "20"))
DATABASE_MAX_OVERFLOW = int(os.getenv("DATABASE_MAX_OVERFLOW", "30"))
DATABASE_ECHO = os.getenv("DATABASE_ECHO", "false").lower() == "true"

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

# Create base class for models
Base = declarative_base()

# Metadata for schema
metadata = MetaData(schema=DATABASE_SCHEMA)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get database session.
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
        logger.info("✅ Database connection closed")
    except Exception as e:
        logger.error(f"❌ Error closing database: {e}")


# Keep the old sync versions for backward compatibility
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# Sync engine for existing code
if DATABASE_URL:
    sync_engine = create_engine(
        DATABASE_URL,
        pool_size=DATABASE_POOL_SIZE,
        max_overflow=DATABASE_MAX_OVERFLOW,
        echo=DATABASE_ECHO,
        pool_pre_ping=True,
        pool_recycle=300,
    )
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

def get_db_sync() -> Session:
    """
    Get synchronous database session for backward compatibility.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Export main functions
__all__ = [
    "get_db",
    "init_db", 
    "close_db",
    "AsyncSessionLocal",
    "Base",
    "metadata",
    "async_engine",
    "get_db_sync",  # For backward compatibility
]
