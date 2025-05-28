"""Atualizar main.py para garantir que o modelo seja importado."""
with open('src/synapse/main.py', 'r') as f:
    content = f.read()

# Adicionar import do modelo no início se não existir
if 'from synapse.models.file import File' not in content:
    lines = content.split('\n')
    # Encontrar onde adicionar o import
    for i, line in enumerate(lines):
        if line.startswith('from synapse.') and 'import' in line:
            # Adicionar após outros imports do synapse
            lines.insert(i + 1, 'from synapse.models.file import File  # Garantir registro do modelo')
            break
    
    # Salvar arquivo atualizado
    with open('src/synapse/main.py', 'w') as f:
        f.write('\n'.join(lines))
    print("✅ main.py atualizado com import do modelo")
else:
    print("✅ main.py já tem import do modelo")
