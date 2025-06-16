# 🚨 NOTA IMPORTANTE
> Scripts antigos como `auto_setup.sh`, `setup_complete.py`, etc. não são mais utilizados. Use apenas `dev.sh`, `prod.sh` e `setup.sh` (se existir).

# 🛠️ Scripts de Setup do SynapScale Backend

O setup do projeto agora é padronizado e simplificado:

## Setup Único e Recomendado

```bash
rm -rf venv .venv env ENV
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install torch
pip install -r requirements.txt
cp .env.example .env
# Edite o .env conforme necessário
```

## Inicialização
- **Desenvolvimento:**
  ```bash
  ./dev.sh
  ```
- **Produção:**
  ```bash
  ./prod.sh
  ```

## Migrações de Banco de Dados
- Migrações **não são mais automáticas**. Rode manualmente se necessário:
  ```bash
  alembic upgrade head
  ```
