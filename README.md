# 🚀 SynapScale Backend

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-2.0.0-orange.svg)](pyproject.toml)

**Plataforma backend completa para integração com LLMs (Large Language Models)** - Uma solução robusta e escalável para desenvolvedores que precisam integrar múltiplos provedores de IA em suas aplicações.

---

## 📋 Índice

- [Visão Geral](#-visão-geral)
- [Funcionalidades](#-funcionalidades)
- [Arquitetura](#-arquitetura)  
- [Início Rápido](#-início-rápido)
- [Instalação](#-instalação)
- [Configuração](#-configuração)
- [API Reference](#-api-reference)
- [Desenvolvimento](#-desenvolvimento)
- [Testes](#-testes)
- [Deploy](#-deploy)
- [Contribuição](#-contribuição)
- [Licença](#-licença)

---

## 🌟 Visão Geral

O **SynapScale Backend** é uma plataforma de integração de IA que permite aos desenvolvedores conectar facilmente suas aplicações a múltiplos provedores de LLM (OpenAI, Anthropic, Google, etc.) através de uma API unificada e escalável.

### 🎯 Principais Objetivos
- **Unificação**: Interface única para múltiplos provedores de IA
- **Escalabilidade**: Arquitetura preparada para alta demanda
- **Flexibilidade**: Suporte a diferentes tipos de modelos e casos de uso
- **Segurança**: Autenticação robusta e gestão segura de API keys
- **Observabilidade**: Logs detalhados e métricas de performance

---

## ✨ Funcionalidades

### 🤖 **Integração com LLMs**
- Suporte para **OpenAI GPT-4/GPT-3.5**
- Integração com **Anthropic Claude**
- Compatibilidade com **Google Gemini**
- Suporte a **modelos locais** (Ollama, Hugging Face)
- **Roteamento inteligente** entre provedores

### 🔐 **Autenticação & Segurança**
- Autenticação **JWT** com refresh tokens
- **RBAC** (Role-Based Access Control)
- Gestão segura de **API keys** de provedores
- **Rate limiting** e throttling
- Logs de auditoria completos

### 💾 **Gestão de Dados**
- **PostgreSQL** como banco principal
- **Redis** para cache e sessões
- **Alembic** para migrações de schema
- Suporte a **workspaces** multi-tenant
- **Backup automático** e recuperação

### 🔧 **APIs & Integrações**
- **REST API** completa com FastAPI
- **WebSocket** para chat em tempo real
- **Webhooks** para eventos assíncronos
- **Upload/download** de arquivos
- Integração com **storage** externo

### 📊 **Monitoramento & Analytics**
- **Métricas** de uso e performance
- **Logs centralizados** com Loki/Grafana
- **Health checks** automatizados
- **Alertas** configuráveis
- Dashboard de **analytics**

---

## 🏗️ Arquitetura

```
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│   Frontend/Client   │────│   SynapScale API    │────│   LLM Providers     │
│                     │    │   (FastAPI)         │    │   (OpenAI, Claude)  │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
                                      │
                           ┌─────────────────────┐
                           │   Database Layer    │
                           │ (PostgreSQL+Redis)  │
                           └─────────────────────┘
```

### 🗂️ **Estrutura do Projeto**
```
synapse-backend-agents-jc/
├── src/synapse/           # Código fonte principal
│   ├── api/              # Endpoints da API
│   ├── core/             # Configurações e utilidades
│   ├── models/           # Modelos do banco de dados
│   ├── schemas/          # Schemas Pydantic
│   └── services/         # Lógica de negócio
├── docs/                 # Documentação
├── tests/                # Testes automatizados
├── deployment/           # Configurações de deploy
├── alembic/              # Migrações de banco
└── tools/                # Scripts utilitários
```

---

## ⚡ Início Rápido

### 1️⃣ **Clone o Repositório**
```bash
git clone <repository-url>
cd synapse-backend-agents-jc
```

### 2️⃣ **Configure o Ambiente**
```bash
# Copie e configure as variáveis de ambiente
cp .env.example .env
# Edite .env com suas configurações
```

### 3️⃣ **Execute com Docker (Recomendado)**
```bash
# Suba toda a stack
docker-compose up -d

# A API estará disponível em http://localhost:8000
```

### 4️⃣ **Ou Execute Localmente**
```bash
# Instale dependências
pip install -r requirements.txt

# Execute migrações
alembic upgrade head

# Inicie o servidor
./dev.sh
```

### 5️⃣ **Teste a API**
```bash
# Health check
curl http://localhost:8000/health

# Documentação interativa
open http://localhost:8000/docs
```

---

## 🔧 Instalação

### **Pré-requisitos**
- **Python 3.11+**
- **PostgreSQL 13+**
- **Redis 6+**
- **Docker** (opcional, mas recomendado)

### **Método 1: Instalação Local**

1. **Clone e entre no diretório:**
   ```bash
   git clone <repository-url>
   cd synapse-backend-agents-jc
   ```

2. **Crie ambiente virtual:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # ou
   venv\Scripts\activate     # Windows
   ```

3. **Instale dependências:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure banco de dados:**
   ```bash
   # Configure PostgreSQL e Redis
   # Edite .env com as credenciais corretas
   ```

5. **Execute migrações:**
   ```bash
   alembic upgrade head
   ```

### **Método 2: Docker (Recomendado)**

1. **Clone o repositório:**
   ```bash
   git clone <repository-url>
   cd synapse-backend-agents-jc
   ```

2. **Configure variáveis:**
   ```bash
   cp .env.example .env
   # Edite .env conforme necessário
   ```

3. **Execute com Docker:**
   ```bash
   docker-compose up -d
   ```

### **Método 3: Deploy em Nuvem**

- **Render**: Siga o guia em [`docs/deployment/render_guide.md`](docs/deployment/render_guide.md)
- **AWS/GCP**: Configurações em [`deployment/`](deployment/)

---

## ⚙️ Configuração

### **Variáveis de Ambiente Essenciais**

```bash
# Banco de Dados
DATABASE_URL=postgresql://user:pass@localhost:5432/synapscale
REDIS_URL=redis://localhost:6379

# Autenticação
JWT_SECRET_KEY=your-super-secret-key
JWT_ALGORITHM=HS256

# LLM Providers (configure conforme necessário)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...

# Configurações da Aplicação
DEBUG=false
LOG_LEVEL=INFO
CORS_ORIGINS=["*"]
```

### **Arquivo de Configuração**

Veja o exemplo completo em [`.env.example`](.env.example) e a documentação detalhada em [`docs/configuration/`](docs/configuration/).

---

## 📖 API Reference

### **Endpoints Principais**

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/health` | Health check do sistema |
| `POST` | `/auth/login` | Autenticação de usuário |
| `POST` | `/llm/chat` | Chat com LLMs |
| `GET` | `/workspaces` | Listar workspaces |
| `POST` | `/files/upload` | Upload de arquivos |

### **Documentação Interativa**

- **Swagger UI**: [`http://localhost:8000/docs`](http://localhost:8000/docs)
- **ReDoc**: [`http://localhost:8000/redoc`](http://localhost:8000/redoc)
- **OpenAPI JSON**: [`http://localhost:8000/openapi.json`](http://localhost:8000/openapi.json)

### **Guias Detalhados**

- 📘 [**Guia de Autenticação**](docs/api/authentication_guide.md)
- 🤖 [**Integração LLM**](docs/api/llm/integration_guide.md)
- 📁 [**Gestão de Arquivos**](docs/api/files_endpoints.md)
- 📊 [**Analytics**](docs/api/analytics_endpoints.md)

---

## 🛠️ Desenvolvimento

### **Scripts de Desenvolvimento**

```bash
# Servidor de desenvolvimento com hot-reload
./dev.sh

# Executar todos os testes
pytest

# Linting e formatação
black src/
flake8 src/

# Migrações de banco
alembic revision --autogenerate -m "Nova migração"
alembic upgrade head
```

### **Estrutura de Desenvolvimento**

```bash
src/synapse/
├── api/v1/endpoints/     # Endpoints da API v1
├── core/                 # Configurações centrais
│   ├── config.py        # Configurações da aplicação
│   ├── auth/            # Sistema de autenticação
│   └── services/        # Serviços base
├── models/              # Modelos SQLAlchemy
├── schemas/             # Schemas Pydantic
└── services/            # Lógica de negócio
```

### **Padrões de Código**

- **Arquitetura**: Clean Architecture com Repository Pattern
- **Async/Await**: Para operações I/O
- **Type Hints**: Em todo o código Python
- **Documentação**: Docstrings seguindo padrão Google
- **Testes**: Coverage mínimo de 80%

---

## 🧪 Testes

### **Executar Testes**

```bash
# Todos os testes
pytest

# Testes específicos
pytest tests/unit/
pytest tests/integration/

# Com coverage
pytest --cov=src/synapse --cov-report=html

# Testes de performance
pytest tests/performance/
```

### **Tipos de Teste**

- **Unit**: Testes unitários das funções e classes
- **Integration**: Testes de integração entre componentes
- **API**: Testes dos endpoints da API
- **Performance**: Testes de carga e stress

### **Configuração de Teste**

```bash
# Banco de teste
export DATABASE_URL=postgresql://test:test@localhost:5432/test_db

# Redis de teste
export REDIS_URL=redis://localhost:6379/1
```

---

## 🚀 Deploy

### **Ambientes Suportados**

- **Desenvolvimento**: Local com `./dev.sh`
- **Staging**: Docker Compose
- **Produção**: Render, AWS, GCP, Azure

### **Deploy com Docker**

```bash
# Build da imagem
docker build -t synapscale-backend .

# Deploy em produção
docker-compose -f deployment/docker/docker-compose.yml up -d
```

### **Deploy no Render**

1. Conecte o repositório ao Render
2. Configure as variáveis de ambiente
3. Siga o guia: [`docs/deployment/render_guide.md`](docs/deployment/render_guide.md)

### **Configurações de Produção**

- **SSL/TLS**: Configurado automaticamente
- **Logs**: Centralizados com Loki/Grafana
- **Monitoring**: Health checks e métricas
- **Backup**: Automático do PostgreSQL
- **Scaling**: Auto-scaling configurável

---

## 🤝 Contribuição

### **Como Contribuir**

1. **Fork** o repositório
2. **Crie** uma branch feature (`git checkout -b feature/nova-funcionalidade`)
3. **Commit** suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. **Push** para a branch (`git push origin feature/nova-funcionalidade`)
5. **Abra** um Pull Request

### **Diretrizes**

- **Código**: Siga os padrões estabelecidos
- **Testes**: Adicione testes para novas funcionalidades
- **Documentação**: Atualize docs quando necessário
- **Commits**: Use mensagens claras e descritivas

### **Desenvolvimento Local**

```bash
# Setup para contribuição
git clone <your-fork>
cd synapse-backend-agents-jc
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pre-commit install
```

Veja mais detalhes em [`CONTRIBUTING.md`](docs/CONTRIBUTING.md).

---

## 🆘 Suporte

### **Documentação**

- 📚 **Documentação Completa**: [`docs/`](docs/)
- 🚀 **Setup Guide**: [`docs/SETUP_GUIDE.md`](docs/SETUP_GUIDE.md)
- 🔧 **API Guide**: [`docs/api/API_GUIDE.md`](docs/api/API_GUIDE.md)
- 🐛 **Troubleshooting**: [`docs/troubleshooting/`](docs/troubleshooting/)

### **Comunidade**

- **Issues**: [GitHub Issues](../../issues)
- **Discussions**: [GitHub Discussions](../../discussions)
- **Wiki**: [Project Wiki](../../wiki)

---

## 📄 Licença

Este projeto está licenciado sob a **MIT License** - veja o arquivo [LICENSE](LICENSE) para detalhes.

---

## 🏆 Stack Tecnológico

<div align="center">

| Categoria | Tecnologias |
|-----------|-------------|
| **Backend** | ![Python](https://img.shields.io/badge/-Python-3776AB?logo=python&logoColor=white) ![FastAPI](https://img.shields.io/badge/-FastAPI-009688?logo=fastapi&logoColor=white) |
| **Database** | ![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-336791?logo=postgresql&logoColor=white) ![Redis](https://img.shields.io/badge/-Redis-DC382D?logo=redis&logoColor=white) |
| **AI/ML** | ![OpenAI](https://img.shields.io/badge/-OpenAI-412991?logo=openai&logoColor=white) ![Anthropic](https://img.shields.io/badge/-Anthropic-D4AF37?logoColor=white) |
| **DevOps** | ![Docker](https://img.shields.io/badge/-Docker-2496ED?logo=docker&logoColor=white) ![GitHub Actions](https://img.shields.io/badge/-GitHub%20Actions-2088FF?logo=github-actions&logoColor=white) |
| **Monitoring** | ![Grafana](https://img.shields.io/badge/-Grafana-F46800?logo=grafana&logoColor=white) ![Loki](https://img.shields.io/badge/-Loki-F46800?logoColor=white) |

</div>

---

<div align="center">

**⭐ Se este projeto foi útil, considere dar uma estrela!**

[![GitHub stars](https://img.shields.io/github/stars/username/repo?style=social)](../../stargazers)
[![GitHub forks](https://img.shields.io/github/forks/username/repo?style=social)](../../network/members)

</div> 