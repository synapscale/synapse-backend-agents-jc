#!/usr/bin/env python3

import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()


async def check_missing_models():
    try:
        DATABASE_URL = os.getenv(
            "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/defaultdb"
        )
        conn = await asyncpg.connect(DATABASE_URL)

        # Tabelas críticas que devem ter models
        critical_tables = [
            "users",
            "tenants",
            "workspaces",
            "agents",
            "llms",
            "files",
            "plans",
            "features",
            "invoices",
            "payment_methods",
            "rbac_roles",
            "rbac_permissions",
            "user_tenant_roles",
            "refresh_tokens",
            "email_verification_tokens",
            "password_reset_tokens",
            "audit_log",
            "workflow_executions",
            "conversations",
            "messages",
            "workspace_members",
            "agent_configurations",
            "nodes",
        ]

        # Models existentes
        models_dir = "src/synapse/models"
        existing_files = []
        for f in os.listdir(models_dir):
            if f.endswith(".py") and f != "__init__.py":
                existing_files.append(f.replace(".py", ""))

        print("=== TABELAS CRÍTICAS vs MODELS ===")
        missing_models = []

        for table in critical_tables:
            # Verificar se existe no banco
            exists_in_db = await conn.fetchval(
                """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'synapscale_db' AND table_name = $1
                )
            """,
                table,
            )

            # Verificar se existe model
            possible_model_names = [
                table,
                table.rstrip("s"),  # remove plural
                table.replace("_", ""),
                table.replace("_", "").rstrip("s"),
            ]

            has_model = any(name in existing_files for name in possible_model_names)

            status = "✅" if has_model else "❌"
            db_status = "(DB)" if exists_in_db else "(NO DB)"

            print(f"{status} {table} {db_status}")

            if exists_in_db and not has_model:
                missing_models.append(table)

        print(f"\n❌ MODELS FALTANDO: {len(missing_models)}")
        for model in missing_models:
            print(f"  - {model}")

        print(f"\n📊 RESUMO:")
        print(f"  Total tabelas críticas: {len(critical_tables)}")
        print(f"  Models existentes: {len(existing_files)}")
        print(f"  Models faltando: {len(missing_models)}")

        await conn.close()

    except Exception as e:
        print(f"Erro: {e}")


if __name__ == "__main__":
    asyncio.run(check_missing_models())
