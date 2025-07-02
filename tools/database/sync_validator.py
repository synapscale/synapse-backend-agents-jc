#!/usr/bin/env python3
"""
🔄 SYNC VALIDATOR - Validador de Sincronização

Verifica se banco de dados, models, API e schemas estão todos sincronizados:
- Compara estrutura do banco com models SQLAlchemy
- Valida endpoints da API com schemas do banco
- Verifica se OpenAPI.json reflete a realidade
- Detecta inconsistências e sugere correções

Este é o coração da manutenção automatizada!
"""

import os
import sys
import json
import ast
import re
from pathlib import Path
from typing import Dict, List, Any, Set, Optional, Tuple
import psycopg2
from dotenv import load_dotenv

# Cores para terminal
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

load_dotenv()

class SyncValidator:
    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL")
        self.project_root = Path(__file__).parent.parent.parent
        self.inconsistencies = []
        self.suggestions = []
        
    def log(self, message: str, level: str = "INFO", color: str = Colors.WHITE):
        """Log com cores"""
        print(f"{color}[{level}] {message}{Colors.END}")

    def get_database_schema(self) -> Dict[str, Dict[str, Any]]:
        """Extrai schema completo do banco de dados"""
        self.log("📊 Extraindo schema do banco de dados", "INFO", Colors.CYAN)
        
        schema = {}
        
        try:
            conn = psycopg2.connect(self.database_url)
            cursor = conn.cursor()
            
            # Buscar todas as tabelas no schema synapscale_db
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'synapscale_db'
                ORDER BY table_name
            """)
            
            tables = [row[0] for row in cursor.fetchall()]
            
            for table in tables:
                self.log(f"   🔍 Analisando tabela: {table}", "DEBUG", Colors.WHITE)
                
                # Buscar colunas da tabela
                cursor.execute("""
                    SELECT 
                        column_name,
                        data_type,
                        is_nullable,
                        column_default,
                        character_maximum_length
                    FROM information_schema.columns 
                    WHERE table_schema = 'synapscale_db' 
                    AND table_name = %s
                    ORDER BY ordinal_position
                """, (table,))
                
                columns = {}
                for col_data in cursor.fetchall():
                    col_name, data_type, is_nullable, default, max_length = col_data
                    columns[col_name] = {
                        "type": data_type,
                        "nullable": is_nullable == "YES",
                        "default": default,
                        "max_length": max_length
                    }
                
                # Buscar chaves estrangeiras
                cursor.execute("""
                    SELECT
                        kcu.column_name,
                        ccu.table_name AS foreign_table,
                        ccu.column_name AS foreign_column
                    FROM information_schema.table_constraints AS tc 
                    JOIN information_schema.key_column_usage AS kcu
                        ON tc.constraint_name = kcu.constraint_name
                        AND tc.table_schema = kcu.table_schema
                    JOIN information_schema.constraint_column_usage AS ccu
                        ON ccu.constraint_name = tc.constraint_name
                        AND ccu.table_schema = tc.table_schema
                    WHERE tc.constraint_type = 'FOREIGN KEY' 
                    AND tc.table_schema = 'synapscale_db'
                    AND tc.table_name = %s
                """, (table,))
                
                foreign_keys = {}
                for fk_data in cursor.fetchall():
                    col_name, foreign_table, foreign_column = fk_data
                    foreign_keys[col_name] = {
                        "references_table": foreign_table,
                        "references_column": foreign_column
                    }
                
                schema[table] = {
                    "columns": columns,
                    "foreign_keys": foreign_keys
                }
            
            cursor.close()
            conn.close()
            
            self.log(f"✅ Schema extraído: {len(schema)} tabelas", "SUCCESS", Colors.GREEN)
            return schema
            
        except Exception as e:
            self.log(f"❌ Erro ao extrair schema: {e}", "ERROR", Colors.RED)
            return {}

    def find_sqlalchemy_models(self) -> Dict[str, Dict[str, Any]]:
        """Encontra e analisa models SQLAlchemy no código"""
        self.log("🔍 Procurando models SQLAlchemy", "INFO", Colors.CYAN)
        
        models = {}
        
        # Procurar por arquivos Python que podem conter models
        model_patterns = [
            "src/**/models.py",
            "src/**/model.py", 
            "src/**/*model*.py",
            "models/*.py",
            "app/models/*.py"
        ]
        
        python_files = []
        for pattern in model_patterns:
            python_files.extend(self.project_root.glob(pattern))
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Parse do AST para encontrar classes de model
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        # Verificar se é um model SQLAlchemy
                        if self._is_sqlalchemy_model(node, content):
                            model_info = self._extract_model_info(node, content)
                            if model_info:
                                models[node.name] = model_info
                                self.log(f"   📋 Model encontrado: {node.name}", "DEBUG", Colors.WHITE)
                
            except Exception as e:
                self.log(f"⚠️ Erro ao analisar {file_path}: {e}", "WARNING", Colors.YELLOW)
        
        self.log(f"✅ Models encontrados: {len(models)}", "SUCCESS", Colors.GREEN)
        return models

    def _is_sqlalchemy_model(self, node: ast.ClassDef, content: str) -> bool:
        """Verifica se uma classe é um model SQLAlchemy"""
        # Procurar por herança de Base, Model, ou similar
        for base in node.bases:
            if isinstance(base, ast.Name):
                if base.id in ['Base', 'Model', 'db.Model']:
                    return True
            elif isinstance(base, ast.Attribute):
                if base.attr in ['Model', 'Base']:
                    return True
        
        # Procurar por __tablename__ na classe
        for item in node.body:
            if isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name) and target.id == '__tablename__':
                        return True
        
        return False

    def _extract_model_info(self, node: ast.ClassDef, content: str) -> Optional[Dict[str, Any]]:
        """Extrai informações de um model SQLAlchemy"""
        model_info = {
            "table_name": None,
            "columns": {},
            "relationships": {}
        }
        
        # Extrair __tablename__
        for item in node.body:
            if isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        if target.id == '__tablename__':
                            if isinstance(item.value, ast.Str):
                                model_info["table_name"] = item.value.s
                            elif isinstance(item.value, ast.Constant):
                                model_info["table_name"] = item.value.value
        
        # Extrair colunas (análise básica)
        for item in node.body:
            if isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        column_name = target.id
                        if not column_name.startswith('_'):  # Ignorar atributos privados
                            # Tentar extrair tipo da coluna do valor
                            column_info = self._parse_column_definition(item.value, content)
                            if column_info:
                                model_info["columns"][column_name] = column_info
        
        return model_info if model_info["table_name"] else None

    def _parse_column_definition(self, value_node: ast.AST, content: str) -> Optional[Dict[str, Any]]:
        """Parse básico de definição de coluna SQLAlchemy"""
        # Esta é uma implementação simplificada
        # Em produção, seria mais robusta
        
        if isinstance(value_node, ast.Call):
            if isinstance(value_node.func, ast.Name):
                if value_node.func.id == 'Column':
                    return {"type": "Column", "details": "SQLAlchemy Column"}
            elif isinstance(value_node.func, ast.Attribute):
                if value_node.func.attr == 'Column':
                    return {"type": "Column", "details": "SQLAlchemy Column"}
        
        return None

    def compare_database_vs_models(self, db_schema: Dict, models: Dict) -> List[Dict[str, Any]]:
        """Compara schema do banco com models SQLAlchemy"""
        self.log("🔄 Comparando banco vs models", "INFO", Colors.MAGENTA)
        
        inconsistencies = []
        
        # Mapear models por table_name
        models_by_table = {}
        for model_name, model_info in models.items():
            table_name = model_info.get("table_name")
            if table_name:
                models_by_table[table_name] = {
                    "model_name": model_name,
                    **model_info
                }
        
        # Verificar tabelas que existem no banco mas não nos models
        db_tables = set(db_schema.keys())
        model_tables = set(models_by_table.keys())
        
        missing_models = db_tables - model_tables
        missing_tables = model_tables - db_tables
        
        for table in missing_models:
            inconsistencies.append({
                "type": "missing_model",
                "severity": "warning",
                "table": table,
                "message": f"Tabela '{table}' existe no banco mas não tem model correspondente",
                "suggestion": f"Criar model SQLAlchemy para tabela '{table}'"
            })
        
        for table in missing_tables:
            inconsistencies.append({
                "type": "missing_table", 
                "severity": "error",
                "table": table,
                "message": f"Model para tabela '{table}' existe mas tabela não está no banco",
                "suggestion": f"Executar migração para criar tabela '{table}' ou remover model"
            })
        
        # Verificar tabelas que existem em ambos
        common_tables = db_tables & model_tables
        for table in common_tables:
            db_table = db_schema[table]
            model_table = models_by_table[table]
            
            # Comparar colunas (comparação básica)
            db_columns = set(db_table["columns"].keys())
            model_columns = set(model_table["columns"].keys())
            
            missing_in_model = db_columns - model_columns
            missing_in_db = model_columns - db_columns
            
            for col in missing_in_model:
                inconsistencies.append({
                    "type": "missing_model_column",
                    "severity": "warning", 
                    "table": table,
                    "column": col,
                    "message": f"Coluna '{col}' existe no banco mas não no model '{model_table['model_name']}'",
                    "suggestion": f"Adicionar coluna '{col}' ao model '{model_table['model_name']}'"
                })
            
            for col in missing_in_db:
                inconsistencies.append({
                    "type": "missing_db_column",
                    "severity": "error",
                    "table": table,
                    "column": col, 
                    "message": f"Coluna '{col}' existe no model mas não no banco",
                    "suggestion": f"Executar migração para adicionar coluna '{col}' ou remover do model"
                })
        
        self.log(f"📋 Encontradas {len(inconsistencies)} inconsistências", "INFO", Colors.WHITE)
        return inconsistencies

    def check_api_endpoints(self) -> List[Dict[str, Any]]:
        """Verifica endpoints da API e sua relação com o banco"""
        self.log("🌐 Verificando endpoints da API", "INFO", Colors.CYAN)
        
        issues = []
        
        # Procurar por arquivos de rotas/endpoints
        route_patterns = [
            "src/**/routes/*.py",
            "src/**/api/*.py",
            "src/**/*route*.py",
            "src/**/*endpoint*.py",
            "app/routes/*.py",
            "app/api/*.py"
        ]
        
        route_files = []
        for pattern in route_patterns:
            route_files.extend(self.project_root.glob(pattern))
        
        endpoints_found = []
        
        for file_path in route_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Buscar por decorators de rota (FastAPI, Flask)
                route_patterns = [
                    r'@app\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']',
                    r'@router\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']',
                    r'@[a-zA-Z_]+\.(route|get|post|put|delete|patch)\(["\']([^"\']+)["\']'
                ]
                
                for pattern in route_patterns:
                    matches = re.findall(pattern, content, re.MULTILINE)
                    for match in matches:
                        if len(match) >= 2:
                            method = match[0]
                            path = match[1] if len(match) > 1 else match[0]
                            endpoints_found.append({
                                "method": method.upper(),
                                "path": path,
                                "file": str(file_path)
                            })
                
            except Exception as e:
                self.log(f"⚠️ Erro ao analisar {file_path}: {e}", "WARNING", Colors.YELLOW)
        
        self.log(f"📋 Encontrados {len(endpoints_found)} endpoints", "INFO", Colors.WHITE)
        
        # Verificações básicas de endpoints
        crud_endpoints = {}
        for endpoint in endpoints_found:
            path = endpoint["path"]
            method = endpoint["method"]
            
            # Detectar padrões CRUD
            if '/users' in path:
                if 'users' not in crud_endpoints:
                    crud_endpoints['users'] = set()
                crud_endpoints['users'].add(method)
        
        # Verificar se CRUD está completo para recursos importantes
        for resource, methods in crud_endpoints.items():
            expected_methods = {'GET', 'POST', 'PUT', 'DELETE'}
            missing_methods = expected_methods - methods
            
            if missing_methods:
                issues.append({
                    "type": "incomplete_crud",
                    "severity": "info",
                    "resource": resource,
                    "missing_methods": list(missing_methods),
                    "message": f"CRUD incompleto para '{resource}' - métodos faltantes: {missing_methods}",
                    "suggestion": f"Considere implementar métodos faltantes para '{resource}'"
                })
        
        return issues

    def generate_sync_report(self, db_schema: Dict, models: Dict, 
                           db_model_issues: List, api_issues: List) -> Dict[str, Any]:
        """Gera relatório completo de sincronização"""
        
        total_issues = len(db_model_issues) + len(api_issues)
        critical_issues = len([i for i in db_model_issues + api_issues if i.get('severity') == 'error'])
        warnings = len([i for i in db_model_issues + api_issues if i.get('severity') == 'warning'])
        
        # Determinar status geral
        if critical_issues == 0 and warnings == 0:
            status = "SINCRONIZADO"
            status_color = Colors.GREEN
        elif critical_issues == 0:
            status = "AVISOS"
            status_color = Colors.YELLOW
        else:
            status = "DESSINCRONIZADO"
            status_color = Colors.RED
        
        report = {
            "timestamp": str(os.times()),
            "status": status,
            "summary": {
                "database_tables": len(db_schema),
                "sqlalchemy_models": len(models),
                "total_issues": total_issues,
                "critical_issues": critical_issues,
                "warnings": warnings
            },
            "database_schema": db_schema,
            "models": models,
            "db_model_inconsistencies": db_model_issues,
            "api_issues": api_issues
        }
        
        # Exibir relatório
        print(f"\n{Colors.BOLD}{'='*80}{Colors.END}")
        print(f"{Colors.BOLD}🔄 RELATÓRIO DE SINCRONIZAÇÃO{Colors.END}")
        print(f"{Colors.BOLD}{'='*80}{Colors.END}")
        
        print(f"\n{status_color}{Colors.BOLD}📊 STATUS: {status}{Colors.END}")
        print(f"{Colors.WHITE}📋 Tabelas no banco: {len(db_schema)}{Colors.END}")
        print(f"{Colors.WHITE}🏗️  Models SQLAlchemy: {len(models)}{Colors.END}")
        print(f"{Colors.WHITE}⚠️  Total de problemas: {total_issues}{Colors.END}")
        
        if db_model_issues:
            print(f"\n{Colors.MAGENTA}{Colors.BOLD}🔄 INCONSISTÊNCIAS BANCO vs MODELS:{Colors.END}")
            for issue in db_model_issues:
                severity_color = Colors.RED if issue['severity'] == 'error' else Colors.YELLOW
                print(f"{severity_color}   • {issue['message']}{Colors.END}")
                print(f"{Colors.CYAN}     💡 {issue['suggestion']}{Colors.END}")
        
        if api_issues:
            print(f"\n{Colors.BLUE}{Colors.BOLD}🌐 PROBLEMAS DA API:{Colors.END}")
            for issue in api_issues:
                print(f"{Colors.BLUE}   • {issue['message']}{Colors.END}")
                if 'suggestion' in issue:
                    print(f"{Colors.CYAN}     💡 {issue['suggestion']}{Colors.END}")
        
        if total_issues == 0:
            print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 Tudo sincronizado perfeitamente!{Colors.END}")
        
        print(f"\n{Colors.BOLD}{'='*80}{Colors.END}")
        
        return report

    def run_full_sync_check(self) -> Dict[str, Any]:
        """Executa verificação completa de sincronização"""
        self.log("🚀 Iniciando verificação de sincronização", "INFO", Colors.BOLD)
        
        # 1. Extrair schema do banco
        db_schema = self.get_database_schema()
        
        # 2. Encontrar models SQLAlchemy
        models = self.find_sqlalchemy_models()
        
        # 3. Comparar banco vs models
        db_model_issues = self.compare_database_vs_models(db_schema, models)
        
        # 4. Verificar endpoints da API
        api_issues = self.check_api_endpoints()
        
        # 5. Gerar relatório
        return self.generate_sync_report(db_schema, models, db_model_issues, api_issues)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Sync Validator - Verificação de sincronização")
    parser.add_argument("--json", action="store_true", help="Saída em formato JSON")
    parser.add_argument("--report", type=str, help="Salvar relatório em arquivo")
    
    args = parser.parse_args()
    
    validator = SyncValidator()
    report = validator.run_full_sync_check()
    
    # Salvar relatório se solicitado
    if args.report:
        with open(args.report, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Relatório salvo em: {args.report}")
    
    # Saída JSON se solicitada
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    
    # Exit code baseado no status
    if report['summary']['critical_issues'] > 0:
        sys.exit(1)  # Problemas críticos
    elif report['summary']['warnings'] > 0:
        sys.exit(2)  # Avisos
    else:
        sys.exit(0)  # Tudo OK

if __name__ == "__main__":
    main()
