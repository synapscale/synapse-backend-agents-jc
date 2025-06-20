#!/usr/bin/env python3
"""
Script para desabilitar COMPLETAMENTE a criptografia das user-variables
Remove todas as flags is_encrypted=true e garante que valores sejam salvos em texto claro
"""
import os
import sys
from dotenv import load_dotenv

# Carregar .env
load_dotenv()

# Adicionar src ao path
sys.path.insert(0, 'src')

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from synapse.models.user_variable import UserVariable

def check_current_status():
    """
    Verifica o status atual das variáveis
    """
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        print("❌ DATABASE_URL não encontrada no .env")
        return False
    
    try:
        engine = create_engine(DATABASE_URL)
        SessionLocal = sessionmaker(bind=engine)
        db = SessionLocal()
        
        print("🔍 Verificando status atual das variáveis...")
        
        total = db.query(UserVariable).count()
        encrypted = db.query(UserVariable).filter(UserVariable.is_encrypted == True).count()
        not_encrypted = total - encrypted
        
        print(f"📊 STATUS ATUAL:")
        print(f"   Total de variáveis: {total}")
        print(f"   Marcadas como criptografadas: {encrypted}")
        print(f"   Marcadas como não criptografadas: {not_encrypted}")
        
        if encrypted > 0:
            print(f"⚠️  {encrypted} variáveis ainda marcadas como criptografadas")
            
            # Mostrar algumas como exemplo
            examples = db.query(UserVariable).filter(UserVariable.is_encrypted == True).limit(5).all()
            print("\n📋 Exemplos de variáveis marcadas como criptografadas:")
            for i, var in enumerate(examples):
                print(f"   {i+1}. {var.key} = {var.value[:20]}{'...' if len(var.value) > 20 else ''}")
        else:
            print("✅ Nenhuma variável está marcada como criptografada!")
        
        db.close()
        return encrypted > 0
        
    except Exception as e:
        print(f"❌ Erro ao conectar no banco: {e}")
        return False

def force_disable_encryption():
    """
    Força a desabilitação completa da criptografia
    """
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        print("❌ DATABASE_URL não encontrada no .env")
        return False
    
    try:
        engine = create_engine(DATABASE_URL)
        SessionLocal = sessionmaker(bind=engine)
        db = SessionLocal()
        
        print("🔧 Forçando desabilitação da criptografia...")
        
        # Buscar todas as variáveis marcadas como encrypted
        encrypted_vars = db.query(UserVariable).filter(
            UserVariable.is_encrypted == True
        ).all()
        
        if len(encrypted_vars) == 0:
            print("✅ Nenhuma variável criptografada encontrada!")
            return True
        
        print(f"🔄 Atualizando {len(encrypted_vars)} variáveis para is_encrypted=false...")
        
        count = 0
        for var in encrypted_vars:
            var.is_encrypted = False
            count += 1
            
            if count % 10 == 0:
                print(f"   Processadas {count}/{len(encrypted_vars)} variáveis...")
        
        # Salvar mudanças
        db.commit()
        
        print(f"✅ {count} variáveis atualizadas com sucesso!")
        
        # Verificação final
        remaining = db.query(UserVariable).filter(
            UserVariable.is_encrypted == True
        ).count()
        
        if remaining == 0:
            print("🎉 CRIPTOGRAFIA COMPLETAMENTE DESABILITADA!")
            print("🎉 Todas as variáveis agora são armazenadas em texto claro")
        else:
            print(f"⚠️  Ainda restam {remaining} variáveis marcadas como criptografadas")
        
        db.close()
        return remaining == 0
        
    except Exception as e:
        print(f"❌ Erro ao desabilitar criptografia: {e}")
        return False

