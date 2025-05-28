# README.md - SynapScale Backend

## Visão Geral

SynapScale é um backend moderno e escalável para gerenciamento de arquivos e processamento de linguagem natural com múltiplos LLMs. O sistema oferece uma API RESTful completa, autenticação segura, gerenciamento de arquivos e integração com diversos provedores de modelos de linguagem.

## Principais Recursos

- **API RESTful**: Interface completa para todas as funcionalidades
- **Autenticação e Autorização**: Sistema seguro baseado em JWT
- **Gerenciamento de Arquivos**: Upload, download, listagem e metadados
- **Integração Multi-LLM**: Suporte a Claude, Gemini, Grok e DeepSeek
- **Cache Inteligente**: Redução de custos e latência para consultas repetidas
- **Documentação Completa**: Guias detalhados e referência de API
- **Testes Abrangentes**: Cobertura de testes unitários e de integração

## Estrutura do Projeto

```
src/
├── synapse/
│   ├── api/              # Endpoints da API
│   ├── core/             # Lógica de negócio central
│   │   ├── llm/          # Integração com LLMs
│   │   └── ...
│   ├── models/           # Modelos de dados
│   ├── schemas/          # Esquemas Pydantic
│   ├── utils/            # Utilitários
│   ├── config.py         # Configurações
│   └── main.py           # Ponto de entrada
├── tests/
│   ├── unit/             # Testes unitários
│   └── integration/      # Testes de integração
└── docs/                 # Documentação
    ├── api/              # Documentação da API
    │   ├── llm/          # Documentação de LLMs
    │   └── ...
    └── ...
```

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/synapscale/synapse-backend.git
cd synapse-backend
```

2. Crie e ative um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure o ambiente:
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

5. Execute as migrações:
```bash
alembic upgrade head
```

6. Inicie o servidor:
```bash
uvicorn src.synapse.main:app --reload
```

## Configuração de LLMs

Para utilizar os recursos de LLM, você precisa configurar as chaves de API dos provedores desejados no arquivo `.env`:

```
CLAUDE_API_KEY=sua_chave_api_claude_aqui
GEMINI_API_KEY=sua_chave_api_gemini_aqui
GROK_API_KEY=sua_chave_api_grok_aqui
DEEPSEEK_API_KEY=sua_chave_api_deepseek_aqui

LLM_DEFAULT_PROVIDER=claude
LLM_ENABLE_CACHE=true
LLM_CACHE_TTL=3600
```

## Documentação da API

A documentação interativa da API está disponível em:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testes

Execute os testes com:

```bash
pytest
```

Para verificar a cobertura de testes:

```bash
pytest --cov=src
```

## Licença

Este projeto está licenciado sob os termos da licença MIT.
