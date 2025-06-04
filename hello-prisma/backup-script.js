const { PrismaClient } = require('@prisma/client')
const fs = require('fs')
const path = require('path')

const prisma = new PrismaClient()

async function backupAllTables() {
  const backupDir = path.join(__dirname, 'backups')
  
  if (!fs.existsSync(backupDir)) {
    fs.mkdirSync(backupDir, { recursive: true })
  }

  console.log('Iniciando backup das tabelas...')

  try {
    // Lista de todas as tabelas que você mencionou
    const tables = [
      'users', 'workspaces', 'workspace_members', 'workspace_invitations',
      'workspace_activities', 'workspace_projects', 'project_collaborators',
      'project_comments', 'project_versions', 'workflows', 'workflow_executions',
      'workflow_connections', 'workflow_nodes', 'workflow_templates',
      'nodes', 'node_executions', 'node_templates', 'node_categories',
      'agents', 'conversations', 'messages', 'files', 'execution_queue',
      'execution_metrics', 'user_variables', 'refresh_tokens',
      'email_verification_tokens', 'password_reset_tokens',
      'marketplace_components', 'component_versions', 'component_downloads',
      'component_purchases', 'component_ratings', 'component_favorites',
      'template_collections', 'template_downloads', 'template_favorites',
      'template_reviews', 'template_usage', 'analytics_events',
      'analytics_metrics', 'analytics_reports', 'analytics_dashboards',
      'analytics_alerts', 'analytics_exports', 'business_metrics',
      'user_behavior_metrics', 'user_insights', 'system_performance_metrics',
      'custom_reports', 'report_executions'
    ]

    for (const table of tables) {
      try {
        // Usar raw query para obter dados
        const data = await prisma.$queryRawUnsafe(`SELECT * FROM "${table}"`)
        
        const filename = path.join(backupDir, `${table}_backup.json`)
        fs.writeFileSync(filename, JSON.stringify(data, null, 2))
        
        console.log(`✓ Backup da tabela ${table} salvo em ${filename}`)
      } catch (error) {
        console.log(`⚠ Erro ao fazer backup da tabela ${table}: ${error.message}`)
      }
    }

    console.log('Backup concluído!')
    
  } catch (error) {
    console.error('Erro durante o backup:', error)
  } finally {
    await prisma.$disconnect()
  }
}

backupAllTables()
