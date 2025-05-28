"""Script para corrigir a importação do Base."""
import os

# 1. Verificar conteúdo atual do file.py
print("=== CONTEÚDO ATUAL DO file.py ===")
with open('src/synapse/models/file.py', 'r') as f:
    content = f.read()
    lines = content.split('\n')
    for i, line in enumerate(lines[:20], 1):
        print(f"{i:2}: {line}")

print("\n=== PROCURANDO IMPORTS DO BASE ===")
for i, line in enumerate(lines, 1):
    if 'Base' in line and ('import' in line or 'from' in line):
        print(f"Linha {i}: {line}")
