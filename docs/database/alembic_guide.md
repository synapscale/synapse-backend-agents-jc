# ⚠️ AVISO IMPORTANTE
As migrações não são mais executadas automaticamente ao iniciar o backend. Use este guia apenas para manutenção manual do banco.

# Guia de Gerenciamento de Migrações com Alembic

Este guia explica como gerenciar as migrações do banco de dados usando o Alembic.

## Comandos Básicos

### Verificar o Status Atual

Para verificar o status atual das migrações:

```bash
python -m alembic -c config/alembic.ini current
```

### Gerar uma Nova Migração

Para gerar uma nova migração com base nas mudanças nos modelos:

```bash
python -m alembic -c config/alembic.ini revision --autogenerate -m "descrição da migração"
```

### Aplicar Migrações Pendentes

Para aplicar todas as migrações pendentes:

```bash
python -m alembic -c config/alembic.ini upgrade head
```

Para aplicar uma migração específica:

```bash
python -m alembic -c config/alembic.ini upgrade <revision>
```

### Reverter Migrações

Para reverter para uma revisão específica:

```bash
python -m alembic -c config/alembic.ini downgrade <revision>
```

Para reverter uma migração:

```bash
python -m alembic -c config/alembic.ini downgrade -1
```

## Solução de Problemas Comuns

### Corrigir Incompatibilidades de Tipos

Se encontrar problemas de incompatibilidade de tipos, use o script `scripts/fix_migration_types.py`:

```bash
python scripts/fix_migration_types.py
```

### Múltiplas Revisões (Multiple Heads)

Se encontrar o erro "Multiple heads", você precisa criar uma migração de mesclagem:

```bash
python -m alembic -c config/alembic.ini merge heads
```

## Práticas Recomendadas

1. **Sempre revise as migrações geradas automaticamente** - O Alembic pode não detectar corretamente todas as mudanças.

2. **Evite modificar migrações já aplicadas** - Em vez disso, crie uma nova migração para fazer correções.

3. **Use tipos consistentes para chaves estrangeiras** - Certifique-se de que as colunas que fazem referência a outras tabelas usem o mesmo tipo (por exemplo, UUID para UUID).

4. **Teste as migrações em um ambiente de desenvolvimento antes de aplicá-las em produção**.

5. **Mantenha um backup do banco de dados antes de aplicar migrações em produção**.

## Estrutura do Projeto

- **alembic/versions/**: Contém os scripts de migração
- **alembic/env.py**: Configuração do ambiente do Alembic
- **config/alembic.ini**: Configuração do Alembic
