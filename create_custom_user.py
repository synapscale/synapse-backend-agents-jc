#!/usr/bin/env python3
"""
Script para criar usuário personalizado no sistema SynapScale
Email: joaovictor@liderimobiliaria.com.br
Senha: @Teste123
"""
import psycopg2
import uuid
from datetime import datetime
import bcrypt
import os
from dotenv import load_dotenv

load_dotenv()

def create_custom_user():
    """Criar usuário personalizado no sistema"""
    
    print("🚀 Criando usuário personalizado no sistema SynapScale...")
    
    # Dados do usuário personalizado
    user_data = {
        'email': 'joaovictor@liderimobiliaria.com.br',
        'username': 'joaovictor',
        'full_name': 'João Victor - Líder Imobiliária',
        'password': '@Teste123'
    }
    
    # URL do banco de dados - obtida do .env
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    # Separar componentes da URL para psycopg2
    import urllib.parse
    parsed = urllib.parse.urlparse(DATABASE_URL)
    
    config = {
        'host': parsed.hostname,
        'port': parsed.port,
        'database': parsed.path[1:],  # remove the leading /
        'user': parsed.username,
        'password': parsed.password,
        'sslmode': 'require'
    }
    
    try:
        # Conectar ao banco
        conn = psycopg2.connect(**config)
        cursor = conn.cursor()
        
        print("✅ Conectado ao banco DigitalOcean")
        
        # Gerar hash da senha usando bcrypt
        password_bytes = user_data['password'].encode('utf-8')
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password_bytes, salt).decode('utf-8')
        
        # Gerar UUID para o usuário
        user_id = str(uuid.uuid4())
        
        # Verificar se usuário já existe
        cursor.execute(
            "SELECT id FROM synapscale_db.users WHERE email = %s OR username = %s",
            (user_data['email'], user_data['username'])
        )
        existing_user = cursor.fetchone()
        
        if existing_user:
            print(f"⚠️  Usuário já existe com ID: {existing_user[0]}")
            print(f"📧 Email: {user_data['email']}")
            print(f"👤 Username: {user_data['username']}")
            cursor.close()
            conn.close()
            return existing_user[0]
        
        # Inserir usuário na tabela correta
        insert_query = """
            INSERT INTO synapscale_db.users 
            (id, email, username, full_name, hashed_password, is_active, is_superuser, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
        """
        
        now = datetime.utcnow()
        cursor.execute(insert_query, (
            user_id,
            user_data['email'],
            user_data['username'], 
            user_data['full_name'],
            hashed_password,
            True,  # is_active
            False,  # is_superuser (usuário normal)
            now,   # created_at
            now    # updated_at
        ))
        
        inserted_id = cursor.fetchone()[0]
        
        # Confirmar transação
        conn.commit()
        
        print(f"✅ Usuário criado com sucesso!")
        print(f"📧 Email: {user_data['email']}")
        print(f"👤 Username: {user_data['username']}")
        print(f"👥 Nome: {user_data['full_name']}")
        print(f"🆔 ID: {inserted_id}")
        print(f"🔐 Senha: {user_data['password']}")
        
        # Verificar se foi realmente criado
        cursor.execute("SELECT COUNT(*) FROM synapscale_db.users;")
        total_users = cursor.fetchone()[0]
        print(f"📊 Total de usuários na base: {total_users}")
        
        # Salvar credenciais em arquivo
        filename = f"usuario_{user_data['username']}_credenciais.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"🎯 Credenciais do Usuário SynapScale\n")
            f.write(f"=======================================\n\n")
            f.write(f"📧 Email: {user_data['email']}\n")
            f.write(f"👤 Username: {user_data['username']}\n")
            f.write(f"👥 Nome: {user_data['full_name']}\n")
            f.write(f"🔐 Senha: {user_data['password']}\n")
            f.write(f"🆔 ID: {inserted_id}\n")
            f.write(f"📅 Criado em: {now}\n\n")
            f.write(f"🔗 Para fazer login via API:\n")
            f.write(f"POST http://localhost:8000/api/v1/auth/login\n")
            f.write(f"Content-Type: application/json\n\n")
            f.write(f'{{\n')
            f.write(f'  "username": "{user_data["email"]}",\n')
            f.write(f'  "password": "{user_data["password"]}"\n')
            f.write(f'}}\n')
        
        print(f"💾 Credenciais salvas em: {filename}")
        
        cursor.close()
        conn.close()
        
        return inserted_id
        
    except psycopg2.Error as e:
        print(f"❌ Erro do PostgreSQL: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
        return None
    except Exception as e:
        print(f"❌ Erro inesperado: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
        return None

def test_user_login():
    """Testa se conseguimos verificar a senha do usuário criado"""
    try:
        # URL do banco de dados - obtida do .env
        DATABASE_URL = os.getenv("DATABASE_URL")
        
        # Separar componentes da URL para psycopg2
        import urllib.parse
        parsed = urllib.parse.urlparse(DATABASE_URL)
        
        config = {
            'host': parsed.hostname,
            'port': parsed.port,
            'database': parsed.path[1:],  # remove the leading /
            'user': parsed.username,
            'password': parsed.password,
            'sslmode': 'require'
        }
        
        conn = psycopg2.connect(**config)
        cursor = conn.cursor()
        
        # Buscar o usuário criado
        cursor.execute(
            "SELECT id, email, username, hashed_password FROM synapscale_db.users WHERE email = %s",
            ('joaovictor@liderimobiliaria.com.br',)
        )
        user = cursor.fetchone()
        
        if user:
            user_id, email, username, stored_hash = user
            test_password = '@Teste123'
            
            # Verificar senha com bcrypt
            if bcrypt.checkpw(test_password.encode('utf-8'), stored_hash.encode('utf-8')):
                print(f"✅ Teste de login bem-sucedido!")
                print(f"👤 Usuário: {username} ({email})")
                print(f"🆔 ID: {user_id}")
            else:
                print(f"❌ Senha não confere!")
        else:
            print(f"❌ Usuário não encontrado!")
            
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro no teste de login: {str(e)}")

if __name__ == "__main__":
    print("🎯 Criador de Usuário Personalizado - SynapScale")
    print("=" * 55)
    print(f"📧 Email: joaovictor@liderimobiliaria.com.br")
    print(f"🔐 Senha: @Teste123")
    print()
    
    # Criar usuário
    user_id = create_custom_user()
    
    if user_id:
        print(f"\n🧪 Testando login...")
        test_user_login()
        
        print(f"\n🎉 Usuário criado e testado com sucesso!")
        print(f"\n📝 Como usar:")
        print(f"1. Inicie o servidor: python -m uvicorn src.synapse.main:app --host 0.0.0.0 --port 8000")
        print(f"2. Faça login via API em: http://localhost:8000/api/v1/auth/login")
        print(f"3. Use o email: joaovictor@liderimobiliaria.com.br")
        print(f"4. Use a senha: @Teste123")
    else:
        print(f"\n❌ Falha na criação do usuário")
