# 🛡️ GUIA DE SEGURANÇA - SYNAPSCALE BACKEND

## 🚨 PROBLEMAS CRÍTICOS CORRIGIDOS

### ✅ **Chaves Hardcoded Removidas**
- `SECRET_KEY`: Agora lida via variável de ambiente
- `JWT_SECRET_KEY`: Agora lida via variável de ambiente  
- `ENCRYPTION_KEY`: Agora lida via variável de ambiente
- `OPENAI_API_KEY`: Valor demo removido

### ✅ **Credenciais de Banco Protegidas**
- Docker Compose: Senhas agora vêm de variáveis de ambiente
- URLs de conexão: Sem credenciais hardcoded

### ✅ **Arquivos Sensíveis Protegidos**
- `.gitignore` atualizado para proteger `.env`, chaves SSH, etc.
- `.env.example` criado como template seguro

## 🔧 FERRAMENTAS DE SEGURANÇA

### 📊 **Script de Verificação**
```bash
./security_scan.sh
```
**Detecta:**
- Chaves de API expostas
- Senhas hardcoded
- Tokens JWT no código
- Chaves secretas padrão
- URLs com credenciais
- Arquivos sensíveis não protegidos

### 🔑 **Gerador de Chaves**
```bash
python3 generate_secure_keys.py
```
**Gera:**
- SECRET_KEY (64 caracteres)
- JWT_SECRET_KEY (64 caracteres) 
- ENCRYPTION_KEY (32 bytes base64)
- Senhas para PostgreSQL e Redis
- Arquivo `.env` configurado

## 📋 CHECKLIST DE SEGURANÇA

### ✅ **Desenvolvimento**
- [ ] Executar `./security_scan.sh` antes de cada commit
- [ ] Usar `.env.example` como base para configuração
- [ ] Nunca commitar arquivo `.env`
- [ ] Gerar chaves únicas para cada desenvolvedor

### ✅ **Produção**
- [ ] Usar chaves diferentes de desenvolvimento
- [ ] Armazenar chaves em cofre seguro (AWS Secrets Manager, etc.)
- [ ] Habilitar HTTPS e cookies seguros
- [ ] Configurar logs de auditoria
- [ ] Implementar rate limiting
- [ ] Monitorar tentativas de acesso suspeitas

## 🔐 CONFIGURAÇÃO SEGURA

### **1. Gerar Chaves Únicas**
```bash
# Gerar todas as chaves necessárias
python3 generate_secure_keys.py
```

### **2. Configurar Variáveis de Ambiente**
```bash
# Copiar template
cp .env.example .env

# Editar com suas configurações
nano .env
```

### **3. Configurar Produção**
```bash
# Definir ambiente
export ENVIRONMENT=production

# Usar PostgreSQL
export DATABASE_URL="postgresql://user:pass@host:5432/db"

# Habilitar HTTPS
export ENABLE_HTTPS_REDIRECT=true
export SECURE_COOKIES=true
```

## 🚫 O QUE NUNCA FAZER

### ❌ **NUNCA Commitar**
- Arquivo `.env` com credenciais reais
- Chaves de API ou tokens
- Senhas ou certificados
- Logs com informações sensíveis

### ❌ **NUNCA Hardcodar**
- Chaves de API no código
- Senhas em configurações
- URLs com credenciais
- Tokens JWT ou refresh tokens

### ❌ **NUNCA Usar em Produção**
- Chaves de desenvolvimento
- Senhas padrão
- Debug mode habilitado
- HTTP sem HTTPS

## 📚 RECURSOS ADICIONAIS

### **Ferramentas Recomendadas**
- **git-secrets**: Previne commits de credenciais
- **bandit**: Análise de segurança para Python
- **safety**: Verifica vulnerabilidades em dependências
- **pre-commit**: Hooks para verificação automática

### **Serviços de Segurança**
- **AWS Secrets Manager**: Gerenciamento de credenciais
- **HashiCorp Vault**: Cofre de segredos
- **Sentry**: Monitoramento de erros
- **Datadog**: Monitoramento de logs

### **Comandos Úteis**
```bash
# Verificar vulnerabilidades em dependências
pip-audit

# Análise de segurança do código
bandit -r src/

# Verificar vazamentos de credenciais
git-secrets --scan

# Verificar configuração SSL
openssl s_client -connect your-domain.com:443
```

## 🆘 EM CASO DE VAZAMENTO

### **Ação Imediata**
1. **Revogar** todas as chaves expostas
2. **Alterar** senhas comprometidas  
3. **Regenerar** tokens JWT
4. **Verificar** logs de acesso
5. **Notificar** equipe de segurança

### **Investigação**
1. Verificar histórico do git
2. Analisar logs de acesso
3. Identificar potencial uso malicioso
4. Documentar incidente

### **Prevenção**
1. Implementar verificações automáticas
2. Treinar equipe sobre boas práticas
3. Revisar processos de desenvolvimento
4. Atualizar políticas de segurança

---

**🔒 Lembre-se: Segurança é responsabilidade de todos!**
