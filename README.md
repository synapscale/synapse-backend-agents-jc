# 🚀 SynapScale Backend API

**Plataforma de Automação com IA - Backend Completo**

API robusta e escalável para gerenciamento de workflows, agentes AI e automações empresariais.

## 📋 Índice

- [Características](#características)
- [Tecnologias](#tecnologias)
- [Instalação](#instalação)
- [Configuração](#configuração)
- [Execução](#execução)
- [Documentação da API](#documentação-da-api)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Deploy](#deploy)
- [Contribuição](#contribuição)

## ✨ Características

### 🔐 **Sistema de Autenticação Completo**
- Registro e login de usuários
- Autenticação JWT robusta
- Refresh tokens automáticos
- Verificação de email
- Reset de senha
- Controle de sessões

### ⚡ **Engine de Workflows**
- Criação e execução de workflows
- Nodes reutilizáveis e customizáveis
- Execução em tempo real
- Monitoramento de performance
- Sistema de filas inteligente

### 🤖 **Integração com IA**
- Múltiplos provedores de IA
- Agentes inteligentes
- Processamento de linguagem natural
- Análise de dados automatizada

### 💬 **Sistema de Conversas**
- Chat em tempo real via WebSocket
- Histórico de conversas
- Suporte a múltiplos usuários
- Notificações push

### 📁 **Gerenciamento de Arquivos**
- Upload seguro de arquivos
- Processamento automático
- Controle de versões
- Integração com workflows

### 🏪 **Marketplace**
- Templates de workflows
- Componentes reutilizáveis
- Sistema de avaliações
- Coleções organizadas

### 📊 **Analytics e Monitoramento**
- Métricas em tempo real
- Dashboard administrativo
- Logs estruturados
- Alertas automáticos

## 🛠 Tecnologias

- **Framework**: FastAPI 0.104.1
- **Banco de Dados**: PostgreSQL com SQLAlchemy
- **Cache**: Redis
- **Autenticação**: JWT + Passlib
- **WebSocket**: FastAPI WebSocket
- **Validação**: Pydantic V2
- **Documentação**: Swagger UI + ReDoc
- **Testes**: Pytest
- **Deploy**: Docker + Docker Compose

## 🚀 Instalação

### Pré-requisitos

 - Python 3.11
 - PostgreSQL 13+
 - Redis 6+
 - Git

### 1. Clone o Repositório

```bash
git clone https://github.com/synapscale/synapse-backend-agents-jc.git
cd synapse-backend-agents-jc
```

### 2. Crie o Ambiente Virtual

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

### 3. Instale as Dependências

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## ⚙️ Configuração

### 1. Variáveis de Ambiente

Copie o arquivo de exemplo e configure:

```bash
cp .env.example .env
```

### 2. Configure o `.env`

```env
# ============================
# CONFIGURAÇÕES DO BANCO DE DADOS
# ============================
# Defina a variável de ambiente com a URL do banco
DATABASE_URL=postgresql://usuario:senha@localhost:5432/synapscale_db
DATABASE_SCHEMA=synapscale_db

# ============================
# CONFIGURAÇÕES DE SEGURANÇA
# ============================
SECRET_KEY=sua_chave_secreta_super_forte_32_chars
JWT_SECRET_KEY=sua_chave_jwt_super_forte_32_chars
ENCRYPTION_KEY=sua_chave_criptografia_base64_32_bytes

# ============================
# CONFIGURAÇÕES DA API
# ============================
API_V1_STR=/api/v1
PROJECT_NAME=SynapScale Backend API
VERSION=1.0.0
DESCRIPTION=Plataforma de Automação com IA
DEBUG=false

# ============================
# CONFIGURAÇÕES DE CORS
# ============================
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://localhost:3001","https://app.synapscale.com"]

# ============================
# CONFIGURAÇÕES DE EMAIL
# ============================
SMTP_TLS=true
SMTP_PORT=587
SMTP_HOST=smtp.gmail.com
SMTP_USER=seu_email@gmail.com
SMTP_PASSWORD=sua_senha_app

# ============================
# CONFIGURAÇÕES DE UPLOAD
# ============================
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=10485760
ALLOWED_EXTENSIONS=.pdf,.doc,.docx,.txt,.csv,.xlsx,.png,.jpg,.jpeg

# ============================
# CONFIGURAÇÕES DE CACHE
# ============================
REDIS_URL=redis://localhost:6379/0
CACHE_TTL=3600

# ============================
# CONFIGURAÇÕES DE IA
# ============================
OPENAI_API_KEY=sua_chave_openai
ANTHROPIC_API_KEY=sua_chave_anthropic
GOOGLE_API_KEY=sua_chave_google
```

### 3. Configure o Banco de Dados

```bash
# Crie o banco de dados
createdb synapscale_db

# Execute as migrações (se houver)
python -c "from src.synapse.database import Base, engine; Base.metadata.create_all(bind=engine)"
```

## 🏃‍♂️ Execução

### Desenvolvimento

```bash
# Ative o ambiente virtual
source venv/bin/activate

# Execute o servidor de desenvolvimento
python -m uvicorn src.synapse.main:app --host 0.0.0.0 --port 8000 --reload
```

### Produção

```bash
# Execute com Gunicorn
gunicorn src.synapse.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Docker

```bash
# Build da imagem
docker build -t synapscale-backend .

# Execute o container
docker run -p 8000:8000 --env-file .env synapscale-backend
```

### Docker Compose

```bash
# Execute todo o stack
docker-compose up -d
```

## 📚 Documentação da API

Após iniciar o servidor, acesse:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### Principais Endpoints

#### Autenticação
- `POST /api/v1/auth/auth/register` - Registrar usuário
- `POST /api/v1/auth/auth/login` - Login
- `POST /api/v1/auth/auth/refresh` - Refresh token
- `GET /api/v1/auth/auth/me` - Dados do usuário atual

#### Workflows
- `GET /api/v1/workflows/` - Listar workflows
- `POST /api/v1/workflows/` - Criar workflow
- `GET /api/v1/workflows/{id}` - Detalhes do workflow
- `POST /api/v1/workflows/{id}/execute` - Executar workflow

#### WebSocket
- `WS /api/v1/ws/execution/{execution_id}` - Execução em tempo real
- `WS /api/v1/ws/global` - Eventos globais
- `WS /api/v1/ws/user` - Eventos do usuário

## 📁 Estrutura do Projeto

```
synapse-backend-agents-jc/
├── src/
│   └── synapse/
│       ├── api/
│       │   └── v1/
│       │       ├── endpoints/
│       │       │   ├── auth.py
│       │       │   ├── workflows.py
│       │       │   ├── agents.py
│       │       │   ├── files.py
│       │       │   └── websockets.py
│       │       └── router.py
│       ├── core/
│       │   ├── config.py
│       │   ├── security.py
│       │   └── exceptions.py
│       ├── models/
│       │   ├── user.py
│       │   ├── workflow.py
│       │   ├── agent.py
│       │   └── __init__.py
│       ├── schemas/
│       │   ├── user.py
│       │   ├── workflow.py
│       │   └── __init__.py
│       ├── services/
│       │   ├── auth_service.py
│       │   ├── workflow_service.py
│       │   ├── execution_service.py
│       │   └── websocket_service.py
│       ├── utils/
│       │   ├── email.py
│       │   ├── file_handler.py
│       │   └── validators.py
│       ├── database.py
│       ├── config.py
│       └── main.py
├── tests/
├── docs/
├── scripts/
├── .env.example
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

## 🚀 Deploy

### Variáveis de Produção

```env
DEBUG=false
# Defina `DATABASE_URL` com sua string de conexão
DATABASE_URL=postgresql://user:pass@prod-db:5432/synapscale
REDIS_URL=redis://prod-redis:6379/0
BACKEND_CORS_ORIGINS=["https://app.synapscale.com"]
```

### Docker Compose Produção

```yaml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      # Defina a variável com sua URL do banco
      - DATABASE_URL=postgresql://user:pass@db:5432/synapscale
    depends_on:
      - db
      - redis
  
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: synapscale
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:7-alpine
    
volumes:
  postgres_data:
```

### Nginx (Opcional)

```nginx
server {
    listen 80;
    server_name api.synapscale.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /ws/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

## 🧪 Testes

Antes de rodar os testes, instale as dependências de desenvolvimento:

```bash
# Usando pip
pip install -r requirements.txt

# Ou com Poetry
poetry install

# Ou execute o script auxiliar
./scripts/prepare_tests.sh
```

Com o ambiente preparado, execute os testes normalmente:

```bash
# Execute todos os testes
pytest

# Execute com cobertura
pytest --cov=src

# Execute testes específicos
pytest tests/test_auth.py
```

## 📈 Monitoramento

### Health Check

```bash
curl http://localhost:8000/health
```

### Métricas

- Acesse `/metrics` para métricas Prometheus
- Logs estruturados em JSON
- Monitoramento de performance automático

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 🆘 Suporte

- **Email**: suporte@synapscale.com
- **Discord**: [SynapScale Community](https://discord.gg/synapscale)
- **Documentação**: [docs.synapscale.com](https://docs.synapscale.com)

## 🎯 Roadmap

- [ ] Sistema de plugins
- [ ] Integração com mais provedores de IA
- [ ] Dashboard analytics avançado
- [ ] API GraphQL
- [ ] Suporte a múltiplos idiomas
- [ ] Sistema de billing

---

**Desenvolvido com ❤️ pela equipe SynapScale**

