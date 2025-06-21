# 🚀 Guia de Instalação e Configuração - SynapScale Backend

## 📋 Visão Geral

Este é o guia **oficial e único** para instalação e configuração do SynapScale Backend. Todas as instruções necessárias estão neste documento.

## ⚡ Pré-requisitos

- **Python 3.11** (obrigatório)
- **PostgreSQL 13+** (recomendado: 15+)
- **Redis 6+** (opcional, para cache)
- **Git 2.30+**

## 🔧 Instalação Rápida (5 minutos)

### 1. Clonar e Configurar Ambiente

```bash
# Clone o repositório
git clone <URL_DO_SEU_REPOSITORIO>
cd synapse-backend-agents-jc

# Criar ambiente virtual
python3.11 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou venv\Scripts\activate  # Windows

# Instalar dependências
pip install --upgrade pip
pip install torch
pip install -r requirements.txt
```

### 2. Configurar Variáveis de Ambiente

```bash
# Criar arquivo .env
cp .env.example .env

# Editar configurações (obrigatório)
nano .env  # ou use seu editor preferido
```

**Configurações mínimas necessárias no `.env`:**

```env
# Banco de Dados (OBRIGATÓRIO)
DATABASE_URL=postgresql://usuario:senha@localhost:5432/synapscale_db

# Segurança (OBRIGATÓRIO)
SECRET_KEY=sua_chave_secreta_aqui
JWT_SECRET_KEY=sua_chave_jwt_aqui

# LLM (pelo menos uma chave)
OPENAI_API_KEY=sua_chave_openai_aqui
# ou
ANTHROPIC_API_KEY=sua_chave_anthropic_aqui
```

### 3. Preparar Banco de Dados

```bash
# PostgreSQL
createdb synapscale_db

# Executar migrações (se necessário)
alembic upgrade head
```

### 4. Iniciar o Servidor

```bash
# Desenvolvimento (com auto-reload)
./dev.sh

# Produção
./prod.sh
```

### 5. Verificar Instalação

```bash
# Testar API
curl http://localhost:8000/health

# Acessar documentação
open http://localhost:8000/docs
```

## 📚 Configuração Detalhada

### Banco de Dados

#### PostgreSQL (Recomendado)

```bash
# Instalar PostgreSQL
sudo apt install postgresql postgresql-contrib  # Ubuntu
brew install postgresql@15                      # macOS

# Configurar banco
sudo -u postgres psql
CREATE USER synapscale WITH PASSWORD 'senha_forte';
CREATE DATABASE synapscale_db OWNER synapscale;
GRANT ALL PRIVILEGES ON DATABASE synapscale_db TO synapscale;
\q
```

#### Docker (Alternativa)

```bash
docker run --name postgres-synapscale \
  -e POSTGRES_USER=synapscale \
  -e POSTGRES_PASSWORD=senha_forte \
  -e POSTGRES_DB=synapscale_db \
  -p 5432:5432 \
  -d postgres:15
```

### Configurações de Produção

Para ambiente de produção, configure no `.env`:

```env
ENVIRONMENT=production
DEBUG=false
SECURE_COOKIES=true
ENABLE_HTTPS_REDIRECT=true
RATE_LIMIT_ENABLED=true
```

### Configurações de LLM

Configure pelo menos um provedor de IA:

```env
# OpenAI (Recomendado)
OPENAI_API_KEY=sk-proj-...
LLM_DEFAULT_PROVIDER=openai

# Ou Anthropic Claude
ANTHROPIC_API_KEY=sk-ant-api03-...
LLM_DEFAULT_PROVIDER=anthropic

# Ou Google Gemini
GOOGLE_API_KEY=...
LLM_DEFAULT_PROVIDER=google
```

## 🛠️ Comandos Úteis

### Desenvolvimento

```bash
# Iniciar servidor de desenvolvimento
./dev.sh

# Executar testes
pytest

# Executar migrações
alembic upgrade head

# Gerar nova migração
alembic revision --autogenerate -m "descrição"
```

### Docker

```bash
# Construir e iniciar com Docker
docker-compose up -d

# Ver logs
docker-compose logs -f

# Parar serviços
docker-compose down
```

## 🔐 Segurança

### Gerar Chaves Seguras

```bash
# Gerar chave secreta
openssl rand -hex 32

# Gerar chave JWT
openssl rand -hex 64
```

### Configurações de Segurança

```env
# Variáveis de segurança obrigatórias
SECRET_KEY=chave_gerada_com_openssl
JWT_SECRET_KEY=chave_jwt_gerada
ENCRYPTION_KEY=chave_base64_32_bytes

# Configurações de CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000","https://seu-frontend.com"]

# Rate limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_DEFAULT=100/minute
```

## 📡 Endpoints Principais

Após a instalação, os seguintes endpoints estarão disponíveis:

- **API Docs**: `http://localhost:8000/docs`
- **Health Check**: `http://localhost:8000/health`
- **LLM Endpoints**: `http://localhost:8000/api/v1/llm/`
- **Files**: `http://localhost:8000/api/v1/files/`
- **Auth**: `http://localhost:8000/api/v1/auth/`

## 🚨 Solução de Problemas

### Erro de Importação

```bash
# Ativar ambiente virtual
source venv/bin/activate

# Reinstalar dependências
pip install -r requirements.txt
```

### Erro de Banco de Dados

```bash
# Verificar conexão
psql -U synapscale -d synapscale_db -h localhost

# Executar migrações
alembic upgrade head
```

### Erro de Porta em Uso

```bash
# Verificar processos na porta 8000
lsof -i :8000

# Matar processo
kill -9 PID
```

## 📖 Próximos Passos

1. **Configurar seu primeiro usuário**
2. **Testar endpoints da API**
3. **Integrar com seu frontend**
4. **Configurar monitoramento** (para produção)

## 🆘 Suporte

- **Documentação da API**: `/docs`
- **Logs**: `logs/synapscale.log`
- **Issues**: GitHub Issues

---

**Última atualização**: Dezembro 2024
**Versão**: 2.0.0 