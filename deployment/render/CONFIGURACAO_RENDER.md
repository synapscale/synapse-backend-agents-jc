# 🔧 CONFIGURAÇÕES OBRIGATÓRIAS PARA O RENDER

## 🚨 Variáveis de Ambiente Essenciais

Você PRECISA configurar estas variáveis de ambiente no dashboard do Render:

### 1. 🔒 Segurança (OBRIGATÓRIAS)
```env
SECRET_KEY=sua-chave-secreta-super-forte-com-32-caracteres-minimo
JWT_SECRET_KEY=sua-chave-jwt-super-forte-com-64-caracteres-minimo-para-seguranca
ENCRYPTION_KEY=sua-chave-de-criptografia-em-base64-32-bytes
```

### 2. 🗄️ Banco de Dados (OBRIGATÓRIA)
```env
DATABASE_URL=postgresql://usuario:senha@host:porta/database?sslmode=require
```

### 3. 🌐 Configurações Opcionais (mas recomendadas)
```env
# OpenAI (se usar funcionalidades de IA)
OPENAI_API_KEY=sk-sua-chave-openai-aqui

# Email (se usar notificações)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=seu-email@gmail.com
SMTP_PASSWORD=sua-senha-de-app

# CORS (para frontend)
BACKEND_CORS_ORIGINS=["https://seu-frontend.vercel.app","https://seu-dominio.com"]
```

## 🎯 Como Configurar no Render

### Passo 1: No Dashboard do Render
1. Vá para seu serviço
2. Clique em "Environment"
3. Adicione cada variável acima

### Passo 2: Configuração do Banco
1. Crie um PostgreSQL database no Render OU use external (recomendado para produção)
2. Copie a URL de conexão completa
3. Cole na variável `DATABASE_URL`

### Passo 3: Gerar Chaves Seguras
Execute este comando para gerar chaves seguras:

```bash
# SECRET_KEY (32 caracteres)
openssl rand -hex 32

# JWT_SECRET_KEY (64 caracteres)  
openssl rand -hex 64

# ENCRYPTION_KEY (base64, 32 bytes)
openssl rand -base64 32
```

## 🚀 Deploy

### Configuração do Serviço
- **Build Command**: `pip install --upgrade pip && pip install -r requirements.txt && chmod +x deployment/render/setup_render.sh && ./deployment/render/setup_render.sh`
- **Start Command**: `./start_production.sh`
- **Health Check Path**: `/health`

### Verificação
Após o deploy, teste:
- Health: `https://seu-app.onrender.com/health`
- Docs: `https://seu-app.onrender.com/docs`

## ⚠️ Problemas Comuns

### Build Falha
- Verifique se `requirements.txt` está correto
- Confirme que Python 3.11 é compatível

### Start Falha
- Verifique todas as variáveis de ambiente obrigatórias
- Confirme que `DATABASE_URL` está correta
- Veja os logs no dashboard do Render

### Erro de Conexão BD
- Teste a conexão do banco externamente
- Verifique se o firewall permite conexões do Render
- Confirme SSL/TLS se necessário

## 📊 Estrutura de Arquivos para Render

Seus arquivos estão corretos:
- ✅ `render.yaml` - Configuração do serviço
- ✅ `setup_render.sh` - Script de configuração  
- ✅ `start_production.sh` - Script de inicialização
- ✅ `requirements.txt` - Dependências Python
- ✅ `/src/synapse/main.py` - Aplicação principal

## 🔄 Próximos Passos

1. Configure as variáveis de ambiente obrigatórias
2. Faça o deploy
3. Teste os endpoints
4. Configure monitoramento (logs no dashboard)
5. Configure domínio customizado (opcional)

**IMPORTANTE**: Nunca commite chaves secretas no código! Use apenas variáveis de ambiente.
