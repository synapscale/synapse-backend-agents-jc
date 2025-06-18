# Documentação da API de LLMs

## Visão Geral

A API de LLMs do SynapScale permite integrar múltiplos provedores de modelos de linguagem através de uma interface unificada. Esta abordagem oferece várias vantagens:

- **Flexibilidade**: Escolha o provedor mais adequado para cada caso de uso
- **Resiliência**: Fallback automático entre provedores em caso de falha
- **Extensibilidade**: Facilidade para adicionar novos provedores
- **Consistência**: Interface padronizada independente do provedor
- **🔑 API Keys Personalizadas**: Usuários podem configurar suas próprias API keys para cada provedor

## 🔑 Sistema de API Keys Específicas por Usuário

### Funcionalidade Principal

O sistema permite que cada usuário configure suas próprias API keys para os provedores LLM, oferecendo:

- ✅ **API Keys Personalizadas**: Cada usuário pode usar suas próprias chaves
- ✅ **Fallback Automático**: Se o usuário não tem API key configurada, usa a chave global do sistema
- ✅ **Criptografia Segura**: Todas as API keys são criptografadas com Fernet
- ✅ **Transparência Total**: Endpoints LLM funcionam normalmente, mas usam chaves específicas automaticamente

### Provedores Suportados

- **OpenAI** (`openai`) - GPT-4, GPT-3.5-turbo, etc.
- **Anthropic** (`anthropic`) - Claude 3 Opus, Sonnet, Haiku
- **Google** (`google`) - Gemini 1.5 Pro, Gemini Pro
- **Grok** (`grok`) - Grok-1, Grok-2
- **DeepSeek** (`deepseek`) - DeepSeek Coder, Chat
- **Llama** (`llama`) - Llama 2, Code Llama

### Como Funciona

1. **Usuário configura API key**: `POST /api/v1/user-variables/api-keys/openai`
2. **Sistema armazena criptografada**: Na tabela `user_variables` com `category="api_keys"`
3. **Uso automático**: Quando usuário chama `/api/v1/llm/generate`, sistema usa sua API key automaticamente
4. **Fallback**: Se usuário não tem API key, usa a chave global do sistema

## Endpoints Disponíveis

### Geração de Texto

```
POST /api/v1/llm/generate
```

Gera texto a partir de um prompt usando o provedor padrão ou especificado.

> 🔑 **API Keys Automáticas**: Este endpoint usa automaticamente a API key específica do usuário se configurada, ou fallback para a chave global do sistema.

**Parâmetros do Corpo**:
- `prompt` (string, obrigatório): Texto de entrada para o modelo
- `provider` (string, opcional): Provedor de LLM a ser usado
- `model` (string, opcional): Modelo específico a ser usado
- `max_tokens` (integer, opcional): Número máximo de tokens a gerar
- `temperature` (float, opcional): Temperatura para amostragem (0.0-1.0)
- `top_p` (float, opcional): Valor de top-p para amostragem nucleus
- `top_k` (integer, opcional): Valor de top-k para amostragem
- `use_cache` (boolean, opcional): Se deve usar o cache (se disponível)

**Exemplo de Requisição**:
```json
{
  "prompt": "Explique o conceito de machine learning em termos simples.",
  "provider": "claude",
  "model": "claude-3-sonnet-20240229",
  "max_tokens": 500,
  "temperature": 0.7
}
```

**Exemplo de Resposta**:
```json
{
  "text": "Machine learning é como ensinar um computador a aprender com exemplos, em vez de programá-lo com regras específicas...",
  "provider": "claude",
  "model": "claude-3-sonnet-20240229",
  "execution_time": 2.45,
  "cached": false
}
```

### Contagem de Tokens

```
POST /api/v1/llm/count-tokens
```

Conta o número de tokens em um texto.

**Parâmetros do Corpo**:
- `text` (string, obrigatório): Texto para contar tokens
- `provider` (string, opcional): Provedor de LLM a ser usado
- `model` (string, opcional): Modelo específico a ser usado

**Exemplo de Requisição**:
```json
{
  "text": "Este é um exemplo de texto para contar tokens.",
  "provider": "claude"
}
```

