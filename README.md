# SynapScale Backend

## Visão Geral

SynapScale é uma plataforma robusta para integração com múltiplos provedores de LLM (Large Language Models), projetada para oferecer uma infraestrutura escalável e segura para aplicações baseadas em IA. Esta implementação segue uma arquitetura de microserviços, com foco inicial no serviço de uploads.

## Arquitetura

O backend SynapScale foi desenvolvido seguindo princípios de design modernos:

- **Arquitetura Modular**: Componentes desacoplados e reutilizáveis
- **API RESTful**: Endpoints bem definidos com documentação OpenAPI
- **Segurança**: Autenticação JWT, validação de arquivos, rate limiting
- **Escalabilidade**: Preparado para crescimento com banco de dados assíncrono
- **Observabilidade**: Logging estruturado e monitoramento

## Tecnologias

- **FastAPI**: Framework web de alta performance
- **SQLAlchemy**: ORM para interação com banco de dados
- **Pydantic**: Validação de dados e serialização
- **PostgreSQL**: Banco de dados relacional
- **Redis**: Cache e rate limiting
- **JWT**: Autenticação e autorização

## Estrutura do Projeto

```
synapse-backend/
├── README.md                     # Documentação principal
├── .env.example                  # Exemplo de variáveis de ambiente
├── pyproject.toml                # Configuração do projeto
├── alembic.ini                   # Configuração de migrações
├── docker-compose.yml            # Configuração Docker
├── Dockerfile                    # Instruções para build
├── scripts/                      # Scripts utilitários
├── docs/                         # Documentação detalhada
├── tests/                        # Testes automatizados
└── src/                          # Código-fonte
    └── synapse/                  # Pacote principal
        ├── config.py             # Configurações centralizadas
        ├── constants.py          # Constantes compartilhadas
        ├── exceptions.py         # Exceções personalizadas
        ├── logging.py            # Configuração de logging
        ├── main.py               # Ponto de entrada
        ├── middlewares/          # Middlewares
        ├── core/                 # Componentes centrais
        │   ├── auth/             # Autenticação
        │   ├── security/         # Segurança
        │   └── storage/          # Armazenamento
        ├── db/                   # Banco de dados
        ├── models/               # Modelos SQLAlchemy
        ├── schemas/              # Schemas Pydantic
        ├── api/                  # Rotas da API
        │   └── v1/               # API versão 1
        ├── services/             # Serviços de negócio
        └── utils/                # Utilitários
```

## Instalação

### Pré-requisitos

- Python 3.9+
- PostgreSQL
- Redis (opcional, para rate limiting)

### Configuração

1. Clone o repositório:
   ```bash
   git clone https://github.com/synapscale/synapse-backend.git
   cd synapse-backend
   ```

2. Crie e ative um ambiente virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # ou
   venv\Scripts\activate  # Windows
   ```

3. Instale as dependências:
   ```bash
   pip install -e .
   ```

4. Configure as variáveis de ambiente:
   ```bash
   cp .env.example .env
   # Edite o arquivo .env com suas configurações
   ```

5. Execute as migrações do banco de dados:
   ```bash
   alembic upgrade head
   ```

### Execução

Para iniciar o servidor em modo de desenvolvimento:

```bash
uvicorn src.synapse.main:app --reload
```

Para produção, recomendamos usar Gunicorn com workers Uvicorn:

```bash
gunicorn -k uvicorn.workers.UvicornWorker -w 4 src.synapse.main:app
```

## Uso da API

### Autenticação

Todas as requisições (exceto health check) requerem autenticação via token JWT no header:

```
Authorization: Bearer <token>
```

### Endpoints Principais

#### Upload de Arquivo

```http
POST /api/v1/files/upload
Content-Type: multipart/form-data

file: <arquivo>
category: document
tags: relatório,financeiro
description: Relatório financeiro anual
is_public: false
```

#### Listar Arquivos

```http
GET /api/v1/files?page=1&size=10&category=document
```

#### Obter Informações do Arquivo

```http
GET /api/v1/files/{file_id}
```

#### Gerar URL de Download

```http
GET /api/v1/files/{file_id}/download
```

#### Atualizar Informações do Arquivo

```http
PATCH /api/v1/files/{file_id}
Content-Type: application/json

{
  "tags": ["relatório", "financeiro", "2023"],
  "description": "Relatório financeiro anual atualizado",
  "is_public": true
}
```

#### Remover Arquivo

```http
DELETE /api/v1/files/{file_id}
```

## Documentação da API

A documentação completa da API está disponível em:

- Swagger UI: `/docs`
- ReDoc: `/redoc`

## Desenvolvimento

### Testes

Para executar os testes:

```bash
pytest
```

Para verificar a cobertura:

```bash
pytest --cov=src
```

### Migrações

Para criar uma nova migração:

```bash
alembic revision --autogenerate -m "descrição da migração"
```

Para aplicar migrações:

```bash
alembic upgrade head
```

## Licença

Este projeto está licenciado sob os termos da licença MIT.
