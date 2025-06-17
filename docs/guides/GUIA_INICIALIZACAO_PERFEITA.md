# 🚀 GUIA DE INICIALIZAÇÃO DO SYNAPSCALE BACKEND

# 🚨 NOTA IMPORTANTE
> Scripts antigos como `auto_setup.sh`, `start_dev_auto.sh`, etc. não são mais utilizados. Use apenas `dev.sh`, `prod.sh` e `setup.sh` (se existir).

## FLUXO PADRÃO EM 2 PASSOS

### 1️⃣ Setup Inicial
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

---

- Use **apenas Python 3.11**.
- Não utilize scripts antigos como `auto_setup.sh`, `start_dev_auto.sh`, etc.
- O único arquivo de configuração é o `.env`.

## 🎯 O QUE ACONTECE AUTOMATICAMENTE

### 🔄 No Setup Inicial (`auto_setup.sh`):
1. **Ambiente Virtual**: Criado e configurado automaticamente
2. **Dependências**: Todas instaladas via requirements.txt
3. **Arquivo .env**: Criado com template completo
4. **Chaves Seguras**: SECRET_KEY, JWT_SECRET_KEY, ENCRYPTION_KEY geradas
5. **Diretórios**: uploads/, logs/, storage/ criados
6. **Banco**: Migrações executadas
7. **Propagação**: Todas as variáveis distribuídas para arquivos necessários

### 🔄 Na Propagação (`propagate_env.py`):
1. **Alembic**: DATABASE_URL configurada automaticamente
2. **Config.py**: Variáveis sincronizadas
3. **Docker**: docker-compose.yml atualizado
4. **Render**: render.yaml configurado
5. **Scripts**: Carregamento de .env adicionado

### 🔄 Na Inicialização (`start_*_auto.sh`):
1. **Ambiente**: Ativado automaticamente
2. **Variáveis**: Carregadas do .env
3. **Migrações**: Executadas automaticamente
4. **Diretórios**: Verificados e criados
5. **Servidor**: Iniciado com configurações ideais

## 📁 ESTRUTURA DE ARQUIVOS GERADA

```
projeto/
├── .env                    # ← ÚNICO arquivo que você edita
├── .env.template          # Template para novos ambientes
├── auto_setup.sh          # Script de setup completo
├── setup_complete.py      # Configurador Python avançado
├── propagate_env.py       # Propagador de variáveis
├── env_loader.py          # Carregador automático (gerado)
├── start_dev_auto.sh      # Inicialização desenvolvimento (gerado)
├── start_prod_auto.sh     # Inicialização produção (gerado)
├── venv/                  # Ambiente virtual (criado)
├── uploads/               # Uploads (criado)
├── logs/                  # Logs (criado)
└── storage/               # Storage (criado)
```

## 🔑 VARIÁVEIS DO .ENV

### ✅ OBRIGATÓRIAS (você configura):
```bash
DATABASE_URL=postgresql://user:pass@host:port/db
```

### 🤖 AUTO-GERADAS (script configura):
```bash
SECRET_KEY=...          # Gerada automaticamente
JWT_SECRET_KEY=...      # Gerada automaticamente  
ENCRYPTION_KEY=...      # Gerada automaticamente
WEBHOOK_SECRET=...      # Gerada automaticamente
```

### 📧 OPCIONAIS (para funcionalidades específicas):
```bash
SMTP_USER=...           # Para envio de emails
SMTP_PASSWORD=...       # Para envio de emails
OPENAI_API_KEY=...      # Para IA OpenAI
ANTHROPIC_API_KEY=...   # Para IA Claude
GOOGLE_API_KEY=...      # Para IA Gemini
```

## 🚀 COMANDOS PRINCIPAIS

### Setup Inicial (uma vez):
```bash
./auto_setup.sh
```

### Desenvolvimento:
```bash
./start_dev_auto.sh     # Inicia com reload automático
```

### Produção:
```bash
./start_prod_auto.sh    # Inicia com Gunicorn otimizado
```

### Re-propagar variáveis:
```bash
python3 propagate_env.py
```

## 🎯 BENEFÍCIOS DESTE FLUXO

### ✅ **AUTOMAÇÃO TOTAL**
- Zero configuração manual
- Todas as dependências resolvidas
- Ambiente sempre consistente

### ✅ **SEGURANÇA**
- Chaves criptográficas seguras geradas automaticamente
- Configurações de produção aplicadas automaticamente
- Validações de segurança integradas

### ✅ **SINCRONIZAÇÃO**
- Uma única fonte de verdade (.env)
- Todas as configurações propagadas automaticamente
- Nunca mais arquivos desatualizados

### ✅ **SIMPLICIDADE**
- Apenas 1 arquivo para editar (.env)
- Scripts inteligentes fazem o resto
- Funciona igual em dev e produção

## 🔧 TROUBLESHOOTING

### Problema: Erro ao executar auto_setup.sh
**Solução:**
```bash
chmod +x auto_setup.sh
./auto_setup.sh
```

### Problema: Erro de importação
**Solução:**
```bash
source venv/bin/activate
python3 setup_complete.py
```

### Problema: Banco não conecta
**Solução:**
1. Verifique DATABASE_URL no .env
2. Execute: `python3 propagate_env.py`
3. Reinicie: `./start_dev_auto.sh`

### Problema: Variáveis não carregam
**Solução:**
```bash
python3 propagate_env.py
source venv/bin/activate
./start_dev_auto.sh
```

## 📚 ENDPOINTS DISPONÍVEIS

Após inicialização:
- **Backend**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health**: http://localhost:8000/health

## 🎉 RESULTADO FINAL

**VOCÊ SÓ PRECISA:**
1. Executar `./auto_setup.sh` (uma vez)
2. Configurar DATABASE_URL no `.env`
3. Executar `./start_dev_auto.sh`

**TUDO FUNCIONA AUTOMATICAMENTE!** 🚀
