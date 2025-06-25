"""
Script para criar as tabelas do Memory Bank no banco de dados
"""
import os
import sys
import logging
from pathlib import Path
from sqlalchemy import create_engine, text, MetaData, Table, Column, Integer, String, Text, DateTime, Boolean, ForeignKey, UniqueConstraint, Float
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB, ARRAY

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("memory-bank-migrations")

def get_database_url():
    """
    Obtém a URL do banco de dados a partir das variáveis de ambiente
    """
    # Verificar se a variável DATABASE_URL está definida
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return database_url
    
    # Verificar se as variáveis individuais estão definidas
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_user = os.getenv("DB_USER", "postgres")
    db_pass = os.getenv("DB_PASS", "postgres")
    db_name = os.getenv("DB_NAME", "synapse")
    
    # Construir a URL do banco de dados
    return f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"

def run_migrations():
    """
    Executa as migrações para criar as tabelas do Memory Bank
    """
    try:
        # Obter a URL do banco de dados
        database_url = get_database_url()
        logger.info(f"Conectando ao banco de dados: {database_url.split('@')[-1]}")
        
        # Criar engine do SQLAlchemy
        engine = create_engine(database_url)
        
        # Verificar se o schema synapscale_db existe
        with engine.connect() as conn:
            result = conn.execute(text("SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'synapscale_db'"))
            if not result.fetchone():
                logger.info("Criando schema synapscale_db...")
                conn.execute(text("CREATE SCHEMA IF NOT EXISTS synapscale_db"))
                conn.commit()
        
        # Criar metadata
        metadata = MetaData(schema="synapscale_db")
        
        # Definir tabelas
        collections = Table(
            "memory_bank_collections",
            metadata,
            Column("id", Integer, primary_key=True, autoincrement=True),
            Column("name", String(255), nullable=False),
            Column("description", Text, nullable=True),
            Column("user_id", Integer, nullable=False),
            Column("workspace_id", Integer, nullable=True),
            Column("is_active", Boolean, default=True, nullable=False),
            Column("metadata", JSONB, nullable=True),
            Column("created_at", DateTime(timezone=True), server_default=func.now(), nullable=False),
            Column("updated_at", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False),
            UniqueConstraint("name", "user_id", name="uq_collection_name_user_id")
        )
        
        memories = Table(
            "memory_bank_memories",
            metadata,
            Column("id", Integer, primary_key=True, autoincrement=True),
            Column("collection_id", Integer, ForeignKey("synapscale_db.memory_bank_collections.id", ondelete="CASCADE"), nullable=False),
            Column("content", Text, nullable=False),
            Column("metadata", JSONB, nullable=True),
            Column("embedding", ARRAY(Float), nullable=True),
            Column("user_id", Integer, nullable=False),
            Column("workspace_id", Integer, nullable=True),
            Column("is_active", Boolean, default=True, nullable=False),
            Column("created_at", DateTime(timezone=True), server_default=func.now(), nullable=False),
            Column("updated_at", DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
        )
        
        # Criar tabelas
        logger.info("Criando tabelas do Memory Bank...")
        metadata.create_all(engine)
        
        logger.info("Tabelas do Memory Bank criadas com sucesso!")
        return True
        
    except Exception as e:
        logger.error(f"Erro ao criar tabelas do Memory Bank: {e}")
        return False

if __name__ == "__main__":
    success = run_migrations()
    sys.exit(0 if success else 1)
