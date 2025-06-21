# 📁 Templates de Configuração

Esta pasta contém templates de variáveis de ambiente para diferentes cenários de deployment do SynapScale Backend.

## 📄 **Arquivos Disponíveis**

### **env.complete**
- **Template completo** com todas as variáveis disponíveis
- **Uso**: Desenvolvimento e produção completos
- **Contém**: Todas as configurações possíveis do sistema

### **env.render.example**  
- **Template específico** para deploy na plataforma Render
- **Uso**: Deploy em produção no Render
- **Contém**: Configurações otimizadas para Render

## 🚀 **Como Usar**

### **Para Desenvolvimento Local**
```bash
# Copiar template completo
cp docs/config-templates/env.complete .env

# Gerar chaves seguras automaticamente
python setup/scripts/generate_secure_keys.py

# Editar e configurar suas chaves específicas
nano .env
```

### **Para Deploy no Render**
```bash
# Usar como referência
cat docs/config-templates/env.render.example

# Configurar variáveis no painel do Render
# baseado no template
```

## ⚙️ **Configuração Essencial**

### **Obrigatórias**
1. **DATABASE_URL** - Conexão PostgreSQL
2. **SECRET_KEY** - Chave secreta (32 chars)
3. **JWT_SECRET_KEY** - Chave JWT (64 chars)
4. **ENCRYPTION_KEY** - Chave criptografia (base64)

### **LLM APIs** (pelo menos uma)
- `OPENAI_API_KEY` - Para GPT models
- `ANTHROPIC_API_KEY` - Para Claude models  
- `GOOGLE_API_KEY` - Para Gemini models

### **Produção Adicional**
- **SMTP_** configurações para email
- **REDIS_URL** para cache
- **CORS** configurado para frontend

## 🔐 **Segurança**

- ✅ **NUNCA** commite arquivos `.env` 
- ✅ **Use** chaves seguras geradas automaticamente
- ✅ **Configure** CORS adequadamente
- ✅ **Ative** HTTPS em produção

## 📚 **Referências**

- **[SETUP_GUIDE.md](../SETUP_GUIDE.md)** - Guia completo de instalação
- **[Security Guide](../SECURITY.md)** - Diretrizes de segurança
- **[Deploy Guide](../guides/DEPLOY-RENDER.md)** - Deploy no Render 