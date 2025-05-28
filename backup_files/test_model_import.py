"""Teste de importação do modelo."""
from synapse.db.base import Base
print("Antes da importação:")
print(f"Tabelas: {list(Base.metadata.tables.keys())}")

from synapse.models.file import File
print("\nDepois da importação:")
print(f"Tabelas: {list(Base.metadata.tables.keys())}")
print(f"Modelo File: {File.__table__}")
