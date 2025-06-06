# 🚀 SynapScale Backend - Sistema Completo de Automação com IA

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)](https://postgresql.org)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-orange.svg)](https://www.sqlalchemy.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)
[![Tests](https://img.shields.io/badge/Tests-Passing-green.svg)](#testes)

## 📋 Visão Geral

O SynapScale Backend é uma plataforma completa de automação com IA que oferece:

- 🤖 **Agentes de IA Múltiplos** - OpenAI, Anthropic, Google, Groq, Grok, DeepSeek
- 🔄 **Workflows Visuais** - Sistema de nodes para automação
- 🔐 **Autenticação Robusta** - JWT com refresh tokens e 2FA
- 💾 **Banco PostgreSQL** - Com SQLAlchemy ORM
- 📁 **Gerenciamento de Arquivos** - Upload/download seguro
- 💬 **WebSockets** - Comunicação em tempo real
- 📊 **Analytics** - Métricas e monitoramento
- 🛒 **Marketplace** - Templates e componentes
- 👥 **Workspaces** - Colaboração em equipe
- 🐳 **Docker Ready** - Containerização completa

## 🏗️ Arquitetura

```
src/synapse/
├── 🔌 api/                    # Endpoints da API
│   ├── v1/endpoints/          # 14 Endpoints implementados
│   │   ├── agents.py          # Gerenciamento de agentes IA
│   │   ├── analytics.py       # Sistema completo de analytics
│   │   ├── auth.py           # Autenticação robusta
│   │   ├── conversations.py   # Sistema de conversas
│   │   ├── executions.py     # Execução de workflows
│   │   ├── files.py          # Gerenciamento de arquivos
│   │   ├── llm/              # Integração com múltiplos LLMs
│   │   ├── marketplace.py    # Marketplace completo
│   │   ├── nodes.py          # Sistema de nodes
│   │   ├── templates.py      # Templates de workflows
│   │   ├── user_variables.py # Variáveis de usuário
│   │   ├── websockets.py     # WebSocket em tempo real
│   │   ├── workflows.py      # Sistema de workflows
│   │   └── workspaces.py     # Workspaces colaborativos
│   └── deps.py               # Dependências da API
├── ⚙️ core/                   # Funcionalidades centrais
│   ├── auth/                 # Autenticação e autorização
│   ├── config/               # Configurações
│   ├── database/             # Conexão com banco
│   └── security.py           # Segurança avançada
├── 🤖 models/                 # 46 Modelos SQLAlchemy
├── 🔧 services/               # Lógica de negócio
├── 📊 schemas/                # Schemas de validação
└── 🛠️ utils/                  # Utilitários
```

## 🚀 Início Rápido

### Pré-requisitos
- Python 3.11+
- PostgreSQL 15+

### 1. Configuração do Ambiente
```bash
# Clone o repositório
git clone <repository-url>
cd synapse-backend-final

# Crie um ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Instale as dependências
pip install -r requirements.txt
```

### 2. Configuração do Banco
```bash
# Configure as variáveis de ambiente
cp .env.example .env
# Edite o .env com suas configurações

# Exemplo de configuração do banco de dados:
# DATABASE_URL=postgresql://user:password@host:port/database?sslmode=require
# DATABASE_SCHEMA=synapscale_db

# Execute as migrações
alembic upgrade head
```

### 3. Iniciar o Servidor
```bash
# Desenvolvimento
./start_dev.sh

# Ou manualmente
python -m uvicorn src.synapse.main:app --host 0.0.0.0 --port 8000 --reload

# Produção
./start.sh
```

## 🐳 Docker

### Desenvolvimento
```bash
docker-compose up -d
```

### Produção
```bash
docker build -t synapscale-backend .
docker run -p 8000:8000 synapscale-backend
```

## 📚 Documentação

- **API Docs**: http://localhost:8000/docs (Swagger UI)
- **ReDoc**: http://localhost:8000/redoc (Documentação alternativa)
- **OpenAPI**: http://localhost:8000/openapi.json (Especificação)

### Documentação Técnica
- 📖 [Guia de Desenvolvimento](docs/development_guide.md)
- 🏗️ [Arquitetura](docs/architecture.md)
- 🔐 [Segurança](docs/security_production.md)
- 🚀 [Guia de Implantação](docs/GUIA_COMPLETO_SYNAPSCALE.md)
- 🗄️ [Banco de Dados - 46 Tabelas](docs/database/🚀%20GUIA%20DEFINITIVO%20-%20Banco%20de%20Dados%20PostgreSQL%20para%20SynapScale%20(46%20Tabelas).md)

## 🧪 Testes

```bash
# Executar todos os testes
pytest

# Testes com cobertura
pytest --cov=src

# Testes específicos
pytest tests/unit/
pytest tests/integration/
pytest tests/performance/

# Script de validação completa
./test_setup.sh
```

## 🔧 Scripts Disponíveis

- `setup.sh` - Configuração inicial completa
- `start.sh` - Iniciar em modo produção
- `start_dev.sh` - Iniciar em modo desenvolvimento
- `test_setup.sh` - Executar testes
- `apply_migrations.sh` - Aplicar migrações do banco

## 🌟 Funcionalidades Principais

### 🤖 Agentes de IA
- **Múltiplos Provedores**: OpenAI, Anthropic, Google, Groq, Grok, DeepSeek
- **Sistema de Templates**: Prompts reutilizáveis
- **Execução Paralela**: Processamento assíncrono
- **Marketplace**: Compartilhamento de agentes

### 🔄 Workflows
- **Editor Visual**: Sistema de nodes drag-and-drop
- **Triggers Automáticos**: Execução baseada em eventos
- **Variáveis Personalizadas**: Configuração flexível
- **Scheduling Avançado**: Execução programada
- **Versionamento**: Controle de versões automático

### 🔐 Autenticação
- **JWT com Refresh Tokens**: Segurança robusta
- **Autenticação de Dois Fatores**: 2FA opcional
- **Sistema de Permissões**: Controle granular
- **Rate Limiting**: Proteção contra abuso

### 📁 Arquivos
- **Upload/Download Seguro**: Múltiplos formatos
- **Processamento Automático**: Análise de conteúdo
- **Versionamento**: Histórico de mudanças
- **Integração Cloud**: Storage distribuído

### 💬 Comunicação
- **WebSockets**: Tempo real
- **Sistema de Conversas**: Chat estruturado
- **Notificações Push**: Alertas instantâneos
- **Chat com IA**: Integração com agentes

### 📊 Analytics
- **Métricas de Performance**: Monitoramento completo
- **Logs Estruturados**: Rastreabilidade total
- **Dashboard**: Visualização em tempo real
- **Alertas Automáticos**: Notificações inteligentes

### 🛒 Marketplace
- **Templates de Workflows**: Biblioteca compartilhada
- **Componentes Reutilizáveis**: Nodes personalizados
- **Sistema de Avaliação**: Reviews e ratings
- **Monetização**: Marketplace comercial

### 👥 Workspaces
- **Colaboração em Equipe**: Múltiplos usuários
- **Permissões Granulares**: Controle de acesso
- **Compartilhamento**: Workflows e recursos
- **Auditoria**: Histórico de atividades

## 🔧 Configuração

### Variáveis de Ambiente Principais
```env
# Banco de Dados
DATABASE_URL=postgresql://user:pass@localhost:5432/defaultdb?sslmode=require
DATABASE_SCHEMA=synapscale_db
DATABASE_ECHO=false

# Segurança
SECRET_KEY=your_secret_key_here
JWT_SECRET_KEY=your_jwt_secret_here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# APIs de IA
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
GOOGLE_API_KEY=your_google_key
GROQ_API_KEY=your_groq_key

# CORS
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8080"]

# Upload de Arquivos
MAX_FILE_SIZE=10485760  # 10MB
UPLOAD_PATH=./storage/uploads

# Redis (Cache)
REDIS_URL=redis://localhost:6379/0

# WebSocket
WS_HEARTBEAT_INTERVAL=30
WS_MAX_CONNECTIONS=1000
```

## 📈 Performance

- **Async/Await** - Operações não-bloqueantes
- **Connection Pooling** - Otimização de banco
- **Caching Redis** - Cache distribuído
- **Rate Limiting** - Proteção contra abuso
- **Monitoring** - Métricas em tempo real
- **Load Balancing** - Distribuição de carga

## 🛡️ Segurança

- **HTTPS** - Comunicação criptografada
- **CORS** - Configuração adequada
- **SQL Injection** - Proteção via ORM
- **XSS** - Sanitização de dados
- **Rate Limiting** - Proteção contra DDoS
- **JWT Security** - Tokens seguros
- **Input Validation** - Validação rigorosa

## 🗄️ Banco de Dados

### 46 Tabelas Implementadas
- **Usuários e Autenticação**: users, user_sessions, user_tokens
- **Workflows**: workflows, nodes, connections, executions
- **Agentes**: agents, agent_configs, conversations, messages
- **Arquivos**: files, file_versions, file_permissions
- **Marketplace**: marketplace_items, reviews, downloads
- **Analytics**: events, metrics, reports
- **Workspaces**: workspaces, members, permissions
- **E muito mais...**

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

Veja [CONTRIBUTING.md](CONTRIBUTING.md) para mais detalhes.

## 📄 Licença

Este projeto está licenciado sob a [MIT License](LICENSE).

## 🆘 Suporte

- 📧 Email: suporte@synapscale.com
- 💬 Discord: [SynapScale Community](https://discord.gg/synapscale)
- 📖 Docs: [docs.synapscale.com](https://docs.synapscale.com)

## 🎯 Roadmap

- [x] Sistema completo de agentes IA
- [x] Workflows visuais avançados
- [x] Marketplace integrado
- [x] Analytics em tempo real
- [x] Workspaces colaborativos
- [ ] Sistema de plugins
- [ ] API GraphQL
- [ ] Clustering e alta disponibilidade

## 📊 Status do Projeto

- ✅ **Backend**: 100% Completo
- ✅ **API**: 14 Endpoints implementados
- ✅ **Banco**: 46 Tabelas configuradas
- ✅ **Testes**: Suite completa
- ✅ **Documentação**: Completa
- ✅ **Docker**: Pronto para produção

---

**Desenvolvido com ❤️ pela equipe SynapScale**

**Versão**: 2.0 Final  
**Data**: Junho 2025  
**Status**: Produção Ready 🚀

