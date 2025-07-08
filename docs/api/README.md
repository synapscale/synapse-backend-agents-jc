# Documentação do Banco de Dados SynapScale

**Gerado automaticamente em:** 2025-07-07 19:24:45

## 📚 Documentação Disponível

### 📊 Schema do Banco
- [Schema Completo](schema.md) - Documentação detalhada de todas as tabelas
- [Dados JSON](database_info.json) - Informações estruturadas do banco

### 🎨 Diagramas
- [Diagrama ER](er_diagram.mmd) - Diagrama entidade-relacionamento em Mermaid

### 🏥 Monitoramento
- [Health Dashboard](health_dashboard.html) - Dashboard de saúde do sistema

## 🔄 Como Atualizar

```bash
# Gerar toda a documentação
python tools/database/doc_generator.py

# Gerar apenas schema
python tools/database/doc_generator.py --schema-only

# Gerar com health check
python tools/database/doc_generator.py --with-health
```

---
*Documentação mantida automaticamente pelo Doc Generator*