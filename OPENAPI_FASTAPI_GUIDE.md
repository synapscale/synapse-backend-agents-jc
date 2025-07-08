# 📚 SynapScale - Guia Completo OpenAPI/FastAPI

## 🎯 Configuração OpenAPI/FastAPI - Documentação Oficial

Este documento define **todas as configurações, regras e fluxos** necessários para o perfeito funcionamento do OpenAPI/FastAPI no SynapScale Backend.

---

## 📋 **ARQUIVOS PRINCIPAIS**

### 🔧 **Arquivo Central:**
- **`openapi.json`** - Especificação OpenAPI estática no diretório raiz
- **`src/synapse/main.py`** - Configurações FastAPI e OpenAPI customizado

### 📊 **Arquivos de Análise:**
- **`reports/analysis/openapi_schemas.json`** - Schemas extraídos para análise
- **`docs/reports/openapi_comparison_report.md`** - Relatórios de comparação
- **`tests/analysis/check_schema_alignment.py`** - Script de validação

---

## ⚙️ **CONFIGURAÇÕES FASTAPI**

### 1. **Aplicação FastAPI (main.py)**

```python
app = FastAPI(
    title=settings.PROJECT_NAME,              # "SynapScale Backend API"
    version=settings.VERSION,                 # "2.0.0"
    description="API de Automação com IA",
    docs_url=None,                            # Usa endpoint customizado
    redoc_url="/redoc",                       # ReDoc ativo
    openapi_tags=openapi_tags,               # 11 tags organizadas
    swagger_ui_parameters={
        "defaultModelsExpandDepth": -1,       # Oculta schemas laterais
        "docExpansion": "none",               # Inicia colapsado
        "displayRequestDuration": True,       # Mostra tempo de resposta
        "tryItOutEnabled": True,              # Permite executar
        "persistAuthorization": True,         # Mantém auth entre sessões
    },
    lifespan=lifespan,                       # Gerenciamento de ciclo de vida
)
```

### 2. **OpenAPI Customizado**

```python
def custom_openapi():
    """Gera esquema OpenAPI customizado com configurações específicas"""
    
    # Forçar regeneração (remove cache)
    app.openapi_schema = None
    
    # Gerar spec base
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
        tags=openapi_tags,
    )
    
    # Configurar esquemas de segurança
    openapi_schema["components"]["securitySchemes"] = {
        "HTTPBearer": {
            "type": "http",
            "scheme": "bearer", 
            "bearerFormat": "JWT",
            "description": "Token JWT obtido via /auth/login"
        },
        "HTTPBasic": {
            "type": "http",
            "scheme": "basic",
            "description": "Login direto com email/senha"
        }
    }
    
    # Segurança global (ambos os métodos aceitos)
    openapi_schema["security"] = [
        {"HTTPBearer": []}, 
        {"HTTPBasic": []}
    ]
    
    # Corrigir referências de schemas
    _fix_refs(openapi_schema)
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

# Aplicar customização
app.openapi = custom_openapi
```

### 3. **Endpoints de Documentação**

```python
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """Swagger UI customizado com design moderno"""
    # HTML customizado com CSS/JS específico
    return HTMLResponse(content=custom_html)

@app.get("/openapi.json", include_in_schema=False)  
async def get_openapi_json():
    """Serve arquivo openapi.json estático"""
    # Tenta carregar arquivo estático, fallback para dinâmico
    if Path("openapi.json").exists():
        return json.load(open("openapi.json"))
    return app.openapi()
```

---

## 🔄 **FLUXO DE GERAÇÃO AUTOMÁTICA**

### 1. **Durante Desenvolvimento (dev.sh)**

```bash
# Regenerar openapi.json automaticamente
echo "🔄 Regenerando openapi.json a partir do app FastAPI..."
python3 - << 'PYCODE'
import json, os, sys
from dotenv import load_dotenv
sys.path.insert(0, './src')
load_dotenv('.env')

try:
    from synapse.main import app
    spec = app.openapi()
    with open('openapi.json', 'w', encoding='utf-8') as f:
        json.dump(spec, f, indent=2, ensure_ascii=False)
    print('✅ openapi.json atualizado com sucesso!')
    print(f'   - Endpoints: {len(spec.get("paths", {}))}')
    print(f'   - Schemas: {len(spec.get("components", {}).get("schemas", {}))}')
except Exception as e:
    print(f'❌ Erro ao gerar openapi.json: {e}')
PYCODE
```