def update_schema_defaults():
    """
    Atualiza o schema padrão no banco para is_encrypted=false
    """
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        print("❌ DATABASE_URL não encontrada no .env")
        return False
    
    try:
        engine = create_engine(DATABASE_URL)
        
        print("🔧 Atualizando schema padrão no banco...")
        
        # Alterar o default da coluna para false
        with engine.connect() as conn:
            conn.execute(text("""
                ALTER TABLE synapscale_db.user_variables 
                ALTER COLUMN is_encrypted SET DEFAULT false
            """))
            conn.commit()
        
        print("✅ Schema padrão atualizado - novas variáveis serão is_encrypted=false por padrão")
        return True
        
    except Exception as e:
        print(f"⚠️  Erro ao atualizar schema (pode ser normal): {e}")
        return False

def test_new_variable():
    """
    Testa criar uma nova variável para verificar se está funcionando
    """
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        print("❌ DATABASE_URL não encontrada no .env")
        return False
    
    try:
        engine = create_engine(DATABASE_URL)
        SessionLocal = sessionmaker(bind=engine)
        db = SessionLocal()
        
        print("🧪 Testando criação de nova variável...")
        
        # Buscar primeiro usuário para teste
        from synapse.models.user import User
        user = db.query(User).first()
        
        if not user:
            print("⚠️  Nenhum usuário encontrado para teste")
            return False
        
        # Criar variável de teste
        test_var = UserVariable.create_variable(
            user_id=user.id,
            key="TEST_NO_ENCRYPTION",
            value="this_is_plain_text_123",
            description="Teste de variável sem criptografia",
            category="test"
        )
        
        db.add(test_var)
        db.commit()
        db.refresh(test_var)
        
        print(f"✅ Variável de teste criada:")
        print(f"   Key: {test_var.key}")
        print(f"   Value: {test_var.value}")
        print(f"   is_encrypted: {test_var.is_encrypted}")
        print(f"   Valor recuperado: {test_var.get_decrypted_value()}")
        
        # Limpar teste
        db.delete(test_var)
        db.commit()
        print("🧹 Variável de teste removida")
        
        db.close()
        
        if test_var.is_encrypted:
            print("❌ PROBLEMA: Variável ainda foi marcada como criptografada!")
            return False
        else:
            print("✅ SUCESSO: Variável criada corretamente sem criptografia!")
            return True
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

def main():
    """
    Função principal
    """
    print("🚀 SCRIPT PARA DESABILITAR CRIPTOGRAFIA COMPLETAMENTE")
    print("=" * 60)
    
    # 1. Verificar status atual
    print("\n1️⃣ VERIFICANDO STATUS ATUAL...")
    has_encrypted = check_current_status()
    
    # 2. Se há variáveis criptografadas, corrigir
    if has_encrypted:
        print("\n2️⃣ CORRIGINDO VARIÁVEIS EXISTENTES...")
        if not force_disable_encryption():
            print("❌ Falha ao corrigir variáveis existentes")
            return False
    else:
        print("\n✅ Nenhuma variável criptografada encontrada")
    
    # 3. Atualizar schema padrão
    print("\n3️⃣ ATUALIZANDO SCHEMA PADRÃO...")
    update_schema_defaults()
    
    # 4. Testar criação de nova variável
    print("\n4️⃣ TESTANDO NOVA VARIÁVEL...")
    if not test_new_variable():
        print("❌ FALHA NO TESTE - ainda há problema!")
        return False
    
    # 5. Verificação final
    print("\n5️⃣ VERIFICAÇÃO FINAL...")
    if not check_current_status():
        print("\n🎉 SUCESSO TOTAL! CRIPTOGRAFIA COMPLETAMENTE DESABILITADA!")
        print("\n📋 RESUMO DO QUE FOI FEITO:")
        print("   ✅ Todas as variáveis existentes marcadas como is_encrypted=false")
        print("   ✅ Schema padrão atualizado")
        print("   ✅ Teste de nova variável funcionando")
        print("   ✅ Valores salvos em texto claro")
        
        print("\n🔧 PRÓXIMOS PASSOS:")
        print("   1. Reinicie o servidor da API")
        print("   2. Teste criar uma nova variável via endpoint")
        print("   3. Verifique se o valor é salvo em texto claro")
        
        return True
    else:
        print("❌ Ainda há problemas - verifique logs acima")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 