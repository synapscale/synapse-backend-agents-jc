# 📚 **Guia de Migração - Endpoints LLM Unificados**

## 🎯 **Visão Geral**

O SynapScale implementou um sistema LLM unificado que centraliza todas as operações de IA em endpoints padronizados. Este guia ajudará você a migrar do sistema antigo para a nova arquitetura.

---

## 🏗️ **Arquitetura Nova vs. Antiga**

### ✅ **Nova Arquitetura (Unificada)**
```
/llm/models        ← Lista todos os modelos disponíveis
/llm/providers     ← Lista todos os provedores configurados
/llm/generate      ← Geração de texto unificada
/llm/chat          ← Chat unificado
/llms/*            ← Catálogo de modelos (alias)
```

### ❌ **Arquitetura Antiga (Fragmentada)**
```
/openai/models     ← Apenas modelos OpenAI
/anthropic/chat    ← Apenas Anthropic
/google/generate   ← Apenas Google
[... endpoints espalhados por provider]
```

---

## 🚀 **Principais Benefícios da Migração**

### 🔄 **1. Unificação Total**
- **Antes**: Múltiplos endpoints por provider
- **Agora**: Endpoints únicos que suportam todos os providers

### ⚡ **2. Performance Otimizada**
- **Cache Redis**: Respostas cachadas para melhor performance
- **Token Management**: Gestão inteligente de tokens e custos
- **Connection Pooling**: Reutilização de conexões

### 🛡️ **3. Validação Robusta**
- **Database Validation**: Validação em tempo real dos modelos
- **Fallback Graceful**: Sistema de fallback automático
- **Error Handling**: Tratamento de erros padronizado

### 📊 **4. Observabilidade**
- **Métricas Prometheus**: Monitoramento completo
- **Usage Tracking**: Rastreamento detalhado de uso
- **Health Checks**: Verificação de saúde dos services

---

## 📋 **Guia de Migração por Endpoint**

### 🔄 **1. Geração de Texto**

#### ❌ **Endpoints Antigos:**
```bash
POST /openai/generate
POST /anthropic/generate  
POST /google/generate
```

#### ✅ **Novo Endpoint Unificado:**
```bash
POST /llm/generate
```

**Payload novo:**
```json
{
  "provider": "openai",        ← Especifica o provider
  "model": "gpt-4o",          ← Modelo específico
  "prompt": "Seu prompt aqui",
  "max_tokens": 1000,
  "temperature": 0.7
}
```

### 🔄 **2. Chat/Conversação**

#### ❌ **Endpoints Antigos:**
```bash
POST /openai/chat
POST /anthropic/messages
POST /google/chat
```

#### ✅ **Novo Endpoint Unificado:**
```bash
POST /llm/chat
```

**Payload novo:**
```json
{
  "provider": "anthropic",
  "model": "claude-3-opus",
  "messages": [
    {"role": "user", "content": "Olá!"}
  ],
  "max_tokens": 1000,
  "temperature": 0.7
}
```

### 🔄 **3. Listagem de Modelos**

#### ❌ **Endpoints Antigos:**
```bash
GET /openai/models
GET /anthropic/models
GET /google/models
```

#### ✅ **Novos Endpoints Unificados:**
```bash
GET /llm/models              ← Todos os modelos
GET /llm/models?provider=openai  ← Filtro por provider
GET /llms/                   ← Catálogo completo (alias)
```

### 🔄 **4. Informações de Providers**

#### ❌ **Endpoints Antigos:**
```bash
GET /openai/status
GET /anthropic/health
GET /google/info
```

#### ✅ **Novo Endpoint Unificado:**
```bash
GET /llm/providers           ← Todos os provedores e status
```

---

## ⚙️ **Mudanças no Código**

### 🔧 **JavaScript/TypeScript**

#### ❌ **Código Antigo:**
```javascript
// Antes - múltiplas chamadas
const openaiResponse = await fetch('/api/v1/openai/generate', {
  method: 'POST',
  body: JSON.stringify({ prompt: 'Hello' })
});

const anthropicResponse = await fetch('/api/v1/anthropic/generate', {
  method: 'POST', 
  body: JSON.stringify({ prompt: 'Hello' })
});
```

#### ✅ **Código Novo:**
```javascript
// Agora - endpoint unificado
const response = await fetch('/api/v1/llm/generate', {
  method: 'POST',
  body: JSON.stringify({
    provider: 'openai',     // ou 'anthropic', 'google', etc.
    model: 'gpt-4o',
    prompt: 'Hello'
  })
});
```

