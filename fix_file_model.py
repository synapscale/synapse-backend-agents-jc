"""Script para corrigir o modelo File."""

# Ler o arquivo atual
with open('src/synapse/models/file.py', 'r') as f:
    content = f.read()

print("CONTEÚDO ATUAL:")
print("=" * 50)
print(content[:500] + "...")

# Se encontrar import incorreto do Base, vamos corrigir
if 'from sqlalchemy.ext.declarative import declarative_base' in content:
    print("\n❌ PROBLEMA ENCONTRADO: File está criando seu próprio Base!")
    content = content.replace(
        'from sqlalchemy.ext.declarative import declarative_base\n\nBase = declarative_base()',
        'from synapse.db.base import Base'
    )
elif 'declarative_base()' in content:
    print("\n❌ PROBLEMA ENCONTRADO: File está criando Base local!")
else:
    print("\n✅ Import do Base parece correto")

# Verificar se já importa corretamente
if 'from synapse.db.base import Base' in content:
    print("✅ Import correto do Base encontrado")
else:
    print("❌ Import do Base não encontrado - adicionando...")
    # Adicionar import correto
    lines = content.split('\n')
    import_added = False
    new_lines = []
    
    for line in lines:
        new_lines.append(line)
        # Adicionar após imports do SQLAlchemy
        if 'from sqlalchemy' in line and not import_added:
            new_lines.append('from synapse.db.base import Base')
            import_added = True
    
    content = '\n'.join(new_lines)

print(f"\nConteúdo corrigido salvo!")
