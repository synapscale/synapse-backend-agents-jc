"""Configuração para testes.

Este módulo contém configurações e fixtures compartilhadas para testes.
"""

import os
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.synapse.db import Base

# Configurar banco de dados em memória para testes
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Criar engine e sessão para testes
engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
)


@pytest.fixture(scope="session")
async def setup_test_db():
    """Configura banco de dados para testes."""
    # Criar tabelas
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    # Limpar tabelas
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db_session(setup_test_db):
    """Fornece sessão de banco de dados para testes."""
    async with TestingSessionLocal() as session:
        yield session
        # Rollback após cada teste para isolar transações
        await session.rollback()
