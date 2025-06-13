#!/usr/bin/env python3
"""
Script para mover tabelas do schema public para synapscale_db
"""

import psycopg2

DATABASE_URL = "postgresql://doadmin:AVNS_DDsc3wHcfGgbX_USTUt@db-banco-dados-automacoes-do-user-13851907-0.e.db.ondigitalocean.com:25060/defaultdb?sslmode=require"

# Tabelas que precisam ser movidas (excluindo as que já existem)
TABLES_TO_MOVE = [
    'user_variables',
    'workflow_executions', 
    'node_executions',
    'execution_queue',
    'execution_metrics',
    'workflow_templates',
    'template_reviews',
    'template_downloads', 
    'template_favorites',
    'template_collections',
    'template_usage',
    'marketplace_components',
    'component_versions',
    'component_ratings',
    'component_downloads',
    'component_purchases',
    'workspaces',
    'workspace_members',
    'workspace_invitations',
    'workspace_activities',
    'workspace_projects',
    'project_collaborators',
    'project_versions',
    'project_comments',
    'workflows',
    'workflow_nodes',
    'workflow_connections',
    'nodes',
    'node_templates',
    'node_categories',
    'conversations',
    'messages',
    'agents',
    'files',
    'analytics_events',
    'analytics_metrics',
    'analytics_reports',
    'analytics_dashboards',
    'analytics_alerts',
    'analytics_exports',
    'user_behavior_metrics',
    'user_insights',
    'business_metrics',
    'system_performance_metrics',
    'custom_reports',
    'report_executions'
]

def move_table(cur, table_name):
    """Move uma tabela do schema public para synapscale_db"""
    try:
        # Verificar se a tabela existe no public
        cur.execute(f"""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = '{table_name}'
            )
        """)
        
        if not cur.fetchone()[0]:
            print(f"   ⚠️  Tabela {table_name} não encontrada no schema public")
            return False
        
        # Verificar se já existe no synapscale_db
        cur.execute(f"""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'synapscale_db' 
                AND table_name = '{table_name}'
            )
        """)
        
        if cur.fetchone()[0]:
            print(f"   ℹ️  Tabela {table_name} já existe no schema synapscale_db")
            return True
        
        # Mover a tabela
        cur.execute(f'ALTER TABLE public."{table_name}" SET SCHEMA synapscale_db')
        print(f"   ✅ Tabela {table_name} movida com sucesso")
        return True
        
    except Exception as e:
        print(f"   ❌ Erro ao mover {table_name}: {e}")
        return False

def main():
    print("🚀 Iniciando migração de tabelas para schema synapscale_db...")
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = True
        cur = conn.cursor()
        
        success_count = 0
        
        for table in TABLES_TO_MOVE:
            print(f"\n🔄 Processando tabela: {table}")
            if move_table(cur, table):
                success_count += 1
        
        print(f"\n🏁 Processo concluído!")
        print(f"✅ {success_count}/{len(TABLES_TO_MOVE)} tabelas processadas com sucesso")
        
        # Verificar resultado final
        cur.execute("""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_schema = 'synapscale_db'
        """)
        
        total_tables = cur.fetchone()[0]
        print(f"📊 Total de tabelas no schema synapscale_db: {total_tables}")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro geral: {e}")

if __name__ == "__main__":
    main()
