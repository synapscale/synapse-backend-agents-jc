# 🚀 SynapScale Backend API

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13+-blue.svg)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-6+-red.svg)](https://redis.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> Plataforma de Automação com IA - Backend completo e otimizado para gerenciamento de workflows, agentes AI e automações empresariais.

## 🎯 **COMEÇAR AQUI**

### 🚀 **[📋 GUIA DE INSTALAÇÃO](./docs/SETUP_GUIDE.md)**
**→ COMECE AQUI!** Guia completo para instalar e configurar o sistema.

### 📚 **[📖 DOCUMENTAÇÃO COMPLETA](./docs/README.md)**
**→ Navegue** por toda a documentação organizada.

---

## 🆕 **Novidades v1.1.0**

### 🔑 **Sistema de API Keys Específicas por Usuário**
- ✅ **6 Provedores Suportados**: OpenAI, Anthropic, Google, Grok, DeepSeek, Llama
- ✅ **Fallback Automático**: Usa chaves globais se usuário não configurou
- ✅ **Criptografia Segura**: Todas as chaves são criptografadas
- ✅ **[Documentação das API Keys](./docs/api/user_variables_api_keys_guide.md)**

### 🧪 **Sistema de Testes Unificado**
- ✅ **242 Endpoints Testados**: Descoberta automática via OpenAPI
- ✅ **Taxa de Sucesso 70.7%**: Monitoramento contínuo da qualidade
- 🚀 **Sistema LLM: 77.8%**: Performance superior do core LLM
- ✅ **Testes Automatizados**: Execução completa em ~2 minutos
- ✅ **[Documentação dos Testes](./DOCUMENTACAO_TESTES_ENDPOINTS.md)**
- 🤖 **[Teste LLM Detalhado](./TESTE_LLM_RESULTADO_DETALHADO.md)**

---

## ⚡ **Início Ultra-Rápido**

```bash
# 1. Clone e configure
git clone <URL_DO_REPOSITORIO>
cd synapse-backend-agents-jc
cp .env.example .env

# 2. Configure DATABASE_URL no .env

# 3. Instale e execute
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
./dev.sh
```

**Acesse**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 📋 **Documentação Principal**

### 🏗️ **Setup e Configuração**
- **[📋 Guia de Instalação](./docs/SETUP_GUIDE.md)** - Instalação completa
- **[🔧 Configuração Avançada](./docs/guides/development.md)** - Para desenvolvedores

### 📡 **API e Integração**
- **[📖 Guia da API](./docs/api/API_GUIDE.md)** - API completa
- **[⚡ Guia Rápido](./docs/api/quick_guide.md)** - Primeiros passos
- **[🤖 Integração LLM](./docs/llm_integration/integracao_multi_llm.md)** - IA

### 🛠️ **Desenvolvimento**
- **[💻 Guia de Desenvolvimento](./docs/guides/development.md)** - Para desenvolvedores
- **[🚀 Deploy](./docs/guides/DEPLOY-RENDER.md)** - Como fazer deploy
- **[🤝 Contribuição](./docs/CONTRIBUTING.md)** - Como contribuir

### 📊 **Recursos**
- **[🔄 Changelog](./docs/CHANGELOG.md)** - Histórico de mudanças
- **[🔒 Segurança](./docs/SECURITY.md)** - Diretrizes de segurança
- **[🏛️ Arquitetura](./docs/architecture/overview.md)** - Visão geral

---

## 🚀 **Características Principais**

- **🤖 IA Multi-Provedor**: OpenAI, Anthropic, Google, Grok, DeepSeek, Llama
- **⚡ FastAPI**: Performance otimizada e documentação automática
- **🔐 Segurança**: JWT, rate limiting, validação robusta
- **📊 Analytics**: Monitoramento e métricas integradas
- **🌐 WebSocket**: Comunicação em tempo real
- **📁 Gerenciamento de Arquivos**: Upload e processamento
- **🔄 Workflows**: Automação de processos
- **🏪 Marketplace**: Templates e componentes
- **👥 Multi-usuário**: Workspaces e permissões

---

## 🛠️ **Tecnologias**

- **Backend**: Python 3.11, FastAPI, SQLAlchemy
- **Banco de Dados**: PostgreSQL, Redis
- **IA**: OpenAI, Anthropic, Google AI
- **Deploy**: Docker, Render, Nginx
- **Testes**: Pytest, Coverage
- **Docs**: Swagger/OpenAPI

---

## 📈 **Status do Projeto**

- ✅ **Produção**: Estável e testado
- ✅ **API**: Documentação completa
- ✅ **Testes**: Cobertura abrangente
- ✅ **Deploy**: Pronto para produção
- ✅ **Segurança**: Implementada
- ✅ **Monitoramento**: Configurado

---

## 🆘 **Ajuda Rápida**

- **🚨 Problema na instalação?** → [SETUP_GUIDE.md](./docs/SETUP_GUIDE.md)
- **❓ Dúvida sobre a API?** → [API_GUIDE.md](./docs/api/API_GUIDE.md)
- **🐛 Encontrou um bug?** → [Issues](https://github.com/seu-usuario/synapse-backend/issues)
- **💡 Quer contribuir?** → [CONTRIBUTING.md](./docs/CONTRIBUTING.md)

---

## 📜 **Licença**

Este projeto está licenciado sob a [Licença MIT](./LICENSE).

---

**Última atualização**: Dezembro 2024  
**Versão**: 1.1.0  
**Desenvolvido com** ❤️ **pela equipe SynapScale**
