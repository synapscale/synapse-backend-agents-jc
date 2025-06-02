"""Teste do modelo corrigido."""
from src.synapse.db.base import Base
from src.synapse.models.file import File

print("=== TESTE DO MODELO CORRIGIDO ===")
print(f"Tabelas registradas: {list(Base.metadata.tables.keys())}")
print(f"Modelo File: {File.__table__.name}")
print(f"Colunas: {list(File.__table__.columns.keys())}")
