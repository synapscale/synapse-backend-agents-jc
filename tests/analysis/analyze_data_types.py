#!/usr/bin/env python3
"""
Script para análise de tipos de dados - SQLAlchemy vs PostgreSQL
Task 1.3: Resolver inconsistências de tipos de dados
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Tuple
from sqlalchemy import create_engine, inspect as sqlalchemy_inspect
from sqlalchemy.types import *
import re

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def analyze_data_types():
    """Análise completa de tipos de dados entre modelos SQLAlchemy e banco PostgreSQL"""
    print("🔍 Análise de Tipos de Dados - SQLAlchemy vs PostgreSQL")
    print("=" * 80)

    issues = []

    try:
        from synapse.core.config import settings

        database_url = settings.get_database_url()
        engine = create_engine(database_url)
        inspector = sqlalchemy_inspect(engine)

        print("💾 Coletando informações do banco de dados...")

        # Obter estrutura do banco
        db_tables = {}
        tables = inspector.get_table_names(schema="synapscale_db")

        for table_name in tables:
            try:
                columns = inspector.get_columns(table_name, schema="synapscale_db")
                db_tables[table_name] = {col["name"]: col for col in columns}
                print(f"   ✓ {table_name}: {len(columns)} colunas")
            except Exception as e:
                print(f"   ⚠️  Erro ao analisar {table_name}: {e}")

        print(f"📊 Total de tabelas analisadas: {len(db_tables)}")

        # Analisar modelos SQLAlchemy
        print(f"\n🔍 Analisando modelos SQLAlchemy...")

        model_files = list(Path("src/synapse/models").glob("*.py"))
        model_mappings = {}

        for model_file in model_files:
            if model_file.name == "__init__.py":
                continue

            try:
                with open(model_file, "r", encoding="utf-8") as f:
                    content = f.read()

                # Extrair informações dos modelos
                model_info = extract_model_info(content)
                for model_name, model_data in model_info.items():
                    model_mappings[model_name] = model_data
                    print(f"   ✓ {model_name} -> {model_data['table_name']}")

            except Exception as e:
                print(f"   ⚠️  Erro ao processar {model_file}: {e}")

        print(f"📊 Total de modelos analisados: {len(model_mappings)}")

        # Comparar tipos de dados
        print(f"\n🔗 Comparando tipos de dados...")

        type_issues = []
        perfect_matches = 0

        for model_name, model_data in model_mappings.items():
            table_name = model_data["table_name"]

            if table_name not in db_tables:
                continue

            db_columns = db_tables[table_name]
            model_columns = model_data["columns"]

            print(f"\n📋 Analisando {model_name} ({table_name}):")

            for col_name, col_info in model_columns.items():
                if col_name in db_columns:
                    db_type = db_columns[col_name]["type"]
                    model_type = col_info["type"]

                    # Comparar tipos
                    is_compatible = compare_types(model_type, str(db_type))

                    if is_compatible:
                        print(f"   ✅ {col_name}: {model_type} ≈ {db_type}")
                        perfect_matches += 1
                    else:
                        issue = {
                            "model": model_name,
                            "table": table_name,
                            "column": col_name,
                            "model_type": model_type,
                            "db_type": str(db_type),
                            "severity": determine_severity(model_type, str(db_type)),
                        }
                        type_issues.append(issue)
                        print(
                            f"   ❌ {col_name}: {model_type} ≠ {db_type} [{issue['severity']}]"
                        )
                else:
                    print(f"   ⚠️  {col_name}: Coluna não encontrada no banco")

        # Gerar relatório de inconsistências
        print(f"\n" + "=" * 80)
        print(f"📋 RELATÓRIO DE INCONSISTÊNCIAS DE TIPOS")
        print(f"=" * 80)

        # Agrupar por severidade
        critical_issues = [i for i in type_issues if i["severity"] == "CRITICAL"]
        high_issues = [i for i in type_issues if i["severity"] == "HIGH"]
        medium_issues = [i for i in type_issues if i["severity"] == "MEDIUM"]
        low_issues = [i for i in type_issues if i["severity"] == "LOW"]

        print(f"✅ Tipos compatíveis: {perfect_matches}")
        print(f"🔴 Issues críticos: {len(critical_issues)}")
        print(f"🟠 Issues high: {len(high_issues)}")
        print(f"🟡 Issues medium: {len(medium_issues)}")
        print(f"🟢 Issues low: {len(low_issues)}")

        # Detalhar issues críticos
        if critical_issues:
            print(f"\n🔴 ISSUES CRÍTICOS:")
            for issue in critical_issues:
                print(
                    f"   • {issue['model']}.{issue['column']}: {issue['model_type']} → {issue['db_type']}"
                )

        if high_issues:
            print(f"\n🟠 ISSUES HIGH:")
            for issue in high_issues:
                print(
                    f"   • {issue['model']}.{issue['column']}: {issue['model_type']} → {issue['db_type']}"
                )

        # Salvar relatório detalhado
        report_file = Path(".taskmaster/reports/data_types_analysis.txt")
        report_file.parent.mkdir(parents=True, exist_ok=True)

        with open(report_file, "w", encoding="utf-8") as f:
            f.write("ANÁLISE DE TIPOS DE DADOS - SynapScale\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Tipos compatíveis: {perfect_matches}\n")
            f.write(f"Issues críticos: {len(critical_issues)}\n")
            f.write(f"Issues high: {len(high_issues)}\n")
            f.write(f"Issues medium: {len(medium_issues)}\n")
            f.write(f"Issues low: {len(low_issues)}\n\n")

            for severity, issues in [
                ("CRITICAL", critical_issues),
                ("HIGH", high_issues),
                ("MEDIUM", medium_issues),
                ("LOW", low_issues),
            ]:
                if issues:
                    f.write(f"{severity} ISSUES:\n")
                    for issue in issues:
                        f.write(
                            f"  {issue['model']}.{issue['column']}: {issue['model_type']} → {issue['db_type']}\n"
                        )
                    f.write("\n")

        print(f"\n💾 Relatório detalhado salvo em: {report_file}")

        return len(critical_issues) + len(high_issues)

    except Exception as e:
        print(f"❌ Erro geral na análise: {e}")
        import traceback

        traceback.print_exc()
        return 1


def extract_model_info(content: str) -> Dict[str, Dict]:
    """Extrair informações dos modelos do código fonte"""
    models = {}
    lines = content.split("\n")

    for i, line in enumerate(lines):
        if "class " in line and "(Base)" in line:
            model_name = line.split("class ")[1].split("(")[0].strip()

            # Encontrar __tablename__
            table_name = None
            columns = {}

            for j in range(
                i, min(i + 200, len(lines))
            ):  # Procurar nas próximas 200 linhas
                if "__tablename__" in lines[j]:
                    table_name = (
                        lines[j].split('"')[1]
                        if '"' in lines[j]
                        else lines[j].split("'")[1]
                    )

                # Encontrar definições de colunas
                if "Column(" in lines[j] and "=" in lines[j]:
                    col_match = re.search(r"(\w+)\s*=\s*Column\((.*?)\)", lines[j])
                    if col_match:
                        col_name = col_match.group(1)
                        col_def = col_match.group(2)

                        # Extrair tipo básico
                        type_match = re.search(
                            r"(UUID|Integer|String|Text|DateTime|Boolean|JSONB|Float|Numeric|BigInteger)",
                            col_def,
                        )
                        if type_match:
                            columns[col_name] = {"type": type_match.group(1)}

            if table_name:
                models[model_name] = {"table_name": table_name, "columns": columns}

    return models


def compare_types(sqlalchemy_type: str, postgres_type: str) -> bool:
    """Comparar se tipos SQLAlchemy e PostgreSQL são compatíveis"""

    # Mapping de tipos compatíveis
    type_mappings = {
        "UUID": ["UUID"],
        "Integer": ["INTEGER", "SERIAL"],
        "BigInteger": ["BIGINT", "BIGSERIAL"],
        "String": ["VARCHAR", "CHARACTER VARYING"],
        "Text": ["TEXT"],
        "DateTime": ["TIMESTAMP WITHOUT TIME ZONE", "TIMESTAMP WITH TIME ZONE"],
        "Boolean": ["BOOLEAN"],
        "JSONB": ["JSONB"],
        "Float": ["REAL", "DOUBLE PRECISION"],
        "Numeric": ["NUMERIC", "DECIMAL"],
    }

    postgres_type_clean = postgres_type.upper().split("(")[0].strip()

    if sqlalchemy_type in type_mappings:
        return postgres_type_clean in type_mappings[sqlalchemy_type]

    return False


def determine_severity(model_type: str, db_type: str) -> str:
    """Determinar severidade da inconsistência"""

    # Incompatibilidades críticas
    critical_combos = [
        ("String", "INTEGER"),
        ("Integer", "TEXT"),
        ("UUID", "INTEGER"),
        ("Boolean", "TEXT"),
    ]

    db_type_clean = db_type.upper().split("(")[0].strip()

    for model_t, db_t in critical_combos:
        if model_type == model_t and db_t in db_type_clean:
            return "CRITICAL"

    # Issues de alta prioridade
    if "VARCHAR" in db_type_clean and model_type == "Text":
        return "HIGH"

    if "SERIAL" in db_type_clean and model_type == "Integer":
        return "MEDIUM"

    return "LOW"


if __name__ == "__main__":
    exit_code = analyze_data_types()
    print(
        f"\n{'✅ Análise concluída!' if exit_code == 0 else f'⚠️  Análise concluída com {exit_code} issues de alta prioridade'}"
    )
    sys.exit(min(exit_code, 1))
