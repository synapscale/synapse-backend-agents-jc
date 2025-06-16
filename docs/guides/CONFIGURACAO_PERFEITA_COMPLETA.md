# 🚨 NOTA IMPORTANTE
> Scripts antigos como `start_master.sh`, `auto_setup.sh`, `setup_complete.py`, etc. não são mais utilizados. Use apenas `dev.sh`, `prod.sh` e `setup.sh` (se existir).

# 🎉 SYNAPSCALE BACKEND - CONFIGURAÇÃO PERFEITA COMPLETA!

## 🚀 FLUXO PADRÃO E SIMPLIFICADO

O backend agora segue um padrão único e robusto:

### 1️⃣ Instalação e Setup
```bash
# Remova ambientes virtuais antigos
rm -rf venv .venv env ENV

# Crie o ambiente virtual com Python 3.11
python3.11 -m venv venv
source venv/bin/activate

# Atualize o pip
pip install --upgrade pip

# Instale o torch antes das demais dependências
pip install torch

# Instale as dependências do projeto
pip install -r requirements.txt

# Configure o arquivo .env
cp .env.example .env
# Edite o .env conforme necessário
```

### 2️⃣ Inicialização

- **Desenvolvimento:**
  ```bash
  ./dev.sh
  ```
- **Produção:**
  ```bash
  ./prod.sh
  ```

### 3️⃣ Migrações de Banco de Dados
- Migrações **não são mais automáticas**. Rode manualmente se necessário:
  ```bash
  alembic upgrade head
  ```

### 4️⃣ Observações
- Use **apenas Python 3.11**.
- Não utilize scripts antigos como `start_master.sh`, `auto_setup.sh`, etc.
- O único arquivo de configuração é o `.env`.

---

## 🌟 RESULTADO FINAL
- Fluxo de inicialização simples e padronizado
- Ambiente sempre consistente
- Zero ambiguidade sobre múltiplos ambientes ou scripts
- Documentação e onboarding claros