### 🔧 **Python**

#### ❌ **Código Antigo:**
```python
# Antes - múltiplos clients
import openai
import anthropic

openai_response = openai.chat.completions.create(...)
anthropic_response = anthropic.messages.create(...)
```

#### ✅ **Código Novo:**
```python
# Agora - client unificado
import requests

response = requests.post('/api/v1/llm/chat', json={
    'provider': 'openai',
    'model': 'gpt-4o', 
    'messages': [{'role': 'user', 'content': 'Hello'}]
})
```

---

## 📅 **Timeline de Depreciação**

### 🟢 **Fase 1 - Atual (Compatibilidade Total)**
- ✅ Novos endpoints `/llm/*` disponíveis
- ✅ Endpoints antigos mantidos para compatibilidade
- ✅ Sem breaking changes

### 🟡 **Fase 2 - Q2 2024 (Deprecation Warnings)**
- ⚠️ Endpoints antigos marcados como deprecated
- ⚠️ Headers de warning adicionados
- ⚠️ Logs de deprecation ativados

### 🟠 **Fase 3 - Q3 2024 (Redirect Automático)**
- 🔄 Endpoints antigos redirecionam automaticamente
- 📧 Notificações por email para desenvolvedores
- 📊 Relatórios de migração disponíveis

### 🔴 **Fase 4 - Q4 2024 (Desativação Completa)**
- ❌ Endpoints antigos removidos completamente
- ✅ Apenas endpoints `/llm/*` disponíveis

---

## 🔧 **Ferramentas de Migração**

### 📊 **1. Script de Análise**
```bash
# Analisa seu código para encontrar endpoints antigos
python scripts/analyze_llm_usage.py --path ./src
```

### 🔄 **2. Script de Migração Automática**
```bash
# Substitui automaticamente endpoints antigos por novos
python scripts/migrate_llm_endpoints.py --path ./src --backup
```

### ✅ **3. Validação**
```bash
# Valida se a migração foi bem-sucedida
python scripts/validate_migration.py --path ./src
```

---

## 🚨 **Problemas Comuns e Soluções**

### ❌ **Problema 1: "Model not found"**
**Causa**: Modelo não existe no provider especificado
```bash
# Verificar modelos disponíveis
curl /api/v1/llm/models?provider=openai
```

### ❌ **Problema 2: "Provider not available"**
**Causa**: Provider não configurado ou inativo
```bash
# Verificar status dos providers
curl /api/v1/llm/providers
```

### ❌ **Problema 3: "Rate limit exceeded"**
**Causa**: Muitas requisições em pouco tempo
**Solução**: Implementar retry com backoff exponencial

### ❌ **Problema 4: "Invalid API key"**
**Causa**: Chave API do provider expirada
**Solução**: Verificar configuração em `/user-variables`

---

## 📞 **Suporte e Recursos**

### 🆘 **Precisa de Ajuda?**
- 📧 **Email**: support@synapscale.com
- 💬 **Discord**: [SynapScale Community](https://discord.gg/synapscale)
- 📖 **Docs**: [docs.synapscale.com](https://docs.synapscale.com)

### 🛠️ **Recursos Técnicos**
- **Health Check**: `GET /health/detailed`
- **Metrics**: `GET /metrics` (Prometheus)
- **OpenAPI**: `GET /docs`

### 📈 **Monitoramento**
- **Usage Logs**: `GET /usage-logs`
- **Billing Events**: `GET /billing-events`
- **Analytics**: `GET /analytics`

---

## ✅ **Checklist de Migração**

### 📋 **Pré-Migração**
- [ ] Fazer backup do código atual
- [ ] Revisar dependências dos endpoints antigos
- [ ] Planejar cronograma de migração
- [ ] Configurar ambiente de teste

### 🔄 **Durante a Migração**
- [ ] Substituir endpoints antigos por `/llm/*`
- [ ] Atualizar payloads para incluir `provider` e `model`
- [ ] Implementar error handling para novos formatos
- [ ] Testar com todos os providers necessários

### ✅ **Pós-Migração**
- [ ] Validar funcionamento em produção
- [ ] Monitorar métricas e logs
- [ ] Remover código dos endpoints antigos
- [ ] Atualizar documentação interna

---

**🎉 Migração concluída com sucesso!** 

Agora você tem acesso a toda a potência do sistema LLM unificado do SynapScale. 