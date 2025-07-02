#!/usr/bin/env python3
"""
Teste simples de autenticação para verificar se o sistema está funcionando

Updated to use correct authentication methods after cleanup.
"""

import sys
import os
import bcrypt
from datetime import datetime

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from synapse.database import SessionLocal
from synapse.models.user import User


def test_database_connection():
    """Testa conexão com banco de dados"""
    try:
        with SessionLocal() as db:
            result = db.execute("SELECT 1").fetchone()
            return result is not None
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return False


def test_user_authentication():
    """Testa autenticação de usuário usando método correto"""
    try:
        with SessionLocal() as db:
            # Buscar usuário teste
            user = db.query(User).filter(User.email == "admin@synapse.com").first()
            
            if not user:
                print("❌ Usuário admin@synapse.com não encontrado")
                return False
                
            print(f"✅ Usuário encontrado: {user.email}")
            print(f"   ID: {user.id}")
            print(f"   Nome: {user.full_name}")
            print(f"   Ativo: {user.is_active}")
            
            # Testar verificação de senha usando método correto do User
            password = "admin123"
            if user.verify_password(password):
                print(f"✅ Autenticação bem-sucedida para {user.email}")
                return True
            else:
                print(f"❌ Senha incorreta para {user.email}")
                return False
                
    except Exception as e:
        print(f"❌ Erro na autenticação: {e}")
        import traceback
        traceback.print_exc()
        return False


def create_test_user():
    """Cria usuário de teste se não existir"""
    try:
        with SessionLocal() as db:
            # Verificar se já existe
            existing_user = db.query(User).filter(User.email == "admin@synapse.com").first()
            if existing_user:
                print("✅ Usuário de teste já existe")
                return True
                
            # Criar novo usuário
            user = User(
                email="admin@synapse.com",
                username="admin",
                full_name="Admin User",
                is_active=True,
                is_verified=True,
                is_superuser=True,
            )
            
            # Definir senha usando método do modelo
            user.set_password("admin123")
            
            db.add(user)
            db.commit()
            db.refresh(user)
            
            print(f"✅ Usuário de teste criado: {user.email}")
            return True
            
    except Exception as e:
        print(f"❌ Erro ao criar usuário de teste: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Executa todos os testes"""
    print("🧪 TESTE SIMPLES DE AUTENTICAÇÃO")
    print("=" * 50)
    print(f"⏰ Iniciado em: {datetime.now()}")
    
    # 1. Testar conexão
    print("\n1️⃣ Testando conexão com banco de dados...")
    if not test_database_connection():
        print("❌ FALHA: Não foi possível conectar ao banco")
        return False
    print("✅ Conexão com banco OK")
    
    # 2. Criar usuário de teste
    print("\n2️⃣ Criando/verificando usuário de teste...")
    if not create_test_user():
        print("❌ FALHA: Não foi possível criar usuário de teste")
        return False
    
    # 3. Testar autenticação
    print("\n3️⃣ Testando autenticação...")
    if not test_user_authentication():
        print("❌ FALHA: Autenticação não funcionou")
        return False
    
    print("\n🎉 TODOS OS TESTES PASSARAM!")
    print("✅ Sistema de autenticação está funcionando corretamente")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
