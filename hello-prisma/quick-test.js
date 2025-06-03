const { PrismaClient } = require('@prisma/client')

const prisma = new PrismaClient()

async function quickTest() {
  try {
    console.log('🔄 Testando conexão...')
    await prisma.$connect()
    console.log('✅ Conectado ao PostgreSQL!')
    
    // Contar algumas tabelas principais
    const userCount = await prisma.users.count()
    const workspaceCount = await prisma.workspaces.count()
    console.log(`📊 Usuários: ${userCount}`)
    console.log(`📊 Workspaces: ${workspaceCount}`)
    
    console.log('🎉 Migração funcionando perfeitamente!')
    
  } catch (error) {
    console.error('❌ Erro:', error.message)
  } finally {
    await prisma.$disconnect()
  }
}

quickTest()
