#!/usr/bin/env python3
"""
Script para criar um usuário no banco de dados SynapScale
"""
import os
import sys
import uuid
import sqlite3
from datetime import datetime, timezone

# Importar apenas as funções de hash necessárias
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from passlib.context import CryptContext

# Configuração do contexto de criptografia
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configuração do banco de dados
DATABASE_URL = "sqlite:///synapse.db"

def get_password_hash(password: str) -> str:
    """Gera hash da senha para armazenamento seguro."""
    return pwd_context.hash(password)


def create_user(email: str, password: str, first_name: str = None, last_name: str = None):
    """Cria um novo usuário no banco de dados SQLite diretamente via SQL."""
    conn = sqlite3.connect("synapse.db")
    cursor = conn.cursor()
    try:
        # Verificar se o usuário já existe
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        if cursor.fetchone():
            print(f"❌ Erro: Usuário com email '{email}' já existe!")
            return False
        # Gerar hash da senha
        password_hash = get_password_hash(password)
        # Gerar UUID
        user_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        # Inserir usuário
        cursor.execute(
            """
            INSERT INTO users (
                id, email, password_hash, first_name, last_name, is_active, is_verified, role, subscription_plan, preferences, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                email,
                password_hash,
                first_name,
                last_name,
                1,  # is_active
                1,  # is_verified
                "user",
                "free",
                "{}",  # preferences vazio
                now,
                now
            )
        )
        conn.commit()
        print("✅ Usuário criado com sucesso!")
        print(f"   ID: {user_id}")
        print(f"   Email: {email}")
        print(f"   Nome: {first_name or ''} {last_name or ''}")
        print("   Ativo: True")
        print("   Verificado: True")
        print("   Role: user")
        print(f"   Data de criação: {now}")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar usuário: {str(e)}")
        conn.rollback()
        return False
    finally:
        conn.close()

def main():
    """Função principal"""
    print("🚀 Criando usuário no SynapScale Backend")
    print("=" * 50)
    
    # Dados do usuário
    email = "joaovictor@liderimobiliaria.com.br"
    password = "@Jvcm1811"
    first_name = "João Victor"
    last_name = "Lider Imobiliária"
    
    print(f"📧 Email: {email}")
    print(f"👤 Nome: {first_name} {last_name}")
    print(f"🔐 Senha: {'*' * len(password)}")
    print()
    
    # Criar usuário
    success = create_user(
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name
    )
    
    if success:
        print()
        print("🎉 Usuário criado e pronto para usar!")
        print("   Você pode fazer login com esses dados no sistema.")
    else:
        print()
        print("❌ Falha ao criar usuário. Verifique os logs acima.")

if __name__ == "__main__":
    main()
