"""Script definitivo para criar o banco com as tabelas corretas."""
import asyncio
import psycopg2
import sys
import os

# Adicionar o caminho do projeto
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))

async def create_database_correctly():
    print("=== CRIAÇÃO CORRETA DO BANCO ===")
    
    # PASSO 1: Importar Base primeiro
    from src.synapse.db.base import Base, init_db, engine
    print(f"1. Base importado. Tabelas registradas: {list(Base.metadata.tables.keys())}")
    
    # PASSO 2: Importar o modelo File para registrá-lo
    from src.synapse.models.file import File
    print(f"2. Modelo File importado. Tabelas registradas: {list(Base.metadata.tables.keys())}")
    
    # PASSO 3: Verificar se o modelo foi registrado corretamente
    if 'files' in Base.metadata.tables:
        print("✅ Modelo File registrado corretamente!")
        file_table = Base.metadata.tables['files']
        print(f"   Colunas da tabela: {list(file_table.columns.keys())}")
    else:
        print("❌ Modelo File NÃO registrado!")
        return
    
    # PASSO 4: Criar o banco
    print("\n3. Criando banco de dados...")
    await init_db()
    
    # PASSO 5: Verificar resultado
    print("\n=== VERIFICAÇÃO FINAL ===")
    if os.path.exists('synapse.db'):
        conn = psycopg2.connect("synapse.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        table_names = [table[0] for table in tables]
        print(f"Tabelas criadas: {table_names}")
        
        if 'files' in table_names:
            print("\n✅ SUCESSO! Tabela 'files' criada!")
            cursor.execute("PRAGMA table_info(files);")
            columns = cursor.fetchall()
            print("Estrutura da tabela 'files':")
            for col in columns:
                print(f"  - {col[1]} ({col[2]})")
        else:
            print("❌ Tabela 'files' não foi criada")
        
        conn.close()
    else:
        print("❌ Arquivo de banco não foi criado")

if __name__ == "__main__":
    asyncio.run(create_database_correctly())
