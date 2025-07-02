#!/usr/bin/env python3
"""
Script para análise de relacionamentos FK em modelos SQLAlchemy
Task 1.2: Validar relacionamentos de chave estrangeira existentes
"""

import os
import sys
import inspect
from pathlib import Path
from typing import Dict, List, Any, Set
from sqlalchemy import create_engine, MetaData, inspect as sqlalchemy_inspect
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import relationship, foreign, remote
from sqlalchemy.sql.schema import ForeignKey
import importlib.util

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from synapse.core.config import settings
    from synapse.models import *
    from synapse.database import Base
except ImportError as e:
    print(f"❌ Erro ao importar modelos: {e}")
    sys.exit(1)


class FKRelationshipAnalyzer:
    """Analisador de relacionamentos FK"""

    def __init__(self):
        self.issues = []
        self.models = {}
        self.relationships = {}
        self.fk_constraints = {}

    def collect_models(self):
        """Coletar todos os modelos SQLAlchemy"""
        print("🔍 Coletando modelos SQLAlchemy...")

        for name, obj in globals().items():
            if (
                inspect.isclass(obj)
                and hasattr(obj, "__tablename__")
                and isinstance(obj, DeclarativeMeta)
                and obj != Base
            ):

                self.models[name] = obj
                print(f"   ✓ Modelo encontrado: {name} -> {obj.__tablename__}")

        print(f"📊 Total de modelos encontrados: {len(self.models)}")
        return self.models

    def analyze_sqlalchemy_relationships(self):
        """Analisar relacionamentos definidos nos modelos SQLAlchemy"""
        print("\n🔗 Analisando relacionamentos SQLAlchemy...")

        for model_name, model_class in self.models.items():
            table_name = model_class.__tablename__

            # Analisar relationships
            relationships = []
            for attr_name in dir(model_class):
                attr = getattr(model_class, attr_name)
                if (
                    hasattr(attr, "property")
                    and hasattr(attr.property, "__class__")
                    and "RelationshipProperty" in str(attr.property.__class__)
                ):
                    rel_info = {
                        "name": attr_name,
                        "target_entity": (
                            attr.property.entity.class_.__name__
                            if hasattr(attr.property, "entity")
                            else "Unknown"
                        ),
                        "back_populates": attr.property.back_populates,
                        "backref": attr.property.backref,
                        "foreign_keys": (
                            [str(fk) for fk in attr.property.local_columns]
                            if hasattr(attr.property, "local_columns")
                            else []
                        ),
                    }
                    relationships.append(rel_info)

            # Analisar foreign keys nas colunas
            foreign_keys = []
            if hasattr(model_class, "__table__"):
                for column in model_class.__table__.columns:
                    if column.foreign_keys:
                        for fk in column.foreign_keys:
                            fk_info = {
                                "column": column.name,
                                "references": f"{fk.column.table.name}.{fk.column.name}",
                                "constraint_name": (
                                    fk.constraint.name if fk.constraint else None
                                ),
                            }
                            foreign_keys.append(fk_info)

            if relationships or foreign_keys:
                self.relationships[model_name] = {
                    "table_name": table_name,
                    "relationships": relationships,
                    "foreign_keys": foreign_keys,
                }

    def get_database_fk_constraints(self):
        """Obter constraints FK diretamente do banco de dados"""
        print("\n💾 Analisando constraints FK no banco de dados...")

        try:
            database_url = settings.get_database_url()
            engine = create_engine(database_url)
            inspector = sqlalchemy_inspect(engine)

            tables = inspector.get_table_names(schema="synapscale_db")

            for table_name in tables:
                try:
                    fks = inspector.get_foreign_keys(table_name, schema="synapscale_db")
                    if fks:
                        self.fk_constraints[table_name] = fks
                        print(f"   ✓ {table_name}: {len(fks)} FK constraints")
                except Exception as e:
                    print(f"   ⚠️  Erro ao analisar {table_name}: {e}")

        except Exception as e:
            print(f"❌ Erro ao conectar com banco: {e}")
            self.issues.append(f"Erro de conexão com banco: {e}")

    def find_relationship_issues(self):
        """Identificar problemas nos relacionamentos"""
        print("\n🔍 Identificando problemas nos relacionamentos...")

        # 1. Verificar relacionamentos orfãos (sem FK correspondente)
        for model_name, rel_data in self.relationships.items():
            for rel in rel_data["relationships"]:
                target_model = rel["target_entity"]

                # Verificar se o modelo target existe
                if target_model not in self.models and target_model != "Unknown":
                    issue = f"❌ {model_name}.{rel['name']}: Referencia modelo inexistente '{target_model}'"
                    self.issues.append(issue)
                    print(f"   {issue}")

                # Verificar se há FK correspondente (aproximado)
                has_corresponding_fk = False
                for fk in rel_data["foreign_keys"]:
                    if target_model.lower() in fk["references"].lower():
                        has_corresponding_fk = True
                        break

                if not has_corresponding_fk and target_model != "Unknown":
                    issue = f"⚠️  {model_name}.{rel['name']}: Relacionamento sem FK correspondente para '{target_model}'"
                    self.issues.append(issue)
                    print(f"   {issue}")

        # 2. Verificar FKs orfãs (sem relacionamento correspondente)
        for model_name, rel_data in self.relationships.items():
            for fk in rel_data["foreign_keys"]:
                referenced_table = fk["references"].split(".")[0]

                # Procurar modelo correspondente para a tabela referenciada
                referenced_model = None
                for m_name, m_class in self.models.items():
                    if (
                        hasattr(m_class, "__tablename__")
                        and m_class.__tablename__ == referenced_table
                    ):
                        referenced_model = m_name
                        break

                if not referenced_model:
                    issue = f"⚠️  {model_name}: FK {fk['column']} referencia tabela inexistente '{referenced_table}'"
                    self.issues.append(issue)
                    print(f"   {issue}")

        # 3. Verificar discrepâncias entre banco e modelos
        model_tables = {
            model_class.__tablename__: model_name
            for model_name, model_class in self.models.items()
            if hasattr(model_class, "__tablename__")
        }

        for table_name, db_fks in self.fk_constraints.items():
            if table_name in model_tables:
                model_name = model_tables[table_name]
                model_fks = self.relationships.get(model_name, {}).get(
                    "foreign_keys", []
                )

                if len(db_fks) != len(model_fks):
                    issue = f"⚠️  {model_name} ({table_name}): {len(db_fks)} FKs no banco vs {len(model_fks)} FKs no modelo"
                    self.issues.append(issue)
                    print(f"   {issue}")

    def generate_report(self):
        """Gerar relatório completo"""
        print("\n" + "=" * 80)
        print("📋 RELATÓRIO DE RELACIONAMENTOS FK")
        print("=" * 80)

        print(f"\n📊 ESTATÍSTICAS:")
        print(f"   • Modelos SQLAlchemy: {len(self.models)}")
        print(f"   • Modelos com relacionamentos: {len(self.relationships)}")
        print(f"   • Tabelas no banco com FK: {len(self.fk_constraints)}")
        print(f"   • Issues identificados: {len(self.issues)}")

        if self.relationships:
            print(f"\n🔗 MODELOS COM RELACIONAMENTOS:")
            for model_name, rel_data in self.relationships.items():
                print(f"\n   📁 {model_name} ({rel_data['table_name']}):")

                if rel_data["relationships"]:
                    print(f"      Relationships ({len(rel_data['relationships'])}):")
                    for rel in rel_data["relationships"]:
                        print(f"         • {rel['name']} -> {rel['target_entity']}")
                        if rel["back_populates"]:
                            print(
                                f"           (back_populates: {rel['back_populates']})"
                            )

                if rel_data["foreign_keys"]:
                    print(f"      Foreign Keys ({len(rel_data['foreign_keys'])}):")
                    for fk in rel_data["foreign_keys"]:
                        print(f"         • {fk['column']} -> {fk['references']}")

        if self.issues:
            print(f"\n❌ ISSUES IDENTIFICADOS ({len(self.issues)}):")
            for i, issue in enumerate(self.issues, 1):
                print(f"   {i}. {issue}")
        else:
            print(f"\n✅ Nenhum issue crítico identificado!")

        # Salvar relatório em arquivo
        report_file = (
            Path(__file__).parent.parent
            / ".taskmaster"
            / "reports"
            / "fk_relationships_analysis.txt"
        )
        report_file.parent.mkdir(parents=True, exist_ok=True)

        with open(report_file, "w", encoding="utf-8") as f:
            f.write("RELATÓRIO DE RELACIONAMENTOS FK - SynapScale\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Modelos SQLAlchemy: {len(self.models)}\n")
            f.write(f"Issues identificados: {len(self.issues)}\n\n")

            if self.issues:
                f.write("ISSUES:\n")
                for issue in self.issues:
                    f.write(f"- {issue}\n")

            f.write(f"\nRelatório gerado em: {report_file}")

        print(f"\n💾 Relatório salvo em: {report_file}")

        return len(self.issues)


def main():
    """Executar análise completa"""
    print("🚀 Iniciando análise de relacionamentos FK...")
    print("=" * 80)

    analyzer = FKRelationshipAnalyzer()

    # Executar análise
    analyzer.collect_models()
    analyzer.analyze_sqlalchemy_relationships()
    analyzer.get_database_fk_constraints()
    analyzer.find_relationship_issues()

    # Gerar relatório
    issue_count = analyzer.generate_report()

    print("\n" + "=" * 80)
    if issue_count == 0:
        print("✅ Análise concluída: Nenhum problema crítico encontrado!")
        return 0
    else:
        print(f"⚠️  Análise concluída: {issue_count} issues identificados")
        return issue_count


if __name__ == "__main__":
    exit_code = main()
    sys.exit(min(exit_code, 1))  # Limitar exit code para 0 ou 1
