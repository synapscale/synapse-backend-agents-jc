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

# Importar o Base do projeto para autogenerate funcionar
sys.path.append(os.path.join(BASE_DIR, "src"))
from synapse.database import Base

target_metadata = Base.metadata


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
        # Garantir que só trabalhamos com o schema synapscale_db
        connection.execute(text(f"SET search_path TO {DATABASE_SCHEMA}"))

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            version_table_schema=DATABASE_SCHEMA,
            include_schemas=False,  # CRÍTICO: Só trabalhar com o schema definido
            include_object=lambda obj, name, type_, reflected, compare_to: (
                # Só incluir objetos do schema synapscale_db
                getattr(obj, "schema", None) == DATABASE_SCHEMA
                or (
                    hasattr(obj, "table")
                    and getattr(obj.table, "schema", None) == DATABASE_SCHEMA
                )
            ),
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
