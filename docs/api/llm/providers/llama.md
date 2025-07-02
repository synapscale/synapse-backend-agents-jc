# 🦙 Provedor LLaMA (Meta) - SynapScale

Esta documentação descreve como usar modelos LLaMA da Meta através da **API LLM unificada** do SynapScale Backend.

> **💡 Nota:** Use sempre a API unificada `/api/v1/llm/*` para melhor compatibilidade e recursos avançados.

## 🚀 Usando Modelos LLaMA

### **Endpoint Unificado**
```http
POST /api/v1/llm/generate
POST /api/v1/llm/chat
```

### **Modelos Disponíveis**
- `llama-3.1-405b-instruct` - Modelo mais avançado
- `llama-3.1-70b-instruct` - Balanceado
- `llama-3.1-8b-instruct` - Rápido
- `llama-3-70b-instruct` - Versão estável
- `llama-3-8b-instruct` - Eficiente

## 📝 Exemplos de Uso

### **Geração de Texto**

```bash
curl -X POST "http://localhost:8000/api/v1/llm/generate" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "llama",
    "model": "llama-3.1-70b-instruct",
    "prompt": "Explique o conceito de machine learning",
    "max_tokens": 500,
    "temperature": 0.7
  }'
```

### **Chat Conversacional**

```bash
curl -X POST "http://localhost:8000/api/v1/llm/chat" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "llama",
    "model": "llama-3.1-405b-instruct",
    "messages": [
      {"role": "system", "content": "Você é um assistente útil."},
      {"role": "user", "content": "Como posso melhorar meu código Python?"}
    ],
    "max_tokens": 1000,
    "temperature": 0.8
  }'
```

## ⚙️ Parâmetros Específicos do LLaMA

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `provider` | string | **Obrigatório**: `"llama"` |
| `model` | string | Modelo específico (ver lista acima) |
| `temperature` | float | 0.0-2.0, controla criatividade |
| `top_p` | float | 0.0-1.0, amostragem nucleus |
| `top_k` | integer | 1-100, limita vocabulário |
| `repetition_penalty` | float | 1.0-1.3, evita repetição |
| `system_prompt` | string | Prompt de sistema (chat) |

## 🔄 Resposta Típica

```json
{
  "text": "Machine learning é uma subárea da inteligência artificial...",
  "model": "llama-3.1-70b-instruct",
  "provider": "llama",
  "tokens_used": 245,
  "cost": 0.0012,
  "cached": false,
  "processing_time": 2.1,
  "finish_reason": "stop"
}
```

## 🎯 Casos de Uso Recomendados

### **LLaMA 3.1 405B**
- Análises complexas
- Raciocínio avançado
- Tarefas criativas sofisticadas

### **LLaMA 3.1 70B**
- Uso geral balanceado
- Conversas naturais
- Análise de código

### **LLaMA 3.1 8B**
- Respostas rápidas
- Tarefas simples
- Alto volume de requisições

## 🔧 Configuração de API Key

### **Usando API Key Global (Sistema)**
O sistema usará automaticamente a chave configurada nos settings do servidor.

### **Usando API Key Específica do Usuário**

```bash
# Configurar sua própria chave LLaMA
curl -X POST "http://localhost:8000/api/v1/user-variables/api-keys/llama" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "value": "sua-chave-llama-aqui",
    "description": "Minha chave LLaMA pessoal"
  }'
```

## 📊 Limites e Cotas

- **Rate Limit**: 100 requisições/minuto (padrão)
- **Tokens por requisição**: Máximo 4.096 tokens
- **Concorrência**: 10 requisições simultâneas
- **Cache**: 1 hora para respostas idênticas

## 🔗 Links Relacionados

- **[API LLM Unificada](../integration_guide.md)** - Guia principal
- **[User API Keys](../../user_variables_guide.md)** - Configurar chaves pessoais
- **[Migration Guide](../migration_guide.md)** - Migrar de APIs antigas
- **[LLM Endpoints](../endpoints.md)** - Documentação completa

## ⚠️ Notas Importantes

- **Sempre use `provider: "llama"`** nas requisições
- **Modelos 405B têm custo maior** - use com moderação
- **Cache automático** reduz custos para prompts repetidos
- **Fallback automático** para chave global se sua chave falhar
