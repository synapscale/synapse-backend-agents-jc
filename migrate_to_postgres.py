#!/usr/bin/env python3
"""
Script para migrar o schema SQLite para PostgreSQL
"""

import sqlite3
import os

def create_postgres_schema():
    """Cria um schema Prisma para PostgreSQL"""
    
    # Lista das tabelas principais que obtivemos
    tables = [
        'agents', 'alembic_version', 'analytics_alerts', 'analytics_dashboards', 
        'analytics_events', 'analytics_exports', 'analytics_metrics', 'analytics_reports',
        'business_metrics', 'component_downloads', 'component_favorites', 'component_purchases',
        'component_ratings', 'component_versions', 'conversations', 'custom_reports',
        'email_verification_tokens', 'execution_metrics', 'execution_queue', 'files',
        'marketplace_components', 'messages', 'node_categories', 'node_executions',
        'node_templates', 'nodes', 'password_reset_tokens', 'project_collaborators',
        'project_comments', 'project_versions', 'refresh_tokens', 'report_executions',
        'system_performance_metrics', 'template_collections', 'template_downloads',
        'template_favorites', 'template_reviews', 'template_usage', 'user_behavior_metrics',
        'user_insights', 'user_variables', 'users', 'workflow_connections',
        'workflow_executions', 'workflow_nodes', 'workflow_templates', 'workflows',
        'workspace_activities', 'workspace_invitations', 'workspace_members',
        'workspace_projects', 'workspaces'
    ]
    
    print(f"Preparando schema para {len(tables)} tabelas...")
    
    # Conectar ao SQLite para obter estrutura
    conn = sqlite3.connect('/workspaces/synapse-backend-agents-jc/synapse.db')
    cursor = conn.cursor()
    
    # Schema base para PostgreSQL
    schema = '''// Prisma schema para SynapScale - PostgreSQL
// Migrado de SQLite

generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

'''
    
    # Modelos essenciais primeiro (versão simplificada para teste)
    schema += '''
// === CORE MODELS ===

model users {
  id                    Int       @id @default(autoincrement())
  email                 String    @unique
  username              String?   @unique
  password_hash         String
  full_name             String?
  is_active             Boolean   @default(true)
  is_verified           Boolean   @default(false)
  created_at            DateTime  @default(now())
  updated_at            DateTime  @updatedAt
  last_login            DateTime?
  
  // Relations
  conversations         conversations[]
  messages              messages[]
  workspaces            workspace_members[]
  files                 files[]
  agents                agents[]
}

model conversations {
  id                    Int       @id @default(autoincrement())
  user_id               Int
  title                 String?
  created_at            DateTime  @default(now())
  updated_at            DateTime  @updatedAt
  is_active             Boolean   @default(true)
  
  // Relations
  user                  users     @relation(fields: [user_id], references: [id])
  messages              messages[]
}

model messages {
  id                    Int       @id @default(autoincrement())
  conversation_id       Int
  user_id               Int
  content               String
  message_type          String    @default("user")
  created_at            DateTime  @default(now())
  updated_at            DateTime  @updatedAt
  
  // Relations
  conversation          conversations @relation(fields: [conversation_id], references: [id])
  user                  users     @relation(fields: [user_id], references: [id])
}

model agents {
  id                    Int       @id @default(autoincrement())
  user_id               Int
  name                  String
  description           String?
  configuration         String?   // JSON
  is_active             Boolean   @default(true)
  created_at            DateTime  @default(now())
  updated_at            DateTime  @updatedAt
  
  // Relations
  user                  users     @relation(fields: [user_id], references: [id])
}

model workspaces {
  id                    Int       @id @default(autoincrement())
  name                  String
  description           String?
  created_at            DateTime  @default(now())
  updated_at            DateTime  @updatedAt
  is_active             Boolean   @default(true)
  
  // Relations
  members               workspace_members[]
  projects              workspace_projects[]
}

model workspace_members {
  id                    Int       @id @default(autoincrement())
  workspace_id          Int
  user_id               Int
  role                  String    @default("member")
  joined_at             DateTime  @default(now())
  
  // Relations
  workspace             workspaces @relation(fields: [workspace_id], references: [id])
  user                  users     @relation(fields: [user_id], references: [id])
  
  @@unique([workspace_id, user_id])
}

model workspace_projects {
  id                    Int       @id @default(autoincrement())
  workspace_id          Int
  name                  String
  description           String?
  created_at            DateTime  @default(now())
  updated_at            DateTime  @updatedAt
  
  // Relations
  workspace             workspaces @relation(fields: [workspace_id], references: [id])
}

model files {
  id                    Int       @id @default(autoincrement())
  user_id               Int
  filename              String
  file_path             String
  file_size             Int?
  mime_type             String?
  created_at            DateTime  @default(now())
  
  // Relations
  user                  users     @relation(fields: [user_id], references: [id])
}

model workflows {
  id                    Int       @id @default(autoincrement())
  name                  String
  description           String?
  configuration         String?   // JSON
  is_active             Boolean   @default(true)
  created_at            DateTime  @default(now())
  updated_at            DateTime  @updatedAt
  
  // Relations
  executions            workflow_executions[]
  nodes                 workflow_nodes[]
}

model workflow_executions {
  id                    Int       @id @default(autoincrement())
  workflow_id           Int
  status                String    @default("pending")
  started_at            DateTime  @default(now())
  completed_at          DateTime?
  result                String?   // JSON
  
  // Relations
  workflow              workflows @relation(fields: [workflow_id], references: [id])
}

model workflow_nodes {
  id                    Int       @id @default(autoincrement())
  workflow_id           Int
  node_type             String
  configuration         String?   // JSON
  position_x            Float?
  position_y            Float?
  
  // Relations
  workflow              workflows @relation(fields: [workflow_id], references: [id])
}

model refresh_tokens {
  id                    Int       @id @default(autoincrement())
  user_id               Int
  token                 String    @unique
  expires_at            DateTime
  created_at            DateTime  @default(now())
  is_revoked            Boolean   @default(false)
}

model email_verification_tokens {
  id                    Int       @id @default(autoincrement())
  user_id               Int
  token                 String    @unique
  expires_at            DateTime
  created_at            DateTime  @default(now())
  is_used               Boolean   @default(false)
}

model password_reset_tokens {
  id                    Int       @id @default(autoincrement())
  user_id               Int
  token                 String    @unique
  expires_at            DateTime
  created_at            DateTime  @default(now())
  is_used               Boolean   @default(false)
}
'''
    
    conn.close()
    
    # Salvar no hello-prisma
    schema_path = '/workspaces/synapse-backend-agents-jc/hello-prisma/prisma/schema.prisma'
    with open(schema_path, 'w') as f:
        f.write(schema)
    
    print(f"✅ Schema PostgreSQL criado!")
    print(f"📁 Salvo em: {schema_path}")
    
    return len([line for line in schema.split('\n') if 'model ' in line])

if __name__ == "__main__":
    count = create_postgres_schema()
    print(f"\n🎉 Schema PostgreSQL com {count} modelos principais criado!")
    print("\n📋 Próximos passos:")
    print("1. Aplicar migração no PostgreSQL")
    print("2. Testar conexão")
    print("3. Migrar dados do SQLite")
