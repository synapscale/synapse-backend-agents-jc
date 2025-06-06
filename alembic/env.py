"""Configuração do Alembic para SynapScale Backend."""

import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context
import sys
import os

# Adicionar o diretório src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

# Importar os modelos
from src.synapse.database import Base
from src.synapse.models import *

# Configuração do Alembic
config = context.config

# Configuração de logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadados dos modelos
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Executar migrações em modo 'offline'."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection: Connection) -> None:
    """Executar migrações com conexão."""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()

async def run_async_migrations() -> None:
    """Executar migrações em modo assíncrono."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

def run_migrations_online() -> None:
    """Executar migrações em modo 'online'."""
    # Para SQLite síncrono
    try:
        from sqlalchemy import create_engine
        url = config.get_main_option("sqlalchemy.url")
        engine = create_engine(url)
        
        with engine.connect() as connection:
            do_run_migrations(connection)
    except Exception as e:
        print(f"Erro ao executar migrações: {e}")
        # Fallback para modo assíncrono
        asyncio.run(run_async_migrations())

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