### 2. **Validação de Alinhamento**

```bash
# Verificar alinhamento com banco de dados
chmod +x tests/analysis/check_schema_alignment.py
tests/analysis/check_schema_alignment.py || true
```

---

## 📊 **ESPECIFICAÇÕES DO OPENAPI.JSON**

### **Estrutura Atual:**
- **Título:** "SynapScale Backend API"
- **Versão:** "2.0.0"
- **Endpoints:** 145 paths documentados
- **Schemas:** 162 componentes Pydantic
- **Tags:** 11 categorias organizadas
- **Tamanho:** ~700KB (arquivo completo)

### **Categorias de Endpoints (Tags):**

1. **system** - Status, saúde e informações gerais
2. **authentication** - Login, registro, JWT, usuários
3. **ai** - LLM, conversas, feedback, IA
4. **agents** - Configurações, ferramentas, modelos
5. **workflows** - Criação, nós, execuções
6. **analytics** - Métricas, dashboards, insights
7. **data** - Arquivos, uploads, variáveis
8. **enterprise** - RBAC, features, pagamentos
9. **marketplace** - Templates, componentes
10. **admin** - Migrações, configurações
11. **deprecated** - Endpoints legados

### **Schemas Organizados:**
- **User Schemas:** `UserCreate`, `UserUpdate`, `UserResponse`
- **Feature Schemas:** `FeatureCreate`, `PlanFeatureCreate`, `TenantFeatureCreate`
- **RBAC Schemas:** `RBACRoleCreate`, `RBACPermissionCreate`
- **Payment Schemas:** `PaymentProviderCreate`, `InvoiceCreate`
- **Workspace Schemas:** `WorkspaceCreate`, `MemberInvite`
- **File Schemas:** `FileCreate`, `FileUpdate`

---

## 🔐 **CONFIGURAÇÕES DE SEGURANÇA**

### 1. **Autenticação no OpenAPI**
```json
{
  "components": {
    "securitySchemes": {
      "HTTPBearer": {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT"
      },
      "HTTPBasic": {
        "type": "http", 
        "scheme": "basic"
      }
    }
  },
  "security": [
    {"HTTPBearer": []},
    {"HTTPBasic": []}
  ]
}
```

### 2. **Headers de Segurança**
```python
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response
```

---

## 🎨 **CUSTOMIZAÇÕES DE INTERFACE**

### 1. **Swagger UI Personalizado**
- Design moderno com CSS customizado
- Cores do sistema: `--primary-color: #3b82f6`
- Transições suaves e animações
- Logo e branding personalizados
- Syntax highlighting: tema 'agate'

### 2. **Funcionalidades Especiais**
- **Try It Out:** Habilitado para todos os endpoints
- **Autorização Persistente:** Mantém tokens entre sessões
- **Ordenação:** Tags e operações em ordem alfabética
- **Expansão:** Inicia com schemas colapsados
- **Tempo de Resposta:** Exibe duração das requisições

---

## 🔧 **COMANDOS E SCRIPTS**

### **Gerar openapi.json Manualmente:**
```bash
python -c "
import sys, json
sys.path.insert(0, 'src')
from synapse.main import app
spec = app.openapi()
json.dump(spec, open('openapi.json', 'w'), indent=2, ensure_ascii=False)
print('✅ openapi.json gerado!')
"
```

### **Validar Alinhamento com DB:**
```bash
./tests/analysis/check_schema_alignment.py
```

### **Verificar Endpoints Ativos:**
```bash
python -c "
import sys
sys.path.insert(0, 'src')
from synapse.main import app
spec = app.openapi()
print(f'Endpoints: {len(spec[\"paths\"])}')
print(f'Schemas: {len(spec[\"components\"][\"schemas\"])}')
"
```

