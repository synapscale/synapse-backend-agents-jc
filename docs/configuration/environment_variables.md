# 🔧 Variáveis de Ambiente - SynapScale Backend

## 📋 Referência Completa

Este documento descreve todas as variáveis de ambiente suportadas pelo SynapScale Backend.

## 🗄️ **Banco de Dados**

```env
# Configuração principal do banco
DATABASE_URL=postgresql://user:password@localhost:5432/synapscale_db

# Pool de conexões
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
```

## 🔐 **Segurança**

```env
# Chaves de criptografia (OBRIGATÓRIAS)
SECRET_KEY=sua_chave_secreta_32_chars
JWT_SECRET_KEY=sua_chave_jwt_64_chars
ENCRYPTION_KEY=sua_chave_base64_32_bytes

# Configurações JWT
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
```

## 🤖 **Provedores LLM**

```env
# OpenAI
OPENAI_API_KEY=sk-proj-...
OPENAI_ORG_ID=org-...

# Anthropic
ANTHROPIC_API_KEY=sk-ant-api03-...

# Google Gemini
GOOGLE_API_KEY=AIza...

# Grok (X.AI)
GROK_API_KEY=xai-...

# DeepSeek
DEEPSEEK_API_KEY=sk-...

# Configurações gerais
LLM_DEFAULT_PROVIDER=openai
LLM_TIMEOUT=30
LLM_MAX_RETRIES=3
```

## 🌐 **CORS e Rede**

```env
# CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000","https://app.synapscale.com"]

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_DEFAULT=100/minute
RATE_LIMIT_BURST=200

# WebSockets
WS_HEARTBEAT_INTERVAL=30
WS_MAX_CONNECTIONS=1000
```

## 📊 **Cache e Redis**

```env
# Redis
REDIS_URL=redis://localhost:6379/0
REDIS_PASSWORD=senha_redis

# Cache
CACHE_TTL=3600
CACHE_MAX_SIZE=10000
```

## 📁 **Armazenamento**

```env
# Local storage
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=10485760  # 10MB
ALLOWED_EXTENSIONS=["jpg","jpeg","png","pdf","docx","txt"]

# Cloud storage (opcional)
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_S3_BUCKET=...
AWS_REGION=us-east-1
```

## 📧 **Email e Notificações**

```env
# SMTP
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=noreply@synapscale.com
SMTP_PASSWORD=app_password
SMTP_TLS=true

# Templates
EMAIL_TEMPLATES_DIR=./templates/emails
```

## 📈 **Monitoramento**

```env
# Logging
LOG_LEVEL=INFO
LOG_FILE=./logs/synapscale.log
LOG_MAX_SIZE=10MB
LOG_BACKUP_COUNT=5

# Métricas
ENABLE_METRICS=true
METRICS_PORT=9090

# Sentry (opcional)
SENTRY_DSN=https://...
```

## 🚀 **Deploy e Ambiente**

```env
# Ambiente
ENVIRONMENT=development  # development, staging, production
DEBUG=true
HOST=0.0.0.0
PORT=8000

# Render específico
RENDER_EXTERNAL_URL=https://seu-app.onrender.com
```

## 🛡️ **Segurança Avançada**

```env
# Headers de segurança
SECURE_COOKIES=true
ENABLE_HTTPS_REDIRECT=true
CSRF_PROTECTION=true

# API Keys
API_KEY_ENCRYPTION_ENABLED=true
USER_API_KEYS_ENABLED=true
```

## 📋 **Templates Disponíveis**

- **[env.complete](./templates/env.complete)** - Todas as variáveis com valores de exemplo
- **[env.render.example](./templates/env.render.example)** - Configuração otimizada para Render

## 🔗 **Links Úteis**

- **[Setup Guide](../SETUP_GUIDE.md)** - Como configurar as variáveis
- **[Security Guide](../SECURITY.md)** - Boas práticas de segurança
- **[Deploy Guide](../deployment/render_guide.md)** - Deploy em produção
