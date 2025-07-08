# 🏗️ SynapScale - Guia de Arquitetura

## 📋 Fontes de Verdade e Regras de Importação

Este documento define claramente as **fontes de verdade** para cada componente do sistema SynapScale, garantindo consistência e evitando conflitos de arquitetura.

---

## 🗃️ 1. BANCO DE DADOS (SQLAlchemy Models)

### 📍 **Fonte de Verdade: `src/synapse/models/`**

**✅ FAZER:**
```python
# Import correto - sempre usar arquivos específicos
from synapse.models.user import User
from synapse.models.workspace import Workspace
from synapse.models.feature import Feature
```

**❌ NÃO FAZER:**
```python
# NUNCA usar imports genéricos ou centralizados
from synapse.models.models import User  # ❌ ERRADO
from synapse.models import *            # ❌ ERRADO
```

### 🔧 **Regras:**
- Cada entidade tem seu próprio arquivo model específico
- Models legados/backup devem ser removidos imediatamente
- Sempre usar relacionamentos SQLAlchemy adequados
- O arquivo `models/models.py` deve estar vazio ou ser removido

---

## 📋 2. SCHEMAS PYDANTIC (Validação)

### 📍 **Fonte de Verdade: `src/synapse/schemas/`**

**✅ FAZER:**
```python
# Import correto - sempre usar schemas específicos por domínio
from synapse.schemas.user import UserCreate, UserUpdate, UserResponse
from synapse.schemas.feature import FeatureCreate, FeatureResponse
from synapse.schemas.payment import PaymentProviderCreate
from synapse.schemas.rbac import RBACRoleCreate
from synapse.schemas.workspace import WorkspaceCreate, MemberInvite
from synapse.schemas.file import FileCreate, FileUpdate
```

**❌ NÃO FAZER:**
```python
# NUNCA usar o arquivo gigante centralizado
from synapse.schemas.models import UserCreate  # ❌ ELIMINADO
from synapse.schemas.models import *           # ❌ ELIMINADO
```

### 🗂️ **Organização dos Schemas:**

| Arquivo | Responsabilidade | Schemas Principais |
|---------|------------------|-------------------|
| `user.py` | Usuários e perfis | `UserCreate`, `UserUpdate`, `UserProfileUpdate` |
| `feature.py` | Features do sistema | `FeatureCreate`, `PlanFeatureCreate`, `TenantFeatureCreate` |
| `rbac.py` | Controle de acesso | `RBACRoleCreate`, `RBACPermissionCreate` |
| `payment.py` | Sistema de pagamento | `PaymentProviderCreate`, `InvoiceCreate` |
| `workspace.py` | Workspaces | `WorkspaceCreate`, `MemberInvite` |
| `file.py` | Gerenciamento de arquivos | `FileCreate`, `FileUpdate` |

### 🔧 **Regras:**
- Schemas organizados por domínio/contexto
- Nunca criar arquivos centralizados gigantes
- Sempre usar `ConfigDict` adequado para cada schema
- O arquivo `schemas/models.py` foi **permanentemente eliminado**

---

## ⚙️ 3. CONFIGURAÇÃO

### 📍 **Fonte de Verdade: `src/synapse/core/config.py`**

**✅ FAZER:**
```python
# Import correto - sempre usar settings centralizado
from synapse.core.config import settings

# Usar configurações
database_url = settings.DATABASE_URL
redis_url = settings.REDIS_URL
```

**❌ NÃO FAZER:**
```python
# NUNCA criar configurações duplicadas
import os
DATABASE_URL = os.getenv("DATABASE_URL")  # ❌ ERRADO - bypassa validação

# NUNCA importar Settings diretamente
from synapse.core.config import Settings  # ❌ ERRADO
config = Settings()                       # ❌ ERRADO
```

### 🔧 **Regras:**
- Sempre usar `settings` importado de `core.config`
- Configurações são validadas via Pydantic
- Nunca acessar `os.getenv()` diretamente para configs principais
- Usar `PROJECT_ROOT` para paths absolutos

