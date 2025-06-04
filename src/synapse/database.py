"""
Configuração do banco de dados com Prisma
Migrado de SQLAlchemy para PostgreSQL/Prisma
"""
from prisma import Prisma
from typing import Optional, AsyncGenerator
import asyncio
import logging

from src.synapse.config import settings

logger = logging.getLogger(__name__)

# Instância global do Prisma Client
prisma: Optional[Prisma] = None


async def connect_database():
    """Conecta ao banco de dados PostgreSQL via Prisma"""
    global prisma
    
    try:
        prisma = Prisma()
        await prisma.connect()
        logger.info("✅ Conectado ao banco de dados PostgreSQL via Prisma")
        return prisma
    except Exception as e:
        logger.error(f"❌ Erro ao conectar ao banco de dados: {e}")
        raise


async def disconnect_database():
    """Desconecta do banco de dados"""
    global prisma
    
    if prisma:
        try:
            await prisma.disconnect()
            logger.info("✅ Desconectado do banco de dados")
        except Exception as e:
            logger.error(f"❌ Erro ao desconectar do banco de dados: {e}")


async def get_database() -> Prisma:
    """Retorna a instância do Prisma Client"""
    global prisma
    
    if not prisma:
        await connect_database()
    
    return prisma


# Dependency para FastAPI (compatibilidade com SQLAlchemy)
async def get_db() -> Prisma:
    """Dependency para obter instância do banco de dados"""
    return await get_database()


# Dependency para FastAPI (Prisma)
async def get_prisma() -> Prisma:
    """Dependency para obter instância do Prisma Client"""
    return await get_database()


# Funções de compatibilidade com SQLAlchemy (para migração gradual)
def create_tables():
    """
    Criar todas as tabelas no banco de dados
    Nota: Com Prisma, use 'npx prisma db push' ou 'npx prisma migrate dev'
    """
    logger.warning("⚠️  Use 'npx prisma db push' para criar tabelas com Prisma")


def drop_tables():
    """
    Remover todas as tabelas do banco de dados
    Nota: Com Prisma, use 'npx prisma migrate reset'
    """
    logger.warning("⚠️  Use 'npx prisma migrate reset' para remover tabelas com Prisma")


# Classe Base para compatibilidade (não usada com Prisma)
class Base:
    """Classe base para compatibilidade com SQLAlchemy"""
    metadata = None

