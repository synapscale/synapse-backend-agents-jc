#!/usr/bin/env python3
"""
Script para remover completamente a criptografia das user-variables
Atualiza registros existentes no banco de dados
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
from synapse.database import get_db, Base

def fix_encrypted_variables():
    """
    Remove flags de criptografia de todas as variáveis
    """
    
    # Conectar ao banco
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        print("❌ DATABASE_URL não encontrada no .env")
        return False
    
    try:
        engine = create_engine(DATABASE_URL)
        SessionLocal = sessionmaker(bind=engine)
        db = SessionLocal()
        
        print("🔍 Buscando variáveis com is_encrypted=true...")
        
        # Buscar todas as variáveis marcadas como encrypted
        encrypted_vars = db.query(UserVariable).filter(
            UserVariable.is_encrypted == True
        ).all()
        
        print(f"📊 Encontradas {len(encrypted_vars)} variáveis marcadas como criptografadas")
        
        if len(encrypted_vars) == 0:
            print("✅ Nenhuma variável criptografada encontrada!")
            return True
        
        # Mostrar algumas para confirmar
        print("\n📋 Primeiras 5 variáveis encontradas:")
        for i, var in enumerate(encrypted_vars[:5]):
            print(f"   {i+1}. {var.key} = {var.value[:20]}{'...' if len(var.value) > 20 else ''}")
        
        # Confirmar antes de atualizar
        resposta = input(f"\n🔧 Deseja atualizar todas as {len(encrypted_vars)} variáveis para is_encrypted=false? (s/N): ")
        
        if resposta.lower() != 's':
            print("❌ Operação cancelada pelo usuário")
            return False
        
        # Atualizar todas as variáveis
        print("🔄 Atualizando variáveis...")
        
        count = 0
        for var in encrypted_vars:
            var.is_encrypted = False
            count += 1
            
            if count % 10 == 0:
                print(f"   Processadas {count}/{len(encrypted_vars)} variáveis...")
        
        # Salvar mudanças
        db.commit()
        
        print(f"✅ {count} variáveis atualizadas com sucesso!")
        print("✅ Todas as variáveis agora estão marcadas como is_encrypted=false")
        
        # Verificação final
        remaining = db.query(UserVariable).filter(
            UserVariable.is_encrypted == True
        ).count()
        
        if remaining == 0:
            print("🎉 CRIPTOGRAFIA COMPLETAMENTE REMOVIDA!")
            print("🎉 Todas as variáveis agora são armazenadas em texto claro")
        else:
            print(f"⚠️  Ainda restam {remaining} variáveis marcadas como criptografadas")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro ao conectar no banco: {e}")
        return False

def show_current_status():
    """
    Mostra o status atual das variáveis
    """
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        print("❌ DATABASE_URL não encontrada no .env")
        return
    
    try:
        engine = create_engine(DATABASE_URL)
        SessionLocal = sessionmaker(bind=engine)
        db = SessionLocal()
        
        # Contar variáveis
        total = db.query(UserVariable).count()
        encrypted = db.query(UserVariable).filter(UserVariable.is_encrypted == True).count()
        not_encrypted = total - encrypted
        
        print("📊 STATUS ATUAL DAS VARIÁVEIS:")
        print(f"   Total de variáveis: {total}")
        print(f"   Marcadas como criptografadas: {encrypted}")
        print(f"   Marcadas como não criptografadas: {not_encrypted}")
        
        if encrypted > 0:
            print(f"⚠️  {encrypted} variáveis ainda marcadas como criptografadas")
        else:
            print("✅ Nenhuma variável marcada como criptografada")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Erro ao conectar no banco: {e}")

if __name__ == "__main__":
    print("🚀 FERRAMENTA DE REMOÇÃO DE CRIPTOGRAFIA - SYNAPSCALE")
    print("=" * 60)
    
    # Mostrar status atual
    show_current_status()
    
    print("\nOpções:")
    print("1. Remover criptografia de todas as variáveis")
    print("2. Apenas mostrar status atual")
    print("3. Sair")
    
    choice = input("\nEscolha uma opção (1-3): ").strip()
    
    if choice == "1":
        print("\n🔧 REMOVENDO CRIPTOGRAFIA...")
        print("=" * 40)
        if fix_encrypted_variables():
            print("\n🎉 PROCESSO CONCLUÍDO COM SUCESSO!")
        else:
            print("\n❌ PROCESSO FALHOU!")
            
    elif choice == "2":
        print("\n📊 STATUS ATUAL:")
        print("=" * 30)
        show_current_status()
        
    elif choice == "3":
        print("👋 Até logo!")
        
    else:
        print("❌ Opção inválida!") 