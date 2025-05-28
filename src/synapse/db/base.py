"""Configuração do banco de dados.

Este módulo contém a configuração do banco de dados, incluindo
a engine, sessão e modelos base.
"""

import logging
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from synapse.config import settings

# Logger
logger = logging.getLogger(__name__)

# Criar engine assíncrona
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    future=True,
)

# Criar sessão assíncrona
async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Base para modelos declarativos
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependência para obter sessão de banco de dados.
    
    Yields:
        Sessão de banco de dados
    """
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db() -> None:
    """Inicializa o banco de dados.
    
    Esta função cria todas as tabelas definidas nos modelos.
    Em produção, deve-se usar migrações Alembic em vez desta função.
    """
    try:
        # Criar tabelas
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Banco de dados inicializado com sucesso")
    except Exception as e:
        logger.error(f"Erro ao inicializar banco de dados: {str(e)}")
        raise
