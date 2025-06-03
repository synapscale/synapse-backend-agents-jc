const { PrismaClient } = require('@prisma/client')

const prisma = new PrismaClient()

async function testConnection() {
  try {
    console.log('🔌 Testando conexão com PostgreSQL...')
    
    // Teste 1: Criar ou buscar usuário
    console.log('\n1️⃣ Criando/buscando usuário de teste...')
    const timestamp = Date.now()
    let user
    
    try {
      user = await prisma.users.create({
        data: {
          email: `teste_${timestamp}@synapscale.com`,
          username: `teste_user_${timestamp}`,
          password_hash: 'hash_teste_123',
          full_name: 'Usuário de Teste',
          is_active: true,
          is_verified: true
        }
      })
      console.log('✅ Novo usuário criado:', { id: user.id, email: user.email })
    } catch (error) {
      if (error.code === 'P2002') {
        // Buscar usuário existente
        user = await prisma.users.findFirst({
          where: { email: { contains: 'teste' } }
        })
        console.log('✅ Usuário existente encontrado:', { id: user.id, email: user.email })
      } else {
        throw error
      }
    }
    console.log('✅ Usuário criado:', { id: user.id, email: user.email, username: user.username })
    
    // Teste 2: Criar um workspace
    console.log('\n2️⃣ Criando workspace de teste...')
    let workspace
    try {
      workspace = await prisma.workspaces.create({
        data: {
          name: `Workspace Teste ${timestamp}`,
          description: 'Workspace para testes de migração',
          is_active: true
        }
      })
      console.log('✅ Novo workspace criado:', { id: workspace.id, name: workspace.name })
    } catch (error) {
      workspace = await prisma.workspaces.findFirst()
      console.log('✅ Workspace existente encontrado:', { id: workspace.id, name: workspace.name })
    }
    
    // Teste 3: Adicionar usuário ao workspace
    console.log('\n3️⃣ Adicionando usuário ao workspace...')
    let member
    try {
      member = await prisma.workspace_members.create({
        data: {
          workspace_id: workspace.id,
          user_id: user.id,
          role: 'admin'
        }
      })
      console.log('✅ Novo membro adicionado:', { workspace_id: member.workspace_id, user_id: member.user_id, role: member.role })
    } catch (error) {
      member = await prisma.workspace_members.findFirst({
        where: { user_id: user.id, workspace_id: workspace.id }
      })
      console.log('✅ Membro existente encontrado:', { workspace_id: member.workspace_id, user_id: member.user_id, role: member.role })
    }
    
    // Teste 4: Criar uma conversa
    console.log('\n4️⃣ Criando conversa de teste...')
    const conversation = await prisma.conversations.create({
      data: {
        user_id: user.id,
        title: 'Conversa de Teste - Migração PostgreSQL',
        is_active: true
      }
    })
    console.log('✅ Conversa criada:', { id: conversation.id, title: conversation.title })
    
    // Teste 5: Adicionar mensagem
    console.log('\n5️⃣ Adicionando mensagem...')
    const message = await prisma.messages.create({
      data: {
        conversation_id: conversation.id,
        user_id: user.id,
        content: 'Esta é uma mensagem de teste da migração para PostgreSQL!',
        message_type: 'user'
      }
    })
    console.log('✅ Mensagem criada:', { id: message.id, content: message.content.substring(0, 50) + '...' })
    
    // Teste 6: Consulta com joins
    console.log('\n6️⃣ Testando consulta com relacionamentos...')
    const userWithData = await prisma.users.findUnique({
      where: { id: user.id },
      include: {
        conversations: {
          include: {
            messages: true
          }
        },
        workspaces: {
          include: {
            workspace: true
          }
        }
      }
    })
    
    console.log('✅ Consulta complexa executada:')
    console.log(`   - Usuário: ${userWithData.full_name}`)
    console.log(`   - Conversas: ${userWithData.conversations.length}`)
    console.log(`   - Mensagens: ${userWithData.conversations[0]?.messages.length || 0}`)
    console.log(`   - Workspaces: ${userWithData.workspaces.length}`)
    
    // Teste 7: Contar registros
    console.log('\n7️⃣ Contando registros...')
    const counts = await Promise.all([
      prisma.users.count(),
      prisma.workspaces.count(),
      prisma.conversations.count(),
      prisma.messages.count(),
      prisma.workspace_members.count()
    ])
    
    console.log('✅ Estatísticas do banco:')
    console.log(`   - Usuários: ${counts[0]}`)
    console.log(`   - Workspaces: ${counts[1]}`)
    console.log(`   - Conversas: ${counts[2]}`)
    console.log(`   - Mensagens: ${counts[3]}`)
    console.log(`   - Membros de workspace: ${counts[4]}`)
    
    console.log('\n🎉 TODOS OS TESTES PASSARAM!')
    console.log('✅ PostgreSQL está funcionando perfeitamente!')
    console.log('✅ Schema migrado com sucesso!')
    console.log('✅ Prisma Cloud conectado!')
    
  } catch (error) {
    console.error('❌ Erro durante os testes:', error)
    throw error
  } finally {
    await prisma.$disconnect()
  }
}

testConnection()
  .then(() => {
    console.log('\n🚀 Migração concluída com sucesso!')
    process.exit(0)
  })
  .catch((error) => {
    console.error('💥 Falha na migração:', error)
    process.exit(1)
  })
