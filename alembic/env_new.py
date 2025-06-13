"""
Alembic env.py simplificado para o schema synapscale_db
"""

from logging.config import fileConfig
from sqlalchemy import pool, text
from alembic import context
import os
import sys

# Configurações
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATABASE_SCHEMA = "synapscale_db"

# Carrega variáveis do .env
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(BASE_DIR, ".env"))
except ImportError:
    pass

# Configuração Alembic
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata vazio para agora - vamos criar as tabelas via scripts SQL
target_metadata = None


def get_url() -> str:
    """Retorna a URL do banco de dados."""
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL não definida. Configure no seu .env.")
    return DATABASE_URL


def run_migrations_offline() -> None:
    """Modo offline: gera SQL sem conectar no banco."""
    context.configure(
        url=get_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        version_table_schema=DATABASE_SCHEMA,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Modo online: conecta no banco e aplica migrações."""
    from sqlalchemy import create_engine

    connectable = create_engine(
        get_url(),
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            version_table_schema=DATABASE_SCHEMA,
            include_schemas=True
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
