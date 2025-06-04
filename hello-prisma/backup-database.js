const { PrismaClient } = require('@prisma/client')
const fs = require('fs')
const path = require('path')

const prisma = new PrismaClient()

async function backupDatabase() {
  const backupDir = path.join(__dirname, 'backups')
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-')
  
  if (!fs.existsSync(backupDir)) {
    fs.mkdirSync(backupDir, { recursive: true })
  }

  console.log('🔄 Iniciando backup completo do banco de dados...')

  try {
    // Obter lista de todas as tabelas
    const tables = await prisma.$queryRaw`
      SELECT table_name 
      FROM information_schema.tables 
      WHERE table_schema = 'public' 
      AND table_type = 'BASE TABLE'
      AND table_name != '_prisma_migrations'
    `

    console.log(`📊 Encontradas ${tables.length} tabelas para backup`)

    const backupData = {
      timestamp: new Date().toISOString(),
      tables: {}
    }

    for (const tableInfo of tables) {
      const tableName = tableInfo.table_name
      try {
        console.log(`📋 Fazendo backup da tabela: ${tableName}`)
        
        const data = await prisma.$queryRawUnsafe(`SELECT * FROM "${tableName}"`)
        backupData.tables[tableName] = data
        
        console.log(`✅ ${tableName}: ${data.length} registros salvos`)
        
      } catch (error) {
        console.log(`⚠️  Erro na tabela ${tableName}: ${error.message}`)
        backupData.tables[tableName] = { error: error.message }
      }
    }

    // Salvar backup completo
    const backupFile = path.join(backupDir, `complete_backup_${timestamp}.json`)
    fs.writeFileSync(backupFile, JSON.stringify(backupData, null, 2))
    
    console.log(`\n🎉 Backup completo salvo em: ${backupFile}`)
    console.log(`📈 Total de tabelas: ${tables.length}`)
    
    // Criar resumo
    const summary = {
      timestamp: new Date().toISOString(),
      totalTables: tables.length,
      tablesWithData: Object.keys(backupData.tables).filter(t => 
        Array.isArray(backupData.tables[t]) && backupData.tables[t].length > 0
      ).length,
      tablesWithErrors: Object.keys(backupData.tables).filter(t => 
        backupData.tables[t].error
      ).length
    }
    
    fs.writeFileSync(
      path.join(backupDir, `backup_summary_${timestamp}.json`), 
      JSON.stringify(summary, null, 2)
    )
    
    console.log(`📋 Resumo salvo: backup_summary_${timestamp}.json`)
    
  } catch (error) {
    console.error('❌ Erro durante o backup:', error)
  } finally {
    await prisma.$disconnect()
  }
}

backupDatabase()
