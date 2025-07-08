# 🔄 Estratégia de Sincronização Sistemática

## 🎯 Objetivo
Sincronizar completamente Models → Schemas → Endpoints para eliminar erros de dessincronização.

## 📋 Plano de Execução

### **FASE 1: Análise** (15 minutos)
```bash
# Executar análise completa
python scripts/analyze_sync_issues.py

# Revisar relatório gerado
cat sync_analysis_report.json | jq '.summary'
```

### **FASE 2: Correção Automática** (30 minutos)
```bash
# Executar correções automáticas
python scripts/fix_sync_issues.py

# Verificar se aplicação ainda funciona
python -c "from synapse.main import app; print('✅ App carregada com sucesso')"
```

### **FASE 3: Testes** (15 minutos)
```bash
# Testar endpoints críticos
curl -X GET http://localhost:8000/api/v1/llms/
curl -X GET http://localhost:8000/api/v1/agents/
curl -X GET http://localhost:8000/api/v1/users/profile

# Verificar documentação
curl -X GET http://localhost:8000/docs
```

### **FASE 4: Correções Manuais** (30 minutos)
Para problemas não cobertos pelo script automático:

#### **Padrões Comuns de Correção:**

1. **Referências Inexistentes → Campos Reais**
   ```python
   # ANTES (ERRADO)
   LLM.is_public == True
   
   # DEPOIS (CORRETO)
   LLM.is_active == True
   ```

2. **user_id → tenant_id (Multi-tenancy)**
   ```python
   # ANTES (ERRADO)
   LLM.user_id == current_user.id
   
   # DEPOIS (CORRETO)
   LLM.tenant_id == current_user.tenant_id
   ```

3. **Lógica OR → AND Simples**
   ```python
   # ANTES (ERRADO)
   or_(Model.is_public == True, Model.user_id == current_user.id)
   
   # DEPOIS (CORRETO)
   and_(Model.tenant_id == current_user.tenant_id, Model.is_active == True)
   ```

## 🔍 Checklist de Validação

### **Para cada endpoint corrigido:**
- [ ] Campos referenciados existem no model
- [ ] Lógica de acesso usa tenant_id
- [ ] Filtros usam campos válidos
- [ ] Não há referências a campos fantasma

### **Testes obrigatórios:**
- [ ] GET /api/v1/llms/ → 200 OK
- [ ] GET /api/v1/agents/ → 200 OK
- [ ] GET /api/v1/users/profile → 200 OK
- [ ] GET /docs → Swagger UI carrega
- [ ] POST /api/v1/auth/login → JWT gerado

## 📊 Métricas de Sucesso

| Métrica | Antes | Meta | Atual |
|---------|--------|------|-------|
| Endpoints com erro 500 | 33 | 0 | ? |
| Endpoints com erro 422 | 36 | <5 | ? |
| Endpoints funcionais | 98 | 200+ | ? |
| Cobertura de schemas | 36% | 90% | ? |

## 🚀 Próximos Passos

### **Curto Prazo (1-2 dias):**
1. Executar scripts de correção
2. Testar endpoints críticos
3. Corrigir problemas manuais
4. Validar funcionalidade

### **Médio Prazo (1 semana):**
1. Criar schemas faltantes
2. Adicionar testes automáticos
3. Implementar CI/CD validation
4. Documentar padrões

### **Longo Prazo (1 mês):**
1. Processo de sincronização contínua
2. Ferramentas de validação automática
3. Padrões de desenvolvimento
4. Testes de regressão

## 📝 Comandos Úteis

```bash
# Encontrar referências problemáticas
grep -r "is_public" src/synapse/api/v1/endpoints/
grep -r "user_id.*current_user.id" src/synapse/api/v1/endpoints/

# Verificar campos de um model
python -c "from synapse.models.llm import LLM; print([c.name for c in LLM.__table__.columns])"

# Testar endpoint específico
python -c "
import asyncio
from synapse.api.v1.endpoints.llms import router
print('✅ Endpoint importado com sucesso')
"

# Verificar se app carrega
python -c "
import sys
sys.path.insert(0, 'src')
from synapse.main import app
print('✅ App carregada - pronta para usar')
"
```

## ⚠️ Cuidados Importantes

1. **Sempre fazer backup** antes de executar correções
2. **Testar em ambiente de desenvolvimento** primeiro
3. **Validar um endpoint por vez** se necessário
4. **Não corrigir tudo de uma vez** - ir por partes
5. **Documentar mudanças** para equipe

## 🔗 Arquivos Relacionados

- `scripts/analyze_sync_issues.py` - Análise de problemas
- `scripts/fix_sync_issues.py` - Correções automáticas
- `PRECISE_MAPPING_ANALYSIS.md` - Mapeamento detalhado
- `COMPREHENSIVE_SCHEMA_ANALYSIS.md` - Análise completa

## 📞 Suporte

Se encontrar problemas específicos:
1. Verificar logs de erro
2. Consultar mapeamento de campos
3. Testar campo por campo
4. Solicitar ajuda se necessário

---

**Última atualização:** 08/01/2025
**Versão:** 1.0