---

## 🔍 4. VALIDAÇÃO DE INPUT (FastAPI Endpoints)

### 📍 **Fonte de Verdade: Schemas Pydantic + FastAPI Signatures**

**✅ FAZER:**
```python
from synapse.schemas.user import UserCreate, UserResponse

@router.post("/users", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,  # ✅ Schema Pydantic para validação
    db: AsyncSession = Depends(get_db)
):
    # Implementação
    pass
```

**❌ NÃO FAZER:**
```python
# NUNCA usar validação manual ou dicts
@router.post("/users")
async def create_user(user_data: dict):  # ❌ ERRADO - sem validação
    pass

# NUNCA misturar schemas antigos
from synapse.schemas.models import UserCreate  # ❌ ELIMINADO
```

### 🔧 **Regras:**
- Sempre usar `response_model` nos endpoints
- Sempre usar schemas Pydantic como parâmetros
- Nunca aceitar `dict` ou validação manual
- Schemas devem cobrir todos os casos de uso

---

## 🚦 5. PROCESSO DE DESENVOLVIMENTO

### ✅ **Checklist de Desenvolvimento:**

1. **Models (Banco):**
   - [ ] Model específico criado em `models/`
   - [ ] Relacionamentos SQLAlchemy definidos
   - [ ] Migration criada e aplicada

2. **Schemas (Validação):**
   - [ ] Schema específico criado em `schemas/`
   - [ ] Schemas de Create, Update, Response definidos
   - [ ] `ConfigDict` adequado configurado

3. **Endpoints (API):**
   - [ ] Imports dos schemas específicos
   - [ ] `response_model` definido
   - [ ] Validação Pydantic nas entradas

4. **Configuração:**
   - [ ] Usar `settings` de `core.config`
   - [ ] Não criar configs duplicadas

### 🔒 **Regras de Segurança:**

- **NUNCA** fazer bypass da validação Pydantic
- **NUNCA** usar arquivos centralizados gigantes
- **NUNCA** misturar fontes de verdade
- **SEMPRE** usar imports específicos e diretos

---

## 🎯 6. TROUBLESHOOTING

### 🔧 **Problemas Comuns:**

| Problema | Causa | Solução |
|----------|-------|---------|
| `ImportError: cannot import name 'X' from schemas.models` | Uso do arquivo eliminado | Usar schema específico |
| `ValidationError` em endpoints | Schema inadequado | Verificar schema correto |
| Configs duplicadas | Import direto de `os.getenv` | Usar `settings` |
| Model não encontrado | Import incorreto | Usar model específico |

### 🚨 **Sinais de Alerta:**

- Imports de `schemas.models` (arquivo eliminado)
- Arquivos com milhares de linhas
- Imports usando `*`
- Configurações hardcoded
- Validação manual em endpoints

---

## 📊 7. MONITORAMENTO CONTÍNUO

### ✅ **Verificações Automáticas:**

```bash
# Verificar se não há imports problemáticos
grep -r "schemas\.models" src/
# Deve retornar vazio

# Verificar estrutura dos schemas
ls src/synapse/schemas/
# Deve mostrar arquivos específicos por domínio

# Validar configuração centralizada
grep -r "from synapse.core.config import settings" src/
# Deve mostrar uso consistente
```

---

## 🏆 **RESULTADO ALCANÇADO**

✅ **Sistema Limpo e Organizado:**
- 0 arquivos usando `schemas.models` (eliminado)
- Schemas organizados por domínio
- Configuração centralizada e validada
- Models específicos e relacionados
- Validação Pydantic adequada

✅ **Benefícios:**
- Eliminação de erros 500, 422, 404
- Arquitetura maintível e escalável
- Fonte de verdade clara para cada componente
- Facilidade para novos desenvolvedores

---

**📅 Documento atualizado:** $(date)
**👥 Responsabilidade:** Todos os desenvolvedores
**🔄 Revisão:** A cada release principal
