# Scripts de Manutenção do Repositório

A maioria dos scripts antigos foi removida ou unificada. O fluxo atual é simples:

- Use apenas `dev.sh` e `prod.sh` para rodar o backend.
- Migrações de banco de dados são manuais: `alembic upgrade head`.
- Para limpar ambientes antigos:
  ```bash
  rm -rf venv .venv env ENV
  ```
- Para atualizar dependências:
  ```bash
  source venv/bin/activate
  pip install --upgrade pip
  pip install torch
  pip install -r requirements.txt
  ```

> Scripts como `fix_requirements.sh`, `fix_env_files.sh`, `auto_setup.sh`, etc. não são mais necessários no fluxo atual.
