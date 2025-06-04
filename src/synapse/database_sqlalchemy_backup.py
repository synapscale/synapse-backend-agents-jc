"""
Configuração do banco de dados SQLAlchemy
"""
from prisma import Prisma
from typing import Generator
import re
from src.synapse.config import settings

def convert_prisma_url_to_postgres(url: str) -> str:
    """
    Converte URL do Prisma Accelerate para URL PostgreSQL padrão
    """
    if url.startswith('prisma+postgres://'):
        return 'sqlite:///./synapse.db'
    return url
database_url = convert_prisma_url_to_postgres(settings.DATABASE_URL)
engine = create_engine(database_url, echo=settings.DEBUG, pool_pre_ping=True, pool_recycle=300)
# SessionLocal = Use Prisma() directly
Base = declarative_base()

def get_prisma() -> Generator[Session, None, None]:
    """
    Dependency para obter sessão do banco de dados
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """
    Criar todas as tabelas no banco de dados
    """
    Base.metadata.create_all(bind=engine)

def drop_tables():
    """
    Remover todas as tabelas do banco de dados
    """
    Base.metadata.drop_all(bind=engine)