# 🤖 Guia Completo de Integração LLM - SynapScale

## 🎯 Visão Geral

O SynapScale oferece integração unificada com **múltiplos provedores de LLM** através de uma única API, permitindo flexibilidade, resiliência e facilidade de uso. Este guia abrange configuração, uso e melhores práticas.

### ✨ **Funcionalidades Principais**

- **🔑 API Keys Personalizadas**: Usuários podem configurar suas próprias chaves para cada provedor
- **🔄 Fallback Automático**: Sistema usa chaves globais se usuário não configurou chaves específicas  
- **🛡️ Criptografia Segura**: Todas as chaves são criptografadas com Fernet
- **⚡ Interface Unificada**: Mesma API para todos os provedores
- **🔍 Transparência Total**: Endpoints funcionam automaticamente com chaves específicas

---

## 🚀 **Provedores Suportados**

| Provedor | Chave API | Modelos Principais | Casos de Uso |
|----------|-----------|-------------------|--------------|
| **OpenAI** | `OPENAI_API_KEY` | GPT-4o, GPT-4, GPT-3.5-turbo | Geração geral, análise, classificação |
| **Anthropic** | `ANTHROPIC_API_KEY` | Claude 3 Opus, Sonnet, Haiku | Raciocínio ético, seguimento de instruções |
| **Google** | `GOOGLE_API_KEY` | Gemini 1.5 Pro, Gemini Pro | Multimodal, análise de dados, código |
| **Grok** | `GROK_API_KEY` | Grok-1, Grok-2 | Conversação, criatividade |
| **DeepSeek** | `DEEPSEEK_API_KEY` | DeepSeek Coder, Chat | Geração de código, programação |
| **Llama** | `LLAMA_API_KEY` | Llama 3 70B, 8B, Llama 2 | Open source, fine-tuning |

---

## ⚙️ **Configuração**

### **1. Configuração Global (Sistema)**

No arquivo `.env` da raiz do projeto:

```env
# Provedores LLM (configuração global)
LLM_DEFAULT_PROVIDER=openai
OPENAI_API_KEY=sk-proj-1234567890abcdef...
ANTHROPIC_API_KEY=sk-ant-api03-1234567890abcdef...
GOOGLE_API_KEY=AIzaSy1234567890abcdef...
GROK_API_KEY=xai-1234567890abcdef...
DEEPSEEK_API_KEY=sk-1234567890abcdef...
LLAMA_API_KEY=la_1234567890abcdef...
```

### **2. Configuração por Usuário (API Keys Específicas)**

Usuários podem configurar suas próprias chaves:

```http
POST /api/v1/user-variables/api-keys/openai
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "value": "sk-proj-SUA_CHAVE_PESSOAL_AQUI",
  "description": "Minha chave OpenAI pessoal"
}
```

**Provedores suportados**: `openai`, `anthropic`, `google`, `grok`, `deepseek`, `llama`

---

## 📚 **Uso da API**

### **Geração de Texto (Endpoint Unificado)**

```http
POST /api/v1/llm/generate
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "prompt": "Explique machine learning em termos simples",
  "provider": "openai",
  "model": "gpt-4o",
  "max_tokens": 500,
  "temperature": 0.7
}
```

> 🔑 **Chaves Automáticas**: Este endpoint usa automaticamente a chave específica do usuário, ou fallback para chaves globais.

### **Endpoints Específicos por Provedor**

```http
POST /api/v1/llm/openai/generate
POST /api/v1/llm/anthropic/generate  
POST /api/v1/llm/google/generate
POST /api/v1/llm/grok/generate
POST /api/v1/llm/deepseek/generate
POST /api/v1/llm/llama/generate
```

### **Contagem de Tokens**

```http
POST /api/v1/llm/count-tokens
Content-Type: application/json

{
  "text": "Texto para contar tokens",
  "provider": "openai"
}
```

### **Listar Modelos e Provedores**

```http
GET /api/v1/llm/models          # Todos os modelos
GET /api/v1/llm/providers       # Todos os provedores
GET /api/v1/llm/openai/models   # Modelos OpenAI específicos
```

---

## 🔧 **Parâmetros Avançados**

### **Parâmetros Comuns (Todos os Provedores)**

| Parâmetro | Tipo | Padrão | Descrição |
|-----------|------|--------|-----------|
| `prompt` | string | - | **Obrigatório**: Texto de entrada |
| `provider` | string | `openai` | Provedor a usar |
| `model` | string | *varia* | Modelo específico |
| `max_tokens` | integer | `1000` | Limite de tokens na resposta |
| `temperature` | float | `0.7` | Aleatoriedade (0.0-1.0) |

### **Parâmetros Específicos por Provedor**

#### **OpenAI**
```json
{
  "top_p": 1.0,
  "frequency_penalty": 0.0,
  "presence_penalty": 0.0,
  "stop": []
}
```

#### **Anthropic**
```json
{
  "top_k": 40,
  "top_p": 0.7,
  "stop_sequences": []
}
```

#### **Google**
```json
{
  "top_k": 40,
  "top_p": 0.95,
  "candidate_count": 1
}
```

---

## 💻 **Exemplos de Código**

### **Python - Uso Básico**

