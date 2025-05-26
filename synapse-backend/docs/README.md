# SynapScale Backend

![SynapScale Logo](https://via.placeholder.com/150x50?text=SynapScale)

## Visão Geral

O SynapScale é uma plataforma backend robusta e escalável para integração com múltiplos provedores de LLM (Large Language Models). Projetado com arquitetura modular e orientada a microsserviços, o SynapScale permite que aplicações frontend se comuniquem de forma unificada com diversos modelos de IA, incluindo OpenAI, Anthropic Claude, Google Gemini, Mistral AI e outros.

### Principais Características

- **Arquitetura de Microsserviços**: Componentes isolados e independentes para maior resiliência e escalabilidade
- **Multi-LLM**: Suporte a múltiplos provedores de LLM com interface unificada
- **Segurança Robusta**: Autenticação JWT, validação de escopos e rate limiting
- **Streaming de Respostas**: Suporte a streaming para experiência de usuário aprimorada
- **Mecanismo de Fallback**: Redirecionamento automático para provedores alternativos em caso de falha
- **Upload Seguro**: Sistema de upload de arquivos com validação rigorosa e sanitização
- **Marketplace de Ferramentas**: Gerenciamento de ferramentas (tools) para agentes de IA
- **Orquestração de Agentes**: Coordenação de múltiplos agentes especializados

## Arquitetura

O SynapScale segue uma arquitetura de microsserviços, com componentes independentes que se comunicam via API REST. O sistema é composto pelos seguintes componentes principais:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│  Frontend App   │────▶│   API Gateway   │────▶│  Auth Service   │
│                 │     │                 │     │                 │
└─────────────────┘     └────────┬────────┘     └─────────────────┘
                                 │
                                 ▼
         ┌───────────────────────┬───────────────────────┐
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│   LLM Service   │     │  Chat Service   │     │ Upload Service  │
│                 │     │                 │     │                 │
└────────┬────────┘     └─────────────────┘     └─────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│                      LLM Provider Connectors                    │
│                                                                 │
├─────────────┬─────────────┬─────────────┬─────────────┬─────────┘
│             │             │             │             │
▼             ▼             ▼             ▼             ▼
OpenAI      Claude        Gemini       Mistral       Others
```

### Componentes Principais

#### API Gateway
- Ponto de entrada único para todas as requisições
- Roteamento para serviços apropriados
- Autenticação e autorização
- Rate limiting e proteção contra abusos

#### Serviço de Autenticação (Auth Service)
- Gerenciamento de usuários e permissões
- Emissão e validação de tokens JWT
- Controle de escopos e níveis de acesso

#### Serviço LLM (LLM Service)
- Interface unificada para múltiplos provedores de LLM
- Seleção dinâmica de modelos
- Mecanismo de fallback
- Gerenciamento de contexto e histórico

#### Serviço de Chat (Chat Service)
- Gerenciamento de conversas e mensagens
- Persistência de histórico
- Streaming de respostas
- Integração com ferramentas externas

#### Serviço de Upload (Upload Service)
- Gerenciamento seguro de uploads de arquivos
- Validação rigorosa de tipos MIME
- Sanitização de nomes de arquivos
- Armazenamento seguro e eficiente

#### Serviço de Marketplace (Marketplace Service)
- Gerenciamento de ferramentas para agentes
- Catálogo de capacidades disponíveis
- Controle de versões e compatibilidade

#### Serviço de Agentes (Agents Service)
- Orquestração de múltiplos agentes especializados
- Roteamento inteligente de tarefas
- Gerenciamento de estado e contexto

## Tecnologias Utilizadas

- **Backend**: Python 3.11+, FastAPI, SQLAlchemy
- **Banco de Dados**: PostgreSQL
- **Containerização**: Docker, Docker Compose
- **Autenticação**: JWT (JSON Web Tokens)
- **Documentação**: OpenAPI/Swagger
- **Testes**: Pytest, Pytest-asyncio

## Instalação e Configuração

### Pré-requisitos

- Docker e Docker Compose
- Python 3.11 ou superior (para desenvolvimento local)
- Chaves de API para os provedores de LLM desejados

### Instalação com Docker (Recomendado)

1. Clone o repositório:
```bash
git clone https://github.com/synapscale/synapse-backend-agents-jc.git
cd synapse-backend-agents-jc
```

2. Configure as variáveis de ambiente:
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

3. Inicie os serviços com Docker Compose:
```bash
docker-compose up -d
```

4. Verifique se todos os serviços estão rodando:
```bash
docker-compose ps
```

### Instalação para Desenvolvimento Local

1. Clone o repositório:
```bash
git clone https://github.com/synapscale/synapse-backend-agents-jc.git
cd synapse-backend-agents-jc
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

4. Configure as variáveis de ambiente:
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

5. Inicie os serviços de banco de dados com Docker:
```bash
docker-compose up -d postgres
```

6. Execute as migrações do banco de dados:
```bash
alembic upgrade head
```

7. Inicie o servidor de desenvolvimento:
```bash
uvicorn api-gateway.main:app --reload
```

## Guia de Uso

### Autenticação

Todas as requisições à API (exceto endpoints públicos) requerem autenticação via token JWT. Para obter um token:

```bash
curl -X POST http://localhost:8000/api/auth/token \
  -H "Content-Type: application/json" \
  -d '{"username": "seu_usuario", "password": "sua_senha"}'
```

A resposta incluirá um token de acesso que deve ser incluído no header `Authorization` de todas as requisições subsequentes:

```bash
curl -X GET http://localhost:8000/api/llm/models \
  -H "Authorization: Bearer seu_token_aqui"
```

### Exemplos de Uso

#### Listar Modelos Disponíveis

```bash
curl -X GET http://localhost:8000/api/llm/models \
  -H "Authorization: Bearer seu_token_aqui"
```

#### Enviar Mensagem para Chat

```bash
curl -X POST http://localhost:8000/api/chat/messages \
  -H "Authorization: Bearer seu_token_aqui" \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "conv_123",
    "content": "Qual é a capital do Brasil?",
    "model": "gpt-4",
    "stream": false
  }'
```

#### Upload de Arquivo

```bash
curl -X POST http://localhost:8000/api/uploads \
  -H "Authorization: Bearer seu_token_aqui" \
  -F "file=@/caminho/para/seu/arquivo.pdf" \
  -F "description=Documento importante"
```

### Streaming de Respostas

Para receber respostas em streaming, defina o parâmetro `stream` como `true` e processe a resposta como um stream de eventos:

```javascript
// Exemplo em JavaScript
fetch('http://localhost:8000/api/chat/messages', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer seu_token_aqui',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    conversation_id: 'conv_123',
    content: 'Explique o conceito de inteligência artificial',
    model: 'gpt-4',
    stream: true
  })
})
.then(response => {
  const reader = response.body.getReader();
  const decoder = new TextDecoder();

  function processStream({ done, value }) {
    if (done) return;

    const chunk = decoder.decode(value);
    const lines = chunk.split('\n').filter(line => line.trim() !== '');

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const data = JSON.parse(line.substring(6));
        console.log(data.content);
      }
    }

    return reader.read().then(processStream);
  }

  return reader.read().then(processStream);
});
```

## Monitoramento e Logs

### Visualização de Logs

Para visualizar os logs de todos os serviços:

```bash
docker-compose logs -f
```

Para visualizar logs de um serviço específico:

```bash
docker-compose logs -f api-gateway
```

### Verificação de Saúde

Endpoint de verificação de saúde do sistema:

```bash
curl http://localhost:8000/health
```

## Solução de Problemas

### Problemas Comuns

#### Erro de Conexão com o Banco de Dados

Verifique se o serviço PostgreSQL está rodando:

```bash
docker-compose ps postgres
```

Se não estiver, inicie-o:

```bash
docker-compose up -d postgres
```

#### Erro de Autenticação

Verifique se o token JWT é válido e não expirou. Obtenha um novo token se necessário.

#### Erro de Rate Limiting

Se receber um erro 429 (Too Many Requests), aguarde o período de cooldown antes de tentar novamente.

## Recursos Adicionais

- [Documentação da API](http://localhost:8000/docs)
- [Guia de Contribuição](./CONTRIBUTING.md)
- [Changelog](./CHANGELOG.md)

## Licença

Este projeto está licenciado sob a [MIT License](./LICENSE).
