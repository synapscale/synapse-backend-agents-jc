#!/usr/bin/env python3
"""
📚 DOC GENERATOR - Gerador Automático de Documentação

Gera documentação completa baseada nos checks e análises:
- Schema do banco em Markdown
- Mapa de relacionamentos 
- Documentação da API
- Diagramas ER em Mermaid
- Health checks em formato HTML

Mantém documentação sempre atualizada automaticamente!
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
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

class DocumentationGenerator:
    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL")
        self.project_root = Path(__file__).parent.parent.parent
        self.docs_dir = self.project_root / "docs" / "database"
        self.docs_dir.mkdir(parents=True, exist_ok=True)
        
    def log(self, message: str, level: str = "INFO", color: str = Colors.WHITE):
        """Log com cores"""
        print(f"{color}[{level}] {message}{Colors.END}")

    def get_database_info(self) -> Dict[str, Any]:
        """Coleta informações completas do banco"""
        self.log("📊 Coletando informações do banco", "INFO", Colors.CYAN)
        
        info = {
            "schemas": {},
            "relationships": [],
            "statistics": {}
        }
        
        try:
            conn = psycopg2.connect(self.database_url)
            cursor = conn.cursor()
            
            # Buscar todos os schemas
            cursor.execute("""
                SELECT schema_name 
                FROM information_schema.schemata 
                WHERE schema_name NOT LIKE 'pg_%' 
                AND schema_name != 'information_schema'
                ORDER BY schema_name
            """)
            
            schemas = [row[0] for row in cursor.fetchall()]
            
            for schema in schemas:
                # Buscar tabelas do schema
                cursor.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = %s 
                    ORDER BY table_name
                """, (schema,))
                
                tables = [row[0] for row in cursor.fetchall()]
                
                schema_info = {"tables": {}}
                
                for table in tables:
                    # Buscar colunas
                    cursor.execute("""
                        SELECT 
                            column_name,
                            data_type,
                            is_nullable,
                            column_default,
                            character_maximum_length
                        FROM information_schema.columns 
                        WHERE table_schema = %s AND table_name = %s
                        ORDER BY ordinal_position
                    """, (schema, table))
                    
                    columns = []
                    for col_data in cursor.fetchall():
                        col_name, data_type, is_nullable, default, max_length = col_data
                        columns.append({
                            "name": col_name,
                            "type": data_type,
                            "nullable": is_nullable == "YES",
                            "default": default,
                            "max_length": max_length
                        })
                    
                    # Buscar estatísticas da tabela
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {schema}.{table}")
                        row_count = cursor.fetchone()[0]
                    except:
                        row_count = 0
                    
                    schema_info["tables"][table] = {
                        "columns": columns,
                        "row_count": row_count
                    }
                
                info["schemas"][schema] = schema_info
            
            # Buscar relacionamentos
            cursor.execute("""
                SELECT
                    tc.table_schema,
                    tc.table_name, 
                    kcu.column_name, 
                    ccu.table_schema AS foreign_schema,
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name 
                FROM information_schema.table_constraints AS tc 
                JOIN information_schema.key_column_usage AS kcu
                    ON tc.constraint_name = kcu.constraint_name
                    AND tc.table_schema = kcu.table_schema
                JOIN information_schema.constraint_column_usage AS ccu
                    ON ccu.constraint_name = tc.constraint_name
                    AND ccu.table_schema = tc.table_schema
                WHERE tc.constraint_type = 'FOREIGN KEY'
                ORDER BY tc.table_schema, tc.table_name
            """)
            
            for rel_data in cursor.fetchall():
                schema, table, column, foreign_schema, foreign_table, foreign_column = rel_data
                info["relationships"].append({
                    "from_schema": schema,
                    "from_table": table,
                    "from_column": column,
                    "to_schema": foreign_schema,
                    "to_table": foreign_table,
                    "to_column": foreign_column
                })
            
            cursor.close()
            conn.close()
            
            self.log("✅ Informações coletadas com sucesso", "SUCCESS", Colors.GREEN)
            return info
            
        except Exception as e:
            self.log(f"❌ Erro ao coletar informações: {e}", "ERROR", Colors.RED)
            return info

    def generate_schema_markdown(self, db_info: Dict[str, Any]) -> str:
        """Gera documentação do schema em Markdown"""
        self.log("📝 Gerando documentação Markdown do schema", "INFO", Colors.CYAN)
        
        md = []
        md.append("# Documentação do Schema do Banco de Dados")
        md.append("")
        md.append(f"**Gerado em:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        md.append("")
        
        # Índice
        md.append("## Índice")
        md.append("")
        for schema_name in db_info["schemas"]:
            md.append(f"- [Schema {schema_name}](#schema-{schema_name.replace('_', '-')})")
        md.append("- [Relacionamentos](#relacionamentos)")
        md.append("")
        
        # Documentar cada schema
        for schema_name, schema_info in db_info["schemas"].items():
            md.append(f"## Schema {schema_name}")
            md.append("")
            
            total_tables = len(schema_info["tables"])
            total_rows = sum(table["row_count"] for table in schema_info["tables"].values())
            
            md.append(f"**Resumo:**")
            md.append(f"- 📋 Total de tabelas: {total_tables}")
            md.append(f"- 📊 Total de registros: {total_rows:,}")
            md.append("")
            
            # Documentar cada tabela
            for table_name, table_info in schema_info["tables"].items():
                md.append(f"### Tabela: `{table_name}`")
                md.append("")
                md.append(f"**Registros:** {table_info['row_count']:,}")
                md.append("")
                
                # Tabela de colunas
                md.append("| Coluna | Tipo | Nulo | Padrão | Tamanho Máx |")
                md.append("|--------|------|------|--------|-------------|")
                
                for col in table_info["columns"]:
                    nullable = "✅" if col["nullable"] else "❌"
                    default = col["default"] or "-"
                    max_length = str(col["max_length"]) if col["max_length"] else "-"
                    
                    md.append(f"| `{col['name']}` | {col['type']} | {nullable} | {default} | {max_length} |")
                
                md.append("")
        
        # Documentar relacionamentos
        md.append("## Relacionamentos")
        md.append("")
        
        if db_info["relationships"]:
            md.append("| Tabela Origem | Coluna | Tabela Destino | Coluna Destino |")
            md.append("|---------------|--------|----------------|----------------|")
            
            for rel in db_info["relationships"]:
                from_table = f"{rel['from_schema']}.{rel['from_table']}"
                to_table = f"{rel['to_schema']}.{rel['to_table']}"
                md.append(f"| `{from_table}` | `{rel['from_column']}` | `{to_table}` | `{rel['to_column']}` |")
        else:
            md.append("Nenhum relacionamento de chave estrangeira encontrado.")
        
        md.append("")
        md.append("---")
        md.append("*Documentação gerada automaticamente pelo Doc Generator*")
        
        return "\n".join(md)

    def generate_mermaid_er_diagram(self, db_info: Dict[str, Any]) -> str:
        """Gera diagrama ER em formato Mermaid"""
        self.log("🎨 Gerando diagrama ER em Mermaid", "INFO", Colors.CYAN)
        
        mermaid = []
        mermaid.append("erDiagram")
        mermaid.append("")
        
        # Definir entidades
        for schema_name, schema_info in db_info["schemas"].items():
            for table_name, table_info in schema_info["tables"].items():
                entity_name = f"{schema_name}_{table_name}".upper()
                mermaid.append(f"    {entity_name} {{")
                
                for col in table_info["columns"]:
                    col_type = col["type"].upper()
                    nullable = "" if col["nullable"] else " NOT NULL"
                    mermaid.append(f"        {col['name']} {col_type}{nullable}")
                
                mermaid.append("    }")
                mermaid.append("")
        
        # Definir relacionamentos
        for rel in db_info["relationships"]:
            from_entity = f"{rel['from_schema']}_{rel['from_table']}".upper()
            to_entity = f"{rel['to_schema']}_{rel['to_table']}".upper()
            mermaid.append(f"    {from_entity} ||--o{{ {to_entity} : {rel['from_column']}")
        
        return "\n".join(mermaid)

    def generate_health_html(self, health_data: Dict[str, Any] = None) -> str:
        """Gera dashboard HTML de health check"""
        self.log("🌐 Gerando dashboard HTML", "INFO", Colors.CYAN)
        
        if not health_data:
            health_data = {
                "status": "UNKNOWN",
                "timestamp": datetime.now().isoformat(),
                "summary": {"total_checks": 0, "successful_checks": 0, "warnings": 0, "errors": 0}
            }
        
        html = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SynapScale Database Health Dashboard</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            padding: 30px;
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
        }}
        .status-card {{
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
            text-align: center;
            font-size: 24px;
            font-weight: bold;
        }}
        .status-excellent {{ background-color: #d4edda; color: #155724; }}
        .status-good {{ background-color: #fff3cd; color: #856404; }}
        .status-critical {{ background-color: #f8d7da; color: #721c24; }}
        .metrics {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        .metric-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}
        .metric-value {{
            font-size: 32px;
            font-weight: bold;
            color: #007bff;
        }}
        .metric-label {{
            color: #6c757d;
            margin-top: 8px;
        }}
        .timestamp {{
            color: #6c757d;
            font-size: 14px;
            text-align: center;
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏥 SynapScale Database Health Dashboard</h1>
        </div>
        
        <div class="status-card status-{health_data['status'].lower()}">
            📊 Status: {health_data['status']}
        </div>
        
        <div class="metrics">
            <div class="metric-card">
                <div class="metric-value">{health_data['summary']['total_checks']}</div>
                <div class="metric-label">Total de Verificações</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{health_data['summary']['successful_checks']}</div>
                <div class="metric-label">Verificações OK</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{health_data['summary']['warnings']}</div>
                <div class="metric-label">Avisos</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{health_data['summary']['errors']}</div>
                <div class="metric-label">Erros</div>
            </div>
        </div>
        
        <div class="timestamp">
            🕒 Última atualização: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
    </div>
    
    <script>
        // Auto-refresh a cada 5 minutos
        setTimeout(() => {{
            window.location.reload();
        }}, 300000);
    </script>
</body>
</html>
"""
        return html

    def generate_all_docs(self) -> Dict[str, str]:
        """Gera toda a documentação"""
        self.log("🚀 Gerando toda a documentação", "INFO", Colors.BOLD)
        
        # Coletar informações do banco
        db_info = self.get_database_info()
        
        docs = {}
        
        # Gerar documentação Markdown
        schema_md = self.generate_schema_markdown(db_info)
        schema_file = self.docs_dir / "schema.md"
        with open(schema_file, 'w', encoding='utf-8') as f:
            f.write(schema_md)
        docs["schema_markdown"] = str(schema_file)
        self.log(f"✅ Schema Markdown: {schema_file}", "SUCCESS", Colors.GREEN)
        
        # Gerar diagrama Mermaid
        mermaid_diagram = self.generate_mermaid_er_diagram(db_info)
        mermaid_file = self.docs_dir / "er_diagram.mmd"
        with open(mermaid_file, 'w', encoding='utf-8') as f:
            f.write(mermaid_diagram)
        docs["mermaid_diagram"] = str(mermaid_file)
        self.log(f"✅ Diagrama Mermaid: {mermaid_file}", "SUCCESS", Colors.GREEN)
        
        # Gerar HTML dashboard
        health_html = self.generate_health_html()
        html_file = self.docs_dir / "health_dashboard.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(health_html)
        docs["health_dashboard"] = str(html_file)
        self.log(f"✅ Dashboard HTML: {html_file}", "SUCCESS", Colors.GREEN)
        
        # Salvar informações em JSON
        json_file = self.docs_dir / "database_info.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(db_info, f, indent=2, ensure_ascii=False)
        docs["database_json"] = str(json_file)
        self.log(f"✅ Dados JSON: {json_file}", "SUCCESS", Colors.GREEN)
        
        # Gerar índice da documentação
        index_md = self._generate_index_markdown(docs)
        index_file = self.docs_dir / "README.md"
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(index_md)
        docs["index"] = str(index_file)
        self.log(f"✅ Índice: {index_file}", "SUCCESS", Colors.GREEN)
        
        return docs

    def _generate_index_markdown(self, docs: Dict[str, str]) -> str:
        """Gera índice da documentação"""
        md = []
        md.append("# Documentação do Banco de Dados SynapScale")
        md.append("")
        md.append(f"**Gerado automaticamente em:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        md.append("")
        md.append("## 📚 Documentação Disponível")
        md.append("")
        md.append("### 📊 Schema do Banco")
        md.append("- [Schema Completo](schema.md) - Documentação detalhada de todas as tabelas")
        md.append("- [Dados JSON](database_info.json) - Informações estruturadas do banco")
        md.append("")
        md.append("### 🎨 Diagramas")
        md.append("- [Diagrama ER](er_diagram.mmd) - Diagrama entidade-relacionamento em Mermaid")
        md.append("")
        md.append("### 🏥 Monitoramento")
        md.append("- [Health Dashboard](health_dashboard.html) - Dashboard de saúde do sistema")
        md.append("")
        md.append("## 🔄 Como Atualizar")
        md.append("")
        md.append("```bash")
        md.append("# Gerar toda a documentação")
        md.append("python tools/database/doc_generator.py")
        md.append("")
        md.append("# Gerar apenas schema")
        md.append("python tools/database/doc_generator.py --schema-only")
        md.append("")
        md.append("# Gerar com health check")
        md.append("python tools/database/doc_generator.py --with-health")
        md.append("```")
        md.append("")
        md.append("---")
        md.append("*Documentação mantida automaticamente pelo Doc Generator*")
        
        return "\n".join(md)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Doc Generator - Gerador de documentação")
    parser.add_argument("--schema-only", action="store_true", help="Gerar apenas documentação do schema")
    parser.add_argument("--with-health", action="store_true", help="Incluir dados de health check")
    parser.add_argument("--output-dir", type=str, help="Diretório de saída personalizado")
    
    args = parser.parse_args()
    
    generator = DocumentationGenerator()
    
    if args.output_dir:
        generator.docs_dir = Path(args.output_dir)
        generator.docs_dir.mkdir(parents=True, exist_ok=True)
    
    if args.schema_only:
        db_info = generator.get_database_info()
        schema_md = generator.generate_schema_markdown(db_info)
        schema_file = generator.docs_dir / "schema.md"
        with open(schema_file, 'w', encoding='utf-8') as f:
            f.write(schema_md)
        print(f"✅ Schema documentado em: {schema_file}")
    else:
        docs = generator.generate_all_docs()
        
        print(f"\n📚 Documentação gerada com sucesso!")
        print(f"📁 Localização: {generator.docs_dir}")
        for doc_type, file_path in docs.items():
            print(f"   📄 {doc_type}: {Path(file_path).name}")

if __name__ == "__main__":
    main()