```python
import requests

def generate_text(prompt, provider="openai"):
    url = "http://localhost:8000/api/v1/llm/generate"
    headers = {"Authorization": "Bearer YOUR_TOKEN"}
    
    response = requests.post(url, json={
        "prompt": prompt,
        "provider": provider,
        "max_tokens": 500,
        "temperature": 0.7
    }, headers=headers)
    
    return response.json()["text"]

# Uso
resultado = generate_text("Explique IA em termos simples", "openai")
print(resultado)
```

### **Python - Sistema de Fallback**

```python
import requests
import time

def generate_with_fallback(prompt, providers=["openai", "anthropic", "google"]):
    for provider in providers:
        try:
            response = requests.post(
                "http://localhost:8000/api/v1/llm/generate",
                json={"prompt": prompt, "provider": provider},
                headers={"Authorization": "Bearer YOUR_TOKEN"},
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()["text"]
                
        except Exception as e:
            print(f"Erro com {provider}: {e}")
            time.sleep(1)
            
    raise Exception("Todos os provedores falharam")
```

### **JavaScript/Node.js**

```javascript
async function generateText(prompt, provider = "openai") {
    const response = await fetch("http://localhost:8000/api/v1/llm/generate", {
        method: "POST",
        headers: {
            "Authorization": "Bearer YOUR_TOKEN",
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            prompt: prompt,
            provider: provider,
            max_tokens: 500,
            temperature: 0.7
        })
    });
    
    const data = await response.json();
    return data.text;
}

// Uso
const resultado = await generateText("Explique IA em termos simples");
console.log(resultado);
```

---

## 🔑 **Gerenciamento de API Keys por Usuário**

### **Configurar Chave**

```python
import requests

def configure_api_key(provider, api_key, token):
    url = f"http://localhost:8000/api/v1/user-variables/api-keys/{provider}"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.post(url, json={
        "value": api_key,
        "description": f"Chave {provider} pessoal"
    }, headers=headers)
    
    return response.json()

# Configurar chave OpenAI
configure_api_key("openai", "sk-proj-SUA_CHAVE", "SEU_TOKEN")
```

### **Listar Chaves (Mascaradas)**

```python
def list_api_keys(token):
    url = "http://localhost:8000/api/v1/user-variables/api-keys"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    return response.json()

# Resultado mostra: "****cdef" para segurança
```

### **Remover Chave**

```python
def remove_api_key(provider, token):
    url = f"http://localhost:8000/api/v1/user-variables/api-keys/{provider}"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.delete(url, headers=headers)
    return response.status_code == 200
```

---

## 🛡️ **Segurança e Melhores Práticas**

### **Segurança**
- ✅ **Criptografia**: Todas as chaves são criptografadas com Fernet
- ✅ **Mascaramento**: Chaves exibidas como `****1234` na listagem
- ✅ **Isolamento**: Cada usuário só acessa suas próprias chaves
- ✅ **Fallback Seguro**: Usa chaves globais quando usuário não tem configurada

### **Melhores Práticas**
1. **Configure chaves específicas** para controle de custos
2. **Use cache** (`use_cache: true`) para economizar tokens
3. **Defina limites** (`max_tokens`) apropriados
4. **Implemente fallback** entre provedores
5. **Monitore custos** regularmente

### **Rate Limiting**
- **Requests**: 100/min por usuário
- **Tokens**: Limitado pelas APIs dos provedores
- **Cache TTL**: 300 segundos (5 minutos)

---

## 🔍 **Troubleshooting**

### **Problemas Comuns**

| Erro | Causa | Solução |
|------|-------|---------|
| `401 Unauthorized` | Chave API inválida | Verificar chave no provedor |
| `429 Too Many Requests` | Rate limit | Aguardar ou usar outro provedor |
| `400 Bad Request` | Parâmetros inválidos | Verificar documentação do modelo |
| `Provider not available` | Provedor offline | Usar fallback automático |

### **Debug**

```python
# Verificar status dos provedores
response = requests.get("http://localhost:8000/api/v1/llm/providers")
providers = response.json()

for provider in providers["providers"]:
    print(f"{provider['name']}: {provider['available']}")
```

---

## 📈 **Performance e Otimização**

### **Cache Inteligente**
- **Cache automático** para prompts idênticos
- **TTL configurável** (padrão: 5 minutos)
- **Economia significativa** de tokens e custos

### **Seleção Automática de Modelos**

```python
def select_optimal_model(prompt_complexity):
    if prompt_complexity == "simple":
        return {"provider": "openai", "model": "gpt-3.5-turbo"}
    elif prompt_complexity == "complex":
        return {"provider": "anthropic", "model": "claude-3-opus"}
    else:
        return {"provider": "google", "model": "gemini-1.5-pro"}
```

---

## 🔗 **Recursos Adicionais**

- **[Endpoints LLM Detalhados](./endpoints.md)** - Documentação completa de endpoints
- **[OpenAI Específico](./openai_endpoints.md)** - Configurações específicas OpenAI
- **[Llama Específico](./llama_endpoints.md)** - Configurações específicas Llama
- **[Guia de API Keys](../user_variables_api_keys_guide.md)** - Gerenciamento detalhado de chaves

---

**Última atualização**: Dezembro 2024  
**Versão**: 2.0.0  
**Status**: ✅ Documentação consolidada e atualizada
