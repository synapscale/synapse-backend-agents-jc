"""Script para inicializar o banco de dados corretamente."""
import sqlite3
from src.synapse.database import Base, engine, create_tables
from src.synapse.models.file import File  # IMPORTANTE: Importar o modelo


def create_database():
    """Cria o banco de dados e todas as tabelas."""
    print("=== INICIALIZANDO BANCO DE DADOS ===")
    
    # Verificar se o modelo foi registrado
    print(f"Modelos registrados: {list(Base.metadata.tables.keys())}")
    
    # Criar todas as tabelas
    print("Criando tabelas...")
    create_tables()
    
    # Verificar tabelas criadas
    print("\n=== VERIFICANDO TABELAS CRIADAS ===")
    conn = sqlite3.connect("synapse.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print(f"Tabelas no banco: {[table[0] for table in tables]}")
    
    # Ver estrutura da tabela files se existir
    if ('files',) in tables:
        print("\n=== ESTRUTURA DA TABELA FILES ===")
        cursor.execute("PRAGMA table_info(files);")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
    
    conn.close()
    print("✅ Banco de dados inicializado com sucesso!")


if __name__ == "__main__":
    create_database()
