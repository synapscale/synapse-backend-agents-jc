#!/usr/bin/env python3
"""
Script para analisar problemas de sincronização entre Models, Schemas e Endpoints
"""

import os
import re
import ast
from pathlib import Path
from typing import Dict, List, Set, Tuple
import json

class SyncAnalyzer:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.models_path = self.project_root / "src" / "synapse" / "models"
        self.schemas_path = self.project_root / "src" / "synapse" / "schemas"
        self.endpoints_path = self.project_root / "src" / "synapse" / "api" / "v1" / "endpoints"
        
        self.models_fields = {}
        self.schemas_fields = {}
        self.endpoints_references = {}
        self.sync_issues = []

    def extract_model_fields(self, model_file: Path) -> Dict[str, Set[str]]:
        """Extrai campos de um model SQLAlchemy"""
        fields = set()
        
        with open(model_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Buscar definições de Column
        column_pattern = r'(\w+)\s*(?::\s*[^=]+)?\s*=\s*Column\('
        for match in re.finditer(column_pattern, content):
            field_name = match.group(1)
            if not field_name.startswith('_'):
                fields.add(field_name)
        
        # Buscar mapped_column (SQLAlchemy 2.0)
        mapped_pattern = r'(\w+):\s*Mapped\[.*?\]\s*=\s*mapped_column\('
        for match in re.finditer(mapped_pattern, content):
            field_name = match.group(1)
            if not field_name.startswith('_'):
                fields.add(field_name)
        
        return fields

    def extract_schema_fields(self, schema_file: Path) -> Dict[str, Set[str]]:
        """Extrai campos de um schema Pydantic"""
        fields = set()
        
        with open(schema_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Buscar definições de Field
        field_pattern = r'(\w+):\s*.*?=\s*Field\('
        for match in re.finditer(field_pattern, content):
            field_name = match.group(1)
            if not field_name.startswith('_'):
                fields.add(field_name)
        
        # Buscar definições simples
        simple_pattern = r'(\w+):\s*\w+.*?='
        for match in re.finditer(simple_pattern, content):
            field_name = match.group(1)
            if not field_name.startswith('_') and field_name not in ['Config', 'model_config']:
                fields.add(field_name)
        
        return fields

    def extract_endpoint_references(self, endpoint_file: Path) -> Dict[str, Set[str]]:
        """Extrai referências a campos de models nos endpoints"""
        references = set()
        
        with open(endpoint_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Buscar referências a campos de models (Model.field)
        model_ref_pattern = r'(\w+)\.(\w+)\s*=='
        for match in re.finditer(model_ref_pattern, content):
            model_name = match.group(1)
            field_name = match.group(2)
            references.add(f"{model_name}.{field_name}")
        
        # Buscar outras referências
        filter_pattern = r'filter\(.*?(\w+)\.(\w+)'
        for match in re.finditer(filter_pattern, content):
            model_name = match.group(1)
            field_name = match.group(2)
            references.add(f"{model_name}.{field_name}")
        
        return references

    def analyze_all_files(self):
        """Analisa todos os arquivos e mapeia campos"""
        print("🔍 Analisando Models...")
        for model_file in self.models_path.glob("*.py"):
            if model_file.name != "__init__.py":
                model_name = model_file.stem
                self.models_fields[model_name] = self.extract_model_fields(model_file)
        
        print("📋 Analisando Schemas...")
        for schema_file in self.schemas_path.glob("*.py"):
            if schema_file.name != "__init__.py":
                schema_name = schema_file.stem
                self.schemas_fields[schema_name] = self.extract_schema_fields(schema_file)
        
        print("🔗 Analisando Endpoints...")
        for endpoint_file in self.endpoints_path.glob("*.py"):
            if endpoint_file.name != "__init__.py":
                endpoint_name = endpoint_file.stem
                self.endpoints_references[endpoint_name] = self.extract_endpoint_references(endpoint_file)

    def find_sync_issues(self):
        """Encontra problemas de sincronização"""
        issues = []
        
        # Verificar referências inexistentes nos endpoints
        for endpoint_name, references in self.endpoints_references.items():
            for ref in references:
                if '.' in ref:
                    model_name, field_name = ref.split('.', 1)
                    
                    # Verificar se o model existe
                    if model_name.lower() in self.models_fields:
                        model_fields = self.models_fields[model_name.lower()]
                        if field_name not in model_fields:
                            issues.append({
                                "type": "missing_model_field",
                                "endpoint": endpoint_name,
                                "model": model_name,
                                "field": field_name,
                                "reference": ref,
                                "severity": "high"
                            })
        
        # Verificar models sem schemas
        for model_name in self.models_fields:
            if model_name not in self.schemas_fields:
                issues.append({
                    "type": "missing_schema",
                    "model": model_name,
                    "severity": "medium"
                })
        
        # Verificar schemas sem models
        for schema_name in self.schemas_fields:
            if schema_name not in self.models_fields:
                issues.append({
                    "type": "orphaned_schema",
                    "schema": schema_name,
                    "severity": "low"
                })
        
        return issues

    def generate_report(self):
        """Gera relatório completo de sincronização"""
        self.analyze_all_files()
        issues = self.find_sync_issues()
        
        report = {
            "summary": {
                "models_count": len(self.models_fields),
                "schemas_count": len(self.schemas_fields),
                "endpoints_count": len(self.endpoints_references),
                "issues_count": len(issues)
            },
            "models": {name: list(fields) for name, fields in self.models_fields.items()},
            "schemas": {name: list(fields) for name, fields in self.schemas_fields.items()},
            "endpoints_references": {name: list(refs) for name, refs in self.endpoints_references.items()},
            "issues": issues
        }
        
        return report

    def print_report(self):
        """Imprime relatório formatado"""
        report = self.generate_report()
        
        print("\n" + "="*60)
        print("📊 RELATÓRIO DE SINCRONIZAÇÃO")
        print("="*60)
        
        print(f"✅ Models encontrados: {report['summary']['models_count']}")
        print(f"📋 Schemas encontrados: {report['summary']['schemas_count']}")
        print(f"🔗 Endpoints encontrados: {report['summary']['endpoints_count']}")
        print(f"🚨 Problemas encontrados: {report['summary']['issues_count']}")
        
        print("\n🚨 PROBLEMAS CRÍTICOS:")
        high_issues = [i for i in report['issues'] if i['severity'] == 'high']
        for issue in high_issues:
            if issue['type'] == 'missing_model_field':
                print(f"  ❌ {issue['endpoint']}.py: {issue['model']}.{issue['field']} NÃO EXISTE")
        
        print("\n⚠️  PROBLEMAS MÉDIOS:")
        medium_issues = [i for i in report['issues'] if i['severity'] == 'medium']
        for issue in medium_issues:
            if issue['type'] == 'missing_schema':
                print(f"  🟡 Model '{issue['model']}' sem schema correspondente")
        
        print("\n💡 RECOMENDAÇÕES:")
        print("  1. Corrigir referências inexistentes nos endpoints")
        print("  2. Criar schemas para models sem schema")
        print("  3. Estabelecer processo de validação contínua")
        
        return report

if __name__ == "__main__":
    analyzer = SyncAnalyzer()
    report = analyzer.print_report()
    
    # Salvar relatório em arquivo
    with open("sync_analysis_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Relatório salvo em: sync_analysis_report.json")
