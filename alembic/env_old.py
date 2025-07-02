"""Alembic env.py ajustado para carregar variáveis do .env e usar Config centralizada.

• Carrega automaticamente o arquivo .env com python-dotenv (caso exista).
• Obtém a DATABASE_URL (e demais configs) diretamente do objeto Settings
  (`synapse.core.config.settings`), garantindo que **todas** as variáveis
  sensíveis venham apenas do .env.
• Remove qualquer dependência de string de conexão fixa dentro do alembic.ini.
"""

from logging.config import fileConfig
from sqlalchemy import pool
from alembic import context

import os
import sys

# ---------------------------------------------------------------------------
# 1. Garante que o diretório "src" esteja no sys.path para importar o projeto
# ---------------------------------------------------------------------------
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_DIR = os.path.join(BASE_DIR, "src")
sys.path.insert(0, SRC_DIR)

# ---------------------------------------------------------------------------
# 2. Carrega variáveis do .env antes de qualquer import que dependa delas
# ---------------------------------------------------------------------------
try:
    from dotenv import load_dotenv  # type: ignore

    load_dotenv(os.path.join(BASE_DIR, ".env"))
except ModuleNotFoundError:
    # python-dotenv não instalado – opcional, segue sem carregar .env
    pass

# ---------------------------------------------------------------------------
# 3. Configurações simplificadas para o schema
# ---------------------------------------------------------------------------
DATABASE_SCHEMA = "synapscale_db"

# 4. Importa modelos diretamente (simplified approach)
try:
    from synapse.database import Base  # noqa: E402
    from synapse.models import *  # noqa: F401,F403,E402

    target_metadata = Base.metadata
except ImportError:
    # Fallback para quando não conseguir importar
    target_metadata = None

# ---------------------------------------------------------------------------
# Configuração Alembic
# ---------------------------------------------------------------------------
config = context.config

# Usa o logger definido no alembic.ini, se existir
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata das tabelas
target_metadata = Base.metadata


# ---------------------------------------------------------------------------
# Helpers para migração (online/offline)
# ---------------------------------------------------------------------------


def get_url() -> str:
    """Retorna a DATABASE_URL a partir das Settings (.env)."""

    if not settings.DATABASE_URL:
        raise RuntimeError(
            "DATABASE_URL não definida. Configure no seu .env para rodar Alembic."
        )

    return settings.DATABASE_URL


def run_migrations_offline() -> None:
    """Modo offline: gera SQL sem conectar no banco."""

    context.configure(
        url=get_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        version_table_schema=settings.DATABASE_SCHEMA,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Modo online: conecta no banco e aplica migrações."""

    from sqlalchemy import create_engine, text  # noqa: E402

    connectable = create_engine(
        get_url(),
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        # Criar o schema se não existir
        schema_sql = f"CREATE SCHEMA IF NOT EXISTS {DATABASE_SCHEMA}"
        connection.execute(text(schema_sql))
        connection.commit()

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


# ---------------------------------------------------------------------------
# Execução
# ---------------------------------------------------------------------------

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
