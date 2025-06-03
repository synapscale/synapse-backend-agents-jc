"""
Configuração do banco de dados SQLAlchemy
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from src.synapse.config import settings

# Criar engine do banco de dados
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # Log SQL queries em modo debug
    pool_pre_ping=True,   # Verificar conexões antes de usar
    pool_recycle=300,     # Reciclar conexões a cada 5 minutos
)

# Criar sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para modelos
Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
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

