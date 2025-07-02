#!/usr/bin/env python3
"""
Script para analisar completude dos schemas Pydantic
Compara tabelas no banco com schemas disponíveis
"""

import os
import sys
from pathlib import Path
from sqlalchemy import create_engine, inspect

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

DATABASE_URL = "postgresql://doadmin:AVNS_DDsc3wHcfGgbX_USTUt@db-banco-dados-automacoes-do-user-13851907-0.e.db.ondigitalocean.com:25060/defaultdb?sslmode=require"


def get_database_tables():
    """Obtém lista de tabelas do banco"""
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    inspector = inspect(engine)
    return inspector.get_table_names(schema="synapscale_db")


def get_existing_schemas():
    """Analisa schemas Pydantic existentes"""
    schemas_path = Path(__file__).parent.parent / "src" / "synapse" / "schemas"

    existing_schemas = {
        "create": set(),
        "update": set(),
        "response": set(),
        "list_response": set(),
    }

    # Analisar models.py
    models_file = schemas_path / "models.py"
    if models_file.exists():
        content = models_file.read_text()

        # Encontrar padrões de classes
        import re

        create_patterns = re.findall(r"class (\w+)Create\(", content)
        update_patterns = re.findall(r"class (\w+)Update\(", content)
        response_patterns = re.findall(r"class (\w+)Response\(", content)
        list_patterns = re.findall(r"class (\w+)ListResponse\(", content)

        for pattern in create_patterns:
            existing_schemas["create"].add(pattern.lower())
        for pattern in update_patterns:
            existing_schemas["update"].add(pattern.lower())
        for pattern in response_patterns:
            existing_schemas["response"].add(pattern.lower())
        for pattern in list_patterns:
            existing_schemas["list_response"].add(pattern.lower())

    return existing_schemas


def main():
    print("🔍 Analisando completude dos schemas...")

    try:
        # Obter tabelas do banco
        db_tables = get_database_tables()
        print(f"📊 Encontradas {len(db_tables)} tabelas no banco")

        # Obter schemas existentes
        existing_schemas = get_existing_schemas()

        print(f"\n📋 Schemas existentes:")
        print(f"  Create: {len(existing_schemas['create'])} schemas")
        print(f"  Update: {len(existing_schemas['update'])} schemas")
        print(f"  Response: {len(existing_schemas['response'])} schemas")
        print(f"  ListResponse: {len(existing_schemas['list_response'])} schemas")

        # Principais tabelas que precisam de schemas
        important_tables = [
            "users",
            "tenants",
            "workspaces",
            "agents",
            "workflows",
            "nodes",
            "files",
            "conversations",
            "llms",
            "tools",
            "knowledge_bases",
            "billing_events",
            "usage_logs",
            "workspace_members",
            "workspace_activities",
            "workspace_invitations",
            "plans",
            "subscriptions",
            "features",
            "rbac_roles",
            "rbac_permissions",
        ]

        print(f"\n🎯 Analisando tabelas importantes:")

        missing_schemas = {
            "create": [],
            "update": [],
            "response": [],
            "list_response": [],
        }

        for table in important_tables:
            if table in db_tables:
                # Converter nome da tabela para singular (convenção comum)
                schema_name = table.rstrip("s")
                if table.endswith("ies"):
                    schema_name = table[:-3] + "y"
                elif table == "workspace_members":
                    schema_name = "workspacemember"
                elif table == "workspace_activities":
                    schema_name = "workspaceactivity"
                elif table == "workspace_invitations":
                    schema_name = "workspaceinvitation"
                elif table == "rbac_roles":
                    schema_name = "rbacrole"
                elif table == "rbac_permissions":
                    schema_name = "rbacpermission"

                # Verificar se existem schemas
                has_create = schema_name in existing_schemas["create"]
                has_update = schema_name in existing_schemas["update"]
                has_response = schema_name in existing_schemas["response"]
                has_list = schema_name in existing_schemas["list_response"]

                status = "✅" if all([has_create, has_update, has_response]) else "❌"

                print(
                    f"  {status} {table:25} -> {schema_name:20} (C:{has_create} U:{has_update} R:{has_response} L:{has_list})"
                )

                if not has_create:
                    missing_schemas["create"].append((table, schema_name))
                if not has_update:
                    missing_schemas["update"].append((table, schema_name))
                if not has_response:
                    missing_schemas["response"].append((table, schema_name))
                if not has_list:
                    missing_schemas["list_response"].append((table, schema_name))
            else:
                print(f"  ⚠️  {table:25} -> Tabela não existe no banco")

        print(f"\n📝 Resumo dos schemas em falta:")
        for schema_type, missing in missing_schemas.items():
            if missing:
                print(f"  {schema_type.title()}: {len(missing)} schemas")
                for table, schema_name in missing[:5]:  # Primeiros 5
                    print(f"    - {schema_name}{schema_type.replace('_', '').title()}")
                if len(missing) > 5:
                    print(f"    ... e mais {len(missing)-5}")
            else:
                print(f"  {schema_type.title()}: ✅ Completo")

        # Verificar tabelas do banco que não estão na lista importante
        other_tables = set(db_tables) - set(important_tables)
        if other_tables:
            print(f"\n📚 Outras tabelas no banco ({len(other_tables)}):")
            for table in sorted(list(other_tables)[:10]):
                print(f"  - {table}")
            if len(other_tables) > 10:
                print(f"  ... e mais {len(other_tables)-10}")

    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
