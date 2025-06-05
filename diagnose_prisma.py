#!/usr/bin/env python3
"""
Diagnóstico completo dos problemas de conexão do Prisma
"""
import asyncio
import os
import sys
import subprocess
import time
from pathlib import Path

# Adicionar o diretório src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

async def test_postgresql_connection():
    """Testa conexão direta com PostgreSQL"""
    print("🔍 Testando conexão PostgreSQL...")
    
    try:
        import psycopg2
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="synapse",
            user="postgres",
            password="postgres"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT version()")
        version = cursor.fetchone()
        print(f"✅ PostgreSQL conectado: {version[0][:50]}...")
        cursor.close()
        conn.close()
        return True
    except ImportError:
        print("⚠️  psycopg2 não instalado - instalando...")
        subprocess.run([sys.executable, "-m", "pip", "install", "psycopg2-binary"])
        return await test_postgresql_connection()
    except Exception as e:
        print(f"❌ Erro na conexão PostgreSQL: {e}")
        return False

async def test_prisma_connection():
    """Testa conexão via Prisma"""
    print("🔍 Testando conexão via Prisma...")
    
    try:
        from prisma import Prisma
        
        prisma = Prisma()
        await prisma.connect()
        
        # Teste simples
        result = await prisma.query_raw("SELECT 'Prisma OK' as status")
        print(f"✅ Prisma conectado: {result}")
        
        await prisma.disconnect()
        return True
        
    except ImportError as e:
        print(f"❌ Erro de importação Prisma: {e}")
        print("💡 Execute: npx prisma generate")
        return False
    except Exception as e:
        print(f"❌ Erro na conexão Prisma: {e}")
        return False

def check_environment():
    """Verifica variáveis de ambiente"""
    print("🔍 Verificando variáveis de ambiente...")
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL não definida")
        return False
    
    print(f"✅ DATABASE_URL: {database_url[:50]}...")
    
    # Verificar formato
    if not database_url.startswith(("postgresql://", "postgres://", "prisma+postgres://")):
        print("❌ DATABASE_URL não é uma URL PostgreSQL válida")
        return False
    
    return True

def check_prisma_client():
    """Verifica se o cliente Prisma foi gerado"""
    print("🔍 Verificando cliente Prisma...")
    
    client_path = Path("app/generated/prisma/client")
    if not client_path.exists():
        print("❌ Cliente Prisma não foi gerado")
        print("💡 Execute: npx prisma generate")
        return False
    
    print("✅ Cliente Prisma encontrado")
    return True

def check_postgresql_service():
    """Verifica se PostgreSQL está rodando"""
    print("🔍 Verificando serviço PostgreSQL...")
    
    try:
        result = subprocess.run(
            ["pg_isready", "-h", "localhost", "-p", "5432"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ PostgreSQL está rodando")
            return True
        else:
            print("❌ PostgreSQL não está rodando")
            print("💡 Execute: sudo systemctl start postgresql")
            print("💡 Ou: docker-compose up -d db")
            return False
            
    except FileNotFoundError:
        print("⚠️  pg_isready não encontrado")
        print("💡 Tentando via Docker...")
        
        try:
            result = subprocess.run(
                ["docker-compose", "ps", "db"],
                capture_output=True,
                text=True
            )
            
            if "Up" in result.stdout:
                print("✅ PostgreSQL rodando via Docker")
                return True
            else:
                print("❌ PostgreSQL não está rodando via Docker")
                return False
                
        except FileNotFoundError:
            print("❌ Docker Compose não encontrado")
            return False

async def run_diagnostics():
    """Executa todos os diagnósticos"""
    print("🚀 Iniciando diagnóstico completo do Prisma...")
    print("=" * 60)
    
    checks = [
        ("Variáveis de ambiente", check_environment),
        ("Serviço PostgreSQL", check_postgresql_service),
        ("Cliente Prisma", check_prisma_client),
        ("Conexão PostgreSQL", test_postgresql_connection),
        ("Conexão Prisma", test_prisma_connection),
    ]
    
    results = {}
    
    for name, check_func in checks:
        print(f"\n📋 {name}:")
        try:
            if asyncio.iscoroutinefunction(check_func):
                result = await check_func()
            else:
                result = check_func()
            results[name] = result
        except Exception as e:
            print(f"❌ Erro inesperado: {e}")
            results[name] = False
    
    print("\n" + "=" * 60)
    print("📊 RESUMO DO DIAGNÓSTICO:")
    print("=" * 60)
    
    all_good = True
    for name, result in results.items():
        status = "✅ OK" if result else "❌ FALHA"
        print(f"{name:.<30} {status}")
        if not result:
            all_good = False
    
    print("=" * 60)
    
    if all_good:
        print("🎉 Todos os testes passaram! O Prisma deve estar funcionando.")
    else:
        print("⚠️  Problemas encontrados. Veja as sugestões acima.")
        print("\n💡 SOLUÇÕES RÁPIDAS:")
        print("1. Execute o script de correção: ./fix_prisma_connection.sh")
        print("2. Verifique o arquivo .env")
        print("3. Reinicie o PostgreSQL")
        print("4. Regenere o cliente Prisma: npx prisma generate")

if __name__ == "__main__":
    asyncio.run(run_diagnostics())
