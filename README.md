# 🚀 SynapScale Backend - Sistema Completo de Automação com IA

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)](https://postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)
[![Tests](https://img.shields.io/badge/Tests-Passing-green.svg)](#testes)

## 📋 Visão Geral

O SynapScale Backend é uma plataforma completa de automação com IA que oferece:

- 🤖 **Agentes de IA Múltiplos** - OpenAI, Anthropic, Google, Groq, Grok, DeepSeek
- 🔄 **Workflows Visuais** - Sistema de nodes para automação
- 🔐 **Autenticação Robusta** - JWT com refresh tokens e 2FA
- 💾 **Banco PostgreSQL** - Com Prisma ORM e migrações Alembic
- 📁 **Gerenciamento de Arquivos** - Upload/download seguro
- 💬 **WebSockets** - Comunicação em tempo real
- 📊 **Analytics** - Métricas e monitoramento
- 🐳 **Docker Ready** - Containerização completa

## 🏗️ Arquitetura

```
src/synapse/
├── 🔌 api/                    # Endpoints da API
│   ├── v1/endpoints/          # Endpoints versionados
│   └── deps.py               # Dependências da API
├── ⚙️ core/                   # Funcionalidades centrais
│   ├── auth/                 # Autenticação e autorização
│   ├── config/               # Configurações
│   └── database/             # Conexão com banco
├── 🤖 models/                 # Modelos Pydantic
├── 🔧 services/               # Lógica de negócio
├── 📊 schemas/                # Schemas de validação
└── 🛠️ utils/                  # Utilitários
```

## 🚀 Início Rápido

### Pré-requisitos
- Python 3.11+
- PostgreSQL 15+
- Node.js 20+ (para Prisma)

### 1. Configuração do Ambiente
```bash
# Clone o repositório
git clone <repository-url>
cd synapscale-backend

# Execute o script de configuração
chmod +x setup_environment.sh
./setup_environment.sh
```

### 2. Configuração do Banco
```bash
# Configure as variáveis de ambiente
cp .env.example .env
# Edite o .env com suas configurações

# Execute as migrações
chmod +x apply_migrations.sh
./apply_migrations.sh
```

### 3. Iniciar o Servidor
```bash
# Desenvolvimento
./start_dev.sh

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

- **API Docs**: `/docs` (Swagger UI)
- **ReDoc**: `/redoc` (Documentação alternativa)
- **OpenAPI**: `/openapi.json` (Especificação)

### Documentação Técnica
- 📖 [Guia de Desenvolvimento](docs/development_guide.md)
- 🏗️ [Arquitetura](docs/architecture.md)
- 🔐 [Segurança](docs/security_production.md)
- 🚀 [Guia de Implantação](Guia%20de%20Implantação%20do%20Backend%20SynapScale.md)

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
```

## 🔧 Scripts Disponíveis

- `setup_environment.sh` - Configuração inicial completa
- `apply_migrations.sh` - Aplicar migrações do banco
- `start_dev.sh` - Iniciar em modo desenvolvimento
- `start.sh` - Iniciar em modo produção
- `scripts/run_tests.sh` - Executar testes
- `scripts/validate.sh` - Validação completa

## 🌟 Funcionalidades Principais

### 🤖 Agentes de IA
- Integração com múltiplos provedores
- Sistema de templates e prompts
- Execução paralela e assíncrona
- Marketplace de agentes

### 🔄 Workflows
- Editor visual de nodes
- Triggers automáticos
- Variáveis personalizadas
- Scheduling avançado

### 🔐 Autenticação
- JWT com refresh tokens
- Autenticação de dois fatores
- Sistema de permissões granular
- Rate limiting

### 📁 Arquivos
- Upload/download seguro
- Processamento de múltiplos formatos
- Versionamento automático
- Integração com storage cloud

### 💬 Comunicação
- WebSockets em tempo real
- Sistema de conversas
- Notificações push
- Chat com IA

### 📊 Analytics
- Métricas de performance
- Logs estruturados
- Dashboard de analytics
- Alertas automáticos

## 🔧 Configuração

### Variáveis de Ambiente Principais
```env
# Banco de Dados
DATABASE_URL=postgresql://user:pass@localhost:5432/synapscale_db

# Segurança
SECRET_KEY=your_secret_key_here
JWT_SECRET_KEY=your_jwt_secret_here

# APIs de IA
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
GOOGLE_API_KEY=your_google_key
```

## 📈 Performance

- **Async/Await** - Operações não-bloqueantes
- **Connection Pooling** - Otimização de banco
- **Caching** - Redis para cache
- **Rate Limiting** - Proteção contra abuso
- **Monitoring** - Métricas em tempo real

## 🛡️ Segurança

- **HTTPS** - Comunicação criptografada
- **CORS** - Configuração adequada
- **SQL Injection** - Proteção via ORM
- **XSS** - Sanitização de dados
- **Rate Limiting** - Proteção contra DDoS

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

- [ ] Integração com mais provedores de IA
- [ ] Sistema de plugins
- [ ] Interface web administrativa
- [ ] API GraphQL
- [ ] Clustering e alta disponibilidade

---

**Desenvolvido com ❤️ pela equipe SynapScale**