**Exemplo de Resposta**:
```json
{
  "token_count": 12,
  "provider": "claude",
  "model": "claude-3-sonnet-20240229"
}
```

### Listagem de Modelos

```
GET /api/v1/llm/models
```

Lista todos os modelos disponíveis em todos os provedores configurados.

**Parâmetros de Query**:
- `provider` (string, opcional): Filtrar por provedor específico

**Exemplo de Resposta**:
```json
{
  "providers": {
    "claude": {
      "available": true,
      "models": [
        {
          "id": "claude-3-opus-20240229",
          "name": "Claude 3 Opus",
          "context_window": 200000,
          "capabilities": ["text-generation", "image-understanding", "reasoning"]
        },
        {
          "id": "claude-3-sonnet-20240229",
          "name": "Claude 3 Sonnet",
          "context_window": 200000,
          "capabilities": ["text-generation", "image-understanding"]
        }
      ]
    },
    "gemini": {
      "available": true,
      "models": [
        {
          "id": "gemini-1.5-pro-latest",
          "name": "Gemini 1.5 Pro",
          "context_window": 1000000,
          "capabilities": ["text-generation", "image-understanding", "code-generation"]
        }
      ]
    }
  }
}
```

### Listagem de Provedores

```
GET /api/v1/llm/providers
```

Lista todos os provedores disponíveis e suas capacidades.

**Exemplo de Resposta**:
```json
{
  "providers": [
    {
      "name": "claude",
      "available": true,
      "capabilities": ["text-generation", "image-understanding"],
      "default_model": "claude-3-sonnet-20240229"
    },
    {
      "name": "gemini",
      "available": true,
      "capabilities": ["text-generation", "image-understanding", "code-generation"],
      "default_model": "gemini-1.5-pro-latest"
    }
  ],
  "default_provider": "claude"
}
```

### Endpoints Específicos de Provedores

Além dos endpoints genéricos, cada provedor tem endpoints específicos:

```
POST /api/v1/llm/{provider}/generate
POST /api/v1/llm/{provider}/count-tokens
GET /api/v1/llm/{provider}/models
```

Estes endpoints funcionam da mesma forma que os genéricos, mas garantem o uso de um provedor específico.

## Códigos de Erro

| Código | Descrição | Solução |
|--------|-----------|---------|
| 401 | Não autorizado | Verifique o token de autenticação |
| 403 | Acesso negado | Verifique as permissões do usuário |
| 404 | Recurso não encontrado | Verifique o caminho da URL |
| 422 | Erro de validação | Verifique os parâmetros da requisição |
| 500 | Erro interno do servidor | Verifique os logs do servidor |

## 🔑 Gerenciamento de API Keys de Usuário

### Configurar API Key

```http
POST /api/v1/user-variables/api-keys/{provider}
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "value": "sk-1234567890abcdef"
}
```

**Provedores suportados**: `openai`, `anthropic`, `google`, `grok`, `deepseek`, `llama`

### Listar API Keys

```http
GET /api/v1/user-variables/api-keys
Authorization: Bearer <access_token>
```

**Resposta** (valores mascarados para segurança):
```json
[
  {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "provider_name": "openai",
    "key_name": "OPENAI_API_KEY",
    "masked_value": "****cdef",
    "is_active": true,
    "description": "Chave da API OpenAI",
    "created_at": "2025-06-18T10:30:00Z",
    "updated_at": "2025-06-18T10:30:00Z"
  }
]
```

### Remover API Key

```http
DELETE /api/v1/user-variables/api-keys/{provider}
Authorization: Bearer <access_token>
```

### Listar Provedores Suportados

```http
GET /api/v1/user-variables/api-keys/providers
```

## Limitações Conhecidas

- **Rate Limiting**: Todos os provedores impõem limites de requisições por minuto
- **Custo**: Chamadas às APIs externas geram custos baseados em tokens processados
- **Latência**: Respostas podem levar vários segundos, especialmente para prompts longos
- **Conteúdo**: Alguns provedores filtram certos tipos de conteúdo
- **Multimodalidade**: Nem todos os provedores suportam processamento de imagens
- **🔑 API Keys**: Usuários devem configurar suas próprias API keys para usar provedores específicos (ou usar as chaves globais do sistema)
