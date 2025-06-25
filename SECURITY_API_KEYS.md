# 🔐 Guia de Segurança - Chaves de API

## ⚠️ IMPORTANTE: Nunca commite chaves de API!

Este documento orienta sobre o manejo seguro de chaves de API no projeto SynapScale.

## 🚨 Problema Resolvido

**Situação:** Chave da API da Anthropic foi detectada pelo GitHub Push Protection
**Solução:** Chave removida e proteções implementadas

## 📋 Configuração Segura

### 1. Arquivo de Configuração MCP

**❌ NUNCA faça isso:**
```json
{
  "env": {
    "ANTHROPIC_API_KEY": "sk-ant-api03-sua-chave-real-aqui"
  }
}
```

**✅ SEMPRE faça isso:**
```json
{
  "env": {
    "ANTHROPIC_API_KEY": ""
  }
}
```

### 2. Como Configurar suas Chaves

1. **Copie o arquivo de exemplo:**
   ```bash
   cp .cursor/mcp.json.example .cursor/mcp.json
   ```

2. **Edite com suas chaves reais:**
   ```bash
   # Abra o arquivo e adicione suas chaves
   code .cursor/mcp.json
   ```

3. **Nunca commite o arquivo com chaves:**
   ```bash
   # O arquivo .cursor/mcp.json está no .gitignore
   git status  # Não deve aparecer na lista
   ```

## 🛡️ Proteções Implementadas

### 1. GitIgnore Atualizado
```gitignore
# Arquivos de configuração com chaves de API (SEGURANÇA)
.cursor/mcp.json
*.api_keys
*_secrets.json
*_credentials.json
*_keys.json
# Manter apenas arquivos de exemplo
!.cursor/mcp.json.example
!*_example.json
!*_template.json
```

### 2. Arquivo de Exemplo
- `.cursor/mcp.json.example` - Template seguro com placeholders
- `.cursor/mcp.json` - Arquivo real (ignorado pelo git)

## 🔑 Chaves Suportadas

O projeto suporta as seguintes APIs:

- **Anthropic** - `ANTHROPIC_API_KEY`
- **Perplexity** - `PERPLEXITY_API_KEY`
- **OpenAI** - `OPENAI_API_KEY`
- **Google** - `GOOGLE_API_KEY`
- **XAI** - `XAI_API_KEY`
- **OpenRouter** - `OPENROUTER_API_KEY`
- **Mistral** - `MISTRAL_API_KEY`
- **Azure OpenAI** - `AZURE_OPENAI_API_KEY`
- **Ollama** - `OLLAMA_API_KEY`

## 🚀 Setup Rápido

```bash
# 1. Copiar arquivo de exemplo
cp .cursor/mcp.json.example .cursor/mcp.json

# 2. Editar com suas chaves
nano .cursor/mcp.json

# 3. Verificar que não está sendo rastreado
git status | grep mcp.json
# Não deve retornar nada

# 4. Continuar desenvolvimento normalmente
```

## 🆘 Se Commitou uma Chave por Engano

1. **Remova imediatamente da configuração**
2. **Revogue a chave no provedor**
3. **Gere uma nova chave**
4. **Faça um novo commit removendo a chave**
5. **Force push se necessário:**
   ```bash
   git add .
   git commit -m "security: remove exposed API key"
   git push --force-with-lease
   ```

## ✅ Verificação de Segurança

Antes de cada commit, verifique:

```bash
# Verificar se não há chaves expostas
grep -r "sk-ant-api03" . --exclude-dir=.git
grep -r "sk-" .cursor/mcp.json 2>/dev/null || echo "Arquivo protegido ✅"

# Verificar gitignore
git check-ignore .cursor/mcp.json && echo "Protegido ✅" || echo "⚠️ PERIGO"
```

## 📞 Contato

Se tiver dúvidas sobre segurança, consulte a equipe de desenvolvimento.

---

**Lembre-se:** A segurança é responsabilidade de todos! 🔒 