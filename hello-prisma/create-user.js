const { PrismaClient } = require('@prisma/client');
const bcrypt = require('bcryptjs');

const prisma = new PrismaClient();

async function createUser() {
  try {
    console.log('🚀 Criando usuário no PostgreSQL...\n');
    
    // Conectar ao banco
    await prisma.$connect();
    console.log('✅ Conectado ao PostgreSQL');
    
    // Email e senha fornecidos
    const email = 'joaovictor@liderimobiliaria.com.br';
    const password = '@Jvcm1811';
    
    // Verificar se o usuário já existe
    const existingUser = await prisma.users.findFirst({
      where: { email: email }
    });
    
    if (existingUser) {
      console.log('⚠️  Usuário já existe! Atualizando senha...');
      
      // Criptografar nova senha
      const hashedPassword = await bcrypt.hash(password, 12);
      
      // Atualizar usuário existente
      const updatedUser = await prisma.users.update({
        where: { id: existingUser.id },
        data: {
          password_hash: hashedPassword,
          is_active: true,
          is_verified: true,
          updated_at: new Date()
        }
      });
      
      console.log('✅ Usuário atualizado com sucesso!');
      console.log(`   ID: ${updatedUser.id}`);
      console.log(`   Email: ${updatedUser.email}`);
      console.log(`   Status: ${updatedUser.is_active ? 'Ativo' : 'Inativo'}`);
      console.log(`   Verificado: ${updatedUser.is_verified ? 'Sim' : 'Não'}`);
      
    } else {
      console.log('📝 Criando novo usuário...');
      
      // Criptografar senha
      const hashedPassword = await bcrypt.hash(password, 12);
      
      // Criar novo usuário
      const newUser = await prisma.users.create({
        data: {
          id: 'user_' + Date.now(),
          email: email,
          password_hash: hashedPassword,
          first_name: 'João Victor',
          last_name: 'Lider Imobiliária',
          is_active: true,
          is_verified: true,
          role: 'admin',
          subscription_plan: 'premium',
          created_at: new Date(),
          updated_at: new Date()
        }
      });
      
      console.log('✅ Usuário criado com sucesso!');
      console.log(`   ID: ${newUser.id}`);
      console.log(`   Email: ${newUser.email}`);
      console.log(`   Nome: ${newUser.first_name} ${newUser.last_name}`);
      console.log(`   Role: ${newUser.role}`);
      console.log(`   Plano: ${newUser.subscription_plan}`);
      console.log(`   Status: ${newUser.is_active ? 'Ativo' : 'Inativo'}`);
      console.log(`   Verificado: ${newUser.is_verified ? 'Sim' : 'Não'}`);
    }
    
    console.log('\n🎉 Processo concluído com sucesso!');
    console.log('🔐 Senha criptografada e armazenada com segurança');
    
  } catch (error) {
    console.error('❌ Erro ao criar usuário:', error);
  } finally {
    await prisma.$disconnect();
  }
}

createUser();