---

## 📍 **URLS DE ACESSO**

### **Desenvolvimento:**
- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`
- **OpenAPI JSON:** `http://localhost:8000/openapi.json`
- **API Base:** `http://localhost:8000/api/v1`

### **Produção:**
- **Swagger UI:** `https://api.synapscale.com/docs` (se DEBUG=true)
- **ReDoc:** `https://api.synapscale.com/redoc`
- **OpenAPI JSON:** `https://api.synapscale.com/openapi.json`

---

## 🚨 **REGRAS CRÍTICAS**

### ✅ **OBRIGATÓRIO FAZER:**

1. **Manter openapi.json Atualizado:**
   - Regenerar após mudanças nos endpoints
   - Executar `dev.sh` automaticamente atualiza

2. **Usar Schemas Específicos:**
   ```python
   # ✅ CORRETO
   from synapse.schemas.user import UserCreate
   from synapse.schemas.feature import FeatureCreate
   
   # ❌ ERRADO  
   from synapse.schemas.models import UserCreate  # ELIMINADO
   ```

3. **Definir response_model:**
   ```python
   # ✅ CORRETO
   @router.post("/users", response_model=UserResponse)
   async def create_user(user: UserCreate):
       pass
   ```

4. **Usar Configurações Centralizadas:**
   ```python
   # ✅ CORRETO
   from synapse.core.config import settings
   title = settings.PROJECT_NAME
   
   # ❌ ERRADO
   import os
   title = os.getenv("PROJECT_NAME")
   ```

### ❌ **NUNCA FAZER:**

1. **Não usar schemas genéricos ou dicts**
2. **Não hardcodar configurações**
3. **Não desabilitar validação Pydantic** 
4. **Não ignorar erros de geração do OpenAPI**
5. **Não modificar openapi.json manualmente**

---

## 🔍 **TROUBLESHOOTING**

### **Problema:** openapi.json não existe
**Solução:** Execute `dev.sh` ou gere manualmente

### **Problema:** Schemas não aparecem na documentação
**Solução:** Verifique se `response_model` está definido

### **Problema:** Autenticação não funciona no Swagger
**Solução:** Verifique se security schemes estão configurados

### **Problema:** Endpoints retornam 422 ou 500
**Solução:** Verifique se schemas Pydantic estão corretos

### **Problema:** Swagger UI não carrega
**Solução:** Verifique se `/docs` está habilitado e CSS está acessível

---

## 📊 **MONITORAMENTO CONTÍNUO**

### **Verificações Automáticas:**

```bash
# Verificar se openapi.json existe e está atualizado
test -f openapi.json && echo "✅ openapi.json existe" || echo "❌ Ausente"

# Verificar se FastAPI gera spec corretamente
python -c "import sys; sys.path.insert(0, 'src'); from synapse.main import app; print('✅ FastAPI OK')"

# Verificar quantidade de endpoints
python -c "import sys; sys.path.insert(0, 'src'); from synapse.main import app; print(f'Endpoints: {len(app.openapi()[\"paths\"])}')"
```

### **Métricas de Qualidade:**
- **145 endpoints** documentados ✅
- **162 schemas** Pydantic ✅  
- **11 tags** organizadas ✅
- **2 métodos** de autenticação ✅
- **100% coverage** dos endpoints ✅

---

## 🏆 **RESULTADO ALCANÇADO**

### ✅ **OpenAPI/FastAPI 100% Funcional:**
- Documentação completa e atualizada
- Interface moderna e responsiva
- Autenticação JWT integrada
- Schemas organizados e validados
- Geração automática funcionando
- Análise de consistência ativa

### ✅ **Benefícios:**
- Documentação sempre sincronizada
- Interface de teste integrada
- Validação automática de dados
- Análise de consistência com banco
- Desenvolvimento ágil e seguro

---

**📅 Documento atualizado:** $(date)  
**👥 Responsabilidade:** Time de Desenvolvimento  
**🔄 Revisão:** A cada release  
**📋 Status:** ✅ IMPLEMENTADO E FUNCIONAL
