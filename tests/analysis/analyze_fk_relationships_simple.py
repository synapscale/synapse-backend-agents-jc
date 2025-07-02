#!/usr/bin/env python3
"""
Script simplificado para análise de relacionamentos FK
Task 1.2: Validar relacionamentos de chave estrangeira existentes
"""

import os
import sys
import inspect
from pathlib import Path
from typing import Dict, List, Any
from sqlalchemy import create_engine, MetaData, inspect as sqlalchemy_inspect

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def simple_fk_analysis():
    """Análise simples de FK sem configuração automática de relacionamentos"""
    print("🚀 Análise Simples de Relacionamentos FK")
    print("=" * 80)

    issues = []

    try:
        from synapse.core.config import settings

        database_url = settings.get_database_url()
        engine = create_engine(database_url)
        inspector = sqlalchemy_inspect(engine)

        print("💾 Analisando FK constraints no banco de dados...")

        # Obter todas as tabelas no schema
        tables = inspector.get_table_names(schema="synapscale_db")
        print(f"📊 Total de tabelas encontradas: {len(tables)}")

        fk_report = {}
        total_fks = 0

        for table_name in tables:
            try:
                fks = inspector.get_foreign_keys(table_name, schema="synapscale_db")
                if fks:
                    fk_report[table_name] = fks
                    total_fks += len(fks)
                    print(f"   ✓ {table_name}: {len(fks)} FK constraints")

                    # Verificar se as tabelas referenciadas existem
                    for fk in fks:
                        referenced_table = fk["referred_table"]
                        if referenced_table not in tables:
                            issue = f"❌ {table_name}: FK referencia tabela inexistente '{referenced_table}'"
                            issues.append(issue)
                            print(f"      {issue}")

            except Exception as e:
                issue = f"⚠️  Erro ao analisar {table_name}: {e}"
                issues.append(issue)
                print(f"   {issue}")

        print(f"\n📈 ESTATÍSTICAS:")
        print(f"   • Total de tabelas: {len(tables)}")
        print(f"   • Tabelas com FK: {len(fk_report)}")
        print(f"   • Total de FK constraints: {total_fks}")
        print(f"   • Issues identificados: {len(issues)}")

        # Agora vamos analisar quais modelos SQLAlchemy existem
        print(f"\n🔍 Analisando modelos SQLAlchemy existentes...")

        model_files = list(Path("src/synapse/models").glob("*.py"))
        existing_models = {}

        for model_file in model_files:
            if model_file.name == "__init__.py":
                continue

            try:
                # Ler o arquivo e procurar por classes que herdam de Base
                with open(model_file, "r") as f:
                    content = f.read()

                # Procurar por definições de classe
                lines = content.split("\n")
                for line in lines:
                    if "class " in line and "(Base)" in line:
                        class_name = line.split("class ")[1].split("(")[0].strip()

                        # Procurar pelo __tablename__
                        for i, l in enumerate(lines):
                            if f"class {class_name}" in l:
                                # Procurar __tablename__ nas próximas 10 linhas
                                for j in range(i, min(i + 10, len(lines))):
                                    if "__tablename__" in lines[j]:
                                        table_name = (
                                            lines[j].split('"')[1]
                                            if '"' in lines[j]
                                            else lines[j].split("'")[1]
                                        )
                                        existing_models[class_name] = table_name
                                        print(
                                            f"   ✓ Modelo {class_name} -> {table_name}"
                                        )
                                        break
                                break

            except Exception as e:
                print(f"   ⚠️  Erro ao processar {model_file}: {e}")

        print(f"📊 Total de modelos SQLAlchemy encontrados: {len(existing_models)}")

        # Verificar tabelas sem modelos
        model_tables = set(existing_models.values())
        missing_models = []

        for table_name in tables:
            if table_name not in model_tables:
                missing_models.append(table_name)

        print(f"\n❌ TABELAS SEM MODELOS SQLALCHEMY ({len(missing_models)}):")
        missing_by_category = {
            "RBAC": [],
            "Auth Tokens": [],
            "Agents": [],
            "Audit": [],
            "Payments": [],
            "CRM/Marketing": [],
            "Knowledge": [],
            "Others": [],
        }

        for table in missing_models:
            if "rbac_" in table:
                missing_by_category["RBAC"].append(table)
            elif "token" in table and ("password" in table or "email" in table):
                missing_by_category["Auth Tokens"].append(table)
            elif "agent_" in table:
                missing_by_category["Agents"].append(table)
            elif "audit" in table:
                missing_by_category["Audit"].append(table)
            elif any(
                word in table
                for word in ["payment", "invoice", "subscription", "coupon"]
            ):
                missing_by_category["Payments"].append(table)
            elif any(word in table for word in ["contact", "campaign"]):
                missing_by_category["CRM/Marketing"].append(table)
            elif "knowledge" in table or "tool" in table:
                missing_by_category["Knowledge"].append(table)
            else:
                missing_by_category["Others"].append(table)

        for category, tables in missing_by_category.items():
            if tables:
                print(f"\n   🏷️  {category}:")
                for table in tables:
                    print(f"      • {table}")

        # Gerar relatório final
        print(f"\n" + "=" * 80)
        print(f"📋 RESUMO EXECUTIVO")
        print(f"=" * 80)

        coverage = (len(existing_models) / len(tables)) * 100 if tables else 0
        print(
            f"✅ Cobertura de modelos: {len(existing_models)}/{len(tables)} ({coverage:.1f}%)"
        )
        print(f"❌ Tabelas sem modelos: {len(missing_models)}")
        print(f"🔗 Total de FK constraints: {total_fks}")
        print(f"⚠️  Issues de FK identificados: {len(issues)}")

        # Salvar relatório
        report_file = Path(".taskmaster/reports/fk_simple_analysis.txt")
        report_file.parent.mkdir(parents=True, exist_ok=True)

        with open(report_file, "w", encoding="utf-8") as f:
            f.write("ANÁLISE SIMPLES DE FK - SynapScale\n")
            f.write("=" * 50 + "\n\n")
            f.write(
                f"Cobertura de modelos: {len(existing_models)}/{len(tables)} ({coverage:.1f}%)\n"
            )
            f.write(f"Tabelas sem modelos: {len(missing_models)}\n")
            f.write(f"Total FK constraints: {total_fks}\n")
            f.write(f"Issues identificados: {len(issues)}\n\n")

            if missing_models:
                f.write("TABELAS SEM MODELOS:\n")
                for category, tables in missing_by_category.items():
                    if tables:
                        f.write(f"\n{category}:\n")
                        for table in tables:
                            f.write(f"  - {table}\n")

            if issues:
                f.write(f"\nISSUES IDENTIFICADOS:\n")
                for issue in issues:
                    f.write(f"- {issue}\n")

        print(f"\n💾 Relatório salvo em: {report_file}")

        return len(issues) + len(missing_models)

    except Exception as e:
        print(f"❌ Erro geral na análise: {e}")
        return 1


if __name__ == "__main__":
    exit_code = simple_fk_analysis()
    print(
        f"\n{'✅ Análise concluída!' if exit_code == 0 else f'⚠️  Análise concluída com {exit_code} items para correção'}"
    )
    sys.exit(min(exit_code, 1))
