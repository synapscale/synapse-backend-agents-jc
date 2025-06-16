# 🚀 SynapScale Backend API

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13+-blue.svg)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-6+-red.svg)](https://redis.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> Plataforma de Automação com IA - Backend completo e otimizado para gerenciamento de workflows, agentes AI e automações empresariais.

## 📋 Sumário

1. [🏁 Início Rápido](#-início-rápido)
2. [🧩 Manutenção do Repositório](#-manutenção-do-repositório)
3. [🛠️ Instalação](#-instalação)
4. [⚙️ Configuração](#-configuração)
5. [🚀 Execução](#-execução)
6. [📁 Estrutura do Projeto](#-estrutura-do-projeto)
7. [🔍 Endpoints API](#-endpoints-api)
8. [🧪 Testes](#-testes)
9. [🚢 Deploy](#-deploy)
10. [📚 Documentação](#-documentação)

---

## 🏁 Início Rápido

Para iniciar rapidamente, execute:

```bash
# 1. Configuração inicial (uma vez)
./setup.sh

# 2. Configure o DATABASE_URL no arquivo .env

# 3. Inicie o servidor no modo desejado:
./dev.sh    # Desenvolvimento (com reload automático)
# ou
./prod.sh   # Produção (otimizado)
```

Depois acesse:

* API: [http://localhost:8000](http://localhost:8000)
* Documentação: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🧩 Manutenção do Repositório

Para manter o repositório organizado e atualizado:

```bash
# Analisar estrutura atual do repositório
./scripts/analyze_repository.sh

# Reorganizar e limpar arquivos antigos
./scripts/reorganize_repository.sh

# Limpar arquivos temporários e caches
./scripts/clean_temp_files.sh

# Validar mudanças feitas na organização
./scripts/validate_changes.sh
```

Os scripts acima ajudam a manter o código limpo, remover documentação antiga e garantir que a estrutura do projeto siga as melhores práticas.

### 📦 Organização do Repositório

O projeto foi reorganizado para seguir um padrão mais claro:

* **Um único arquivo `requirements.txt`**: Todas as dependências em um único arquivo na raiz
* **Arquivos `.env` padronizados**: Apenas `.env.example` (modelo) e `.env` (configuração real)
* **Scripts de setup simplificados**: `setup.sh` com modos básico e completo

Exemplos de uso dos scripts de setup:

```bash
# Setup rápido (manual)
./setup.sh

# Setup completo (automatizado)
./setup.sh --complete
```

---

## 🛠️ Instalação

### Pré-requisitos

* Python 3.11+
* PostgreSQL 13+
* Redis 6+ (opcional)

### Passo a passo

1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/synapscale-backend.git
   cd synapscale-backend
   ```

2. Execute o script de setup:
   ```bash
   ./setup.sh
   ```

   Este script automaticamente:
   * Cria ambiente virtual Python
   * Instala dependências
   * Configura diretórios
   * Prepara o arquivo .env
   * Gera chaves de segurança

---

## ⚙️ Configuração

### Arquivo .env

O arquivo mais importante para configurar é o `.env`. Após o setup inicial, você precisa configurar pelo menos:

1. **Configuração do banco de dados** (obrigatória):
   ```bash
   DATABASE_URL=postgresql://usuario:senha@localhost:5432/synapscale_db
   ```

2. **Outras configurações importantes** (opcionais):
   ```bash
   # API e servidor
   DEBUG=true
   PORT=8000
   
   # Segurança (geradas automaticamente pelo setup)
   SECRET_KEY=...
   JWT_SECRET_KEY=...
   
   # IA (configure suas chaves)
   OPENAI_API_KEY=sua_chave_openai
   ANTHROPIC_API_KEY=sua_chave_anthropic
   ```

Para configurações completas, veja o arquivo `.env.example`.

---

## 🚀 Execução

### Modo Desenvolvimento

```bash
./dev.sh
```

Características:
* Reload automático ao modificar código
* Modo debug ativo
* Logs detalhados

### Modo Produção

```bash
./prod.sh
```

Características:
* Workers otimizados (Gunicorn)
* Performance melhorada
* Logs estruturados

---

## 📁 Estrutura do Projeto

```
synapscale-backend/
├── config/             # Configurações (requirements, alembic)
├── deployment/         # Arquivos de deploy (Docker, render)
├── docs/               # Documentação do projeto
├── setup/              # Scripts de configuração
├── src/                # Código fonte principal
│   ├── synapse/        # Núcleo da aplicação
│   │   ├── api/        # Endpoints da API
│   │   ├── core/       # Núcleo (config, segurança)
│   │   ├── db/         # Modelos e conexão DB
│   │   ├── services/   # Serviços da aplicação
│   │   └── utils/      # Utilitários
├── tests/              # Testes automatizados
├── tools/              # Ferramentas e utilitários
├── .env                # Variáveis de ambiente (criar a partir do .env.example)
├── .env.example        # Exemplo de configuração
├── dev.sh              # Execução em desenvolvimento
├── prod.sh             # Execução em produção
└── setup.sh            # Script de configuração inicial
```

---

## 🔍 Endpoints API

Os principais endpoints disponíveis:

* `GET /api/v1/health` - Status da API
* `POST /api/v1/auth/login` - Autenticação
* `GET /api/v1/users/me` - Informações do usuário
* `POST /api/v1/workflows` - Criar workflow
* `GET /api/v1/agents` - Listar agentes

Documentação completa:
* Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
* ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 🧪 Testes

Para executar os testes automatizados:

```bash
# Testes unitários
python -m pytest

# Testes com cobertura
python -m pytest --cov=src

# Testes específicos
python -m pytest tests/test_auth.py
```

---

## 🚢 Deploy

### Opção 1: Docker

```bash
# Build da imagem
docker build -t synapscale-backend .

# Execução
docker run -p 8000:8000 --env-file .env synapscale-backend
```

### Opção 2: Render.com

O projeto inclui configuração para Render.com:
1. Configure seu repositório no Render
2. Selecione o arquivo `render.yaml`
3. Configure variáveis de ambiente
4. Deploy!

Instruções detalhadas em: `docs/deployment/RENDER_DEPLOY.md`

---

## 📚 Documentação

* **Guia do Desenvolvedor**: `docs/development_guide.md`
* **Arquitetura**: `docs/architecture.md`
* **API Guide**: `docs/api_guide.md`
* **Segurança**: `docs/security_production.md`

---

## 📄 Licença

Este projeto é licenciado sob os termos da licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

---

**SynapScale Backend** - Desenvolvido com ❤️ pela equipe SynapScale.

## ⚠️ Requisito Obrigatório

- **Python 3.11** (exclusivamente). Outras versões não são suportadas devido às dependências de ML.

---

## 🛠️ Instalação Recomendada

```bash
# 1. Remova ambientes virtuais antigos, se existirem
rm -rf venv .venv env ENV

# 2. Crie o ambiente virtual com Python 3.11
python3.11 -m venv venv
source venv/bin/activate

# 3. Atualize o pip
pip install --upgrade pip

# 4. Instale o torch antes das demais dependências
pip install torch

# 5. Instale as dependências do projeto
pip install -r requirements.txt

# 6. Configure o arquivo .env (obrigatório)
cp .env.example .env
# Edite o .env conforme necessário
```

> **Atenção:** Sempre ative o ambiente virtual com `source venv/bin/activate` antes de rodar scripts ou comandos Python.

---

## ❌ Não use outras versões de Python
- O projeto não funcionará corretamente com Python 3.12, 3.13 ou superior.
- Não utilize múltiplos ambientes virtuais. Use sempre o `venv` criado com Python 3.11.

---

## 🧩 Arquitetura dos Modelos Principais

- **Node**: Representa um componente reutilizável de workflow (ex: LLM, API, condição, etc).
- **WorkflowNode**: Representa uma instância de um Node dentro de um workflow específico.
- O relacionamento entre eles é bidirecional:
  - `Node.workflow_instances` lista todas as instâncias de um Node em workflows.
  - `WorkflowNode.node` referencia o Node base daquela instância.
- Isso permite flexibilidade e reuso de componentes em múltiplos workflows.

---

# Scripts e Utilitários

O repositório segue uma organização avançada para scripts e utilitários:

- **scripts/**: Scripts de manutenção, organização, validação e automação do repositório. Não execute em produção. Inclui scripts para limpeza, validação de migrations, organização de requirements, execução de testes automatizados, análise e reorganização do repositório.
- **tools/testing/**: Scripts de teste e diagnose (não rodados em produção).
- **tools/utilities/**: Utilitários de ambiente, segurança, geração de tokens, masking, etc.
- **tools/utils/**: Scripts de validação de setup, propagação de variáveis, etc.
- **tools/database/**: Scripts utilitários para manipulação de banco de dados (criação de usuários, schemas, checagens).
- **setup/templates/**: Templates de configuração (ex: .env.template). Agora realocados para docs/config-templates/.
- **docs/config-templates/**: Local central para templates de configuração e exemplos de arquivos de ambiente.

Cada subdiretório relevante possui um README próprio explicando o propósito dos scripts/utilitários daquele diretório.

Consulte cada script individualmente para instruções de uso.

---
