# Memory Bank

Sistema de armazenamento e recuperação de memórias para o SynapScale Backend.

## Descrição

O Memory Bank é um módulo para o SynapScale Backend que permite armazenar e recuperar memórias em formato vetorial, utilizando técnicas de embeddings e busca semântica. Ele é projetado para ser integrado facilmente ao SynapScale Backend, fornecendo uma API para gerenciar coleções de memórias e realizar buscas semânticas.

## Funcionalidades

- Criação e gerenciamento de coleções de memórias
- Armazenamento de memórias com metadados
- Geração de embeddings para busca semântica
- Busca por similaridade semântica
- Integração com o SynapScale Backend

## Instalação

Para instalar o Memory Bank, execute o script de instalação:

```bash
./install_memory_bank.sh
```

Este script irá:
1. Instalar o Memory Bank em modo de desenvolvimento
2. Executar as migrações para criar as tabelas no banco de dados
3. Configurar as variáveis de ambiente necessárias

## Uso

Para executar o SynapScale Backend com o Memory Bank integrado, use:

```bash
python run_with_memory_bank.py
```

Ou configure a variável de ambiente `ENABLE_MEMORY_BANK=true` antes de iniciar o SynapScale Backend normalmente.

## API

O Memory Bank expõe os seguintes endpoints:

### Coleções

- `GET /api/v1/memory-bank/collections` - Listar todas as coleções
- `POST /api/v1/memory-bank/collections` - Criar uma nova coleção
- `GET /api/v1/memory-bank/collections/{collection_id}` - Obter detalhes de uma coleção
- `PUT /api/v1/memory-bank/collections/{collection_id}` - Atualizar uma coleção
- `DELETE /api/v1/memory-bank/collections/{collection_id}` - Excluir uma coleção

### Memórias

- `GET /api/v1/memory-bank/collections/{collection_id}/memories` - Listar memórias de uma coleção
- `POST /api/v1/memory-bank/collections/{collection_id}/memories` - Adicionar uma memória a uma coleção
- `GET /api/v1/memory-bank/memories/{memory_id}` - Obter detalhes de uma memória
- `PUT /api/v1/memory-bank/memories/{memory_id}` - Atualizar uma memória
- `DELETE /api/v1/memory-bank/memories/{memory_id}` - Excluir uma memória
- `POST /api/v1/memory-bank/collections/{collection_id}/search` - Buscar memórias por similaridade semântica

## Configuração

O Memory Bank pode ser configurado através das seguintes variáveis de ambiente:

- `ENABLE_MEMORY_BANK` - Habilitar ou desabilitar o Memory Bank (true/false)
- `MEMORY_BANK_EMBEDDING_MODEL` - Modelo de embedding a ser utilizado (padrão: all-MiniLM-L6-v2)
- `MEMORY_BANK_VECTOR_STORE` - Armazenamento vetorial a ser utilizado (padrão: faiss)
- `MEMORY_BANK_MAX_MEMORIES` - Número máximo de memórias por coleção (padrão: 1000)

## Estrutura do Projeto

```
memory-bank/
├── api/                  # Endpoints da API
├── migrations/           # Scripts de migração do banco de dados
├── models/               # Modelos SQLAlchemy
├── schemas/              # Schemas Pydantic
├── services/             # Serviços de negócio
├── utils/                # Utilitários
├── __init__.py           # Inicialização do módulo
├── integration.py        # Funções de integração com o SynapScale
├── run_migrations.py     # Script para executar migrações
└── setup.py              # Script de instalação
```

## Licença

MIT
