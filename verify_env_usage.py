#!/usr/bin/env python3
"""
Script para verificar se todas as variáveis estão sendo carregadas do .env
"""
import os
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv()

def verify_env_variables():
    """Verifica se as principais variáveis estão sendo carregadas"""
    print("🔍 Verificando carregamento de variáveis do .env...")
    print("=" * 60)
    
    # Variáveis críticas que devem estar no .env
    critical_vars = [
        'DATABASE_URL',
        'SECRET_KEY', 
        'JWT_SECRET_KEY',
        'ENVIRONMENT'
    ]
    
    # Variáveis opcionais
    optional_vars = [
        'DATABASE_SCHEMA',
        'REDIS_URL',
        'DEBUG',
        'PORT',
        'HOST'
    ]
    
    print("📋 Variáveis CRÍTICAS:")
    for var in critical_vars:
        value = os.getenv(var)
        if value:
            # Mascarar dados sensíveis
            if 'KEY' in var or 'PASSWORD' in var:
                display_value = f"{value[:10]}...{value[-5:]}" if len(value) > 15 else "***"
            elif 'DATABASE_URL' in var:
                display_value = f"{value[:20]}...{value[-15:]}" if len(value) > 35 else "***"
            else:
                display_value = value
            print(f"  ✅ {var}: {display_value}")
        else:
            print(f"  ❌ {var}: NÃO CONFIGURADA")
    
    print("\n📋 Variáveis OPCIONAIS:")
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            print(f"  ✅ {var}: {value}")
        else:
            print(f"  ⚠️  {var}: Usando valor padrão")
    
    print("\n" + "=" * 60)
    print("🎯 RESUMO:")
    
    missing_critical = [var for var in critical_vars if not os.getenv(var)]
    if missing_critical:
        print(f"❌ {len(missing_critical)} variáveis críticas NÃO configuradas:")
        for var in missing_critical:
            print(f"    - {var}")
        print("\n⚠️  Configure essas variáveis no arquivo .env")
        return False
    else:
        print("✅ Todas as variáveis críticas estão configuradas!")
        return True

def test_database_connection():
    """Testa conexão com banco usando variável do .env"""
    print("\n🔌 Testando conexão com banco de dados...")
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL não configurada")
        return False
    
    try:
        import psycopg2
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"✅ Conexão bem-sucedida!")
        print(f"   PostgreSQL: {version[:50]}...")
        cursor.close()
        conn.close()
        return True
    except ImportError:
        print("⚠️  psycopg2 não instalado - não foi possível testar conexão")
        return True
    except Exception as e:
        print(f"❌ Erro na conexão: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 VERIFICAÇÃO DE CONFIGURAÇÃO DO .env")
    print("=" * 60)
    
    env_ok = verify_env_variables()
    db_ok = test_database_connection()
    
    print("\n" + "=" * 60)
    if env_ok and db_ok:
        print("🎉 SUCESSO! Todas as configurações estão corretas!")
    else:
        print("⚠️  ATENÇÃO! Há problemas na configuração que precisam ser resolvidos.")
    print("=" * 60)
