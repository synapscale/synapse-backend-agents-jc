# 📋 Organização da Documentação da API - SynapScale

> **Versão**: 2.0.0  
> **Atualizado**: Dezembro 2024  
> **Status**: ✅ Reorganizado e Otimizado  

## 🎯 Visão Geral

A documentação da API foi completamente reorganizada para ser **mais clara, funcional e intuitiva**. Eliminamos duplicações e categorizamos os endpoints de forma lógica e hierárquica.

## 📚 Estrutura Hierárquica

### 🔐 **AUTENTICAÇÃO E AUTORIZAÇÃO**
- **Tag**: `authentication`
- **Endpoints**: Login, registro, logout, recuperação de senha, verificação de email
- **Localização**: `/api/v1/auth/*`

### 🏠 **INFORMAÇÕES BÁSICAS**
- **Tags**: `root`, `health`, `info`
- **Endpoints**: Status da aplicação, saúde do sistema, informações da API
- **Localização**: `/`, `/health`, `/info`

### 👥 **GESTÃO DE WORKSPACES**
- **Tags**: `workspaces`, `workspace-members`, `workspace-activities`
- **Endpoints**: CRUD de workspaces, gerenciamento de membros, histórico de atividades
- **Localização**: `/api/v1/workspaces/*`

### ⚙️ **WORKFLOWS E AUTOMAÇÃO**
- **Tags**: `workflows`, `executions`, `executions-control`, `executions-monitoring`
- **Funcionalidades**:
  - **workflows**: Criação e gestão de workflows
  - **executions**: Execução de workflows
  - **executions-control**: Controle (pausar, cancelar, retry)
  - **executions-monitoring**: Monitoramento e logs
- **Localização**: `/api/v1/workflows/*`, `/api/v1/executions/*`

### 🔗 **COMPONENTES E NODOS**
- **Tags**: `nodes`, `templates`
- **Funcionalidades**:
  - **nodes**: Nós e componentes para workflows
  - **templates**: Templates e modelos pré-configurados
- **Localização**: `/api/v1/nodes/*`, `/api/v1/templates/*`

### 🤖 **INTELIGÊNCIA ARTIFICIAL**
- **Tags**: `llm`, `agents`, `conversations`
- **Funcionalidades**:
  - **llm**: Modelos de linguagem e IA
  - **agents**: Agentes inteligentes
  - **conversations**: Conversas com agentes IA
- **Localização**: `/api/v1/llm/*`, `/api/v1/agents/*`, `/api/v1/conversations/*`

### 🛒 **MARKETPLACE**
- **Tags**: `marketplace`, `marketplace-components`, `marketplace-ratings`
- **Funcionalidades**:
  - **marketplace**: Marketplace de componentes
  - **marketplace-components**: Componentes disponíveis
  - **marketplace-ratings**: Avaliações e reviews
- **Localização**: `/api/v1/marketplace/*`

### 📊 **ANALYTICS E MÉTRICAS**
- **Tags**: `analytics`, `dashboards`, `reports`, `analysis`, `export`, `alerts`
- **Funcionalidades**:
  - **analytics**: Analytics e métricas gerais
  - **dashboards**: Dashboards personalizados
  - **reports**: Relatórios e exportações
  - **analysis**: Análises estatísticas
  - **export**: Exportação de dados
  - **alerts**: Alertas e notificações
- **Localização**: `/api/v1/analytics/*`

### 📁 **ARQUIVOS E DADOS**
- **Tags**: `files`, `user-variables`
- **Funcionalidades**:
  - **files**: Upload e gerenciamento de arquivos
  - **user-variables**: Variáveis e configurações do usuário
- **Localização**: `/api/v1/files/*`, `/api/v1/user-variables/*`

### 🔌 **COMUNICAÇÃO EM TEMPO REAL**
- **Tag**: `websockets`
- **Funcionalidades**: Conexões WebSocket em tempo real
- **Localização**: `/api/v1/ws/*`

### ⚙️ **ADMINISTRAÇÃO**
- **Tag**: `admin`
- **Funcionalidades**: Funcionalidades administrativas
- **Localização**: Distribuído em diversos endpoints com permissão admin

## 🔄 Principais Mudanças

### ❌ **Removido** (Duplicações e Tags Desnecessárias)
- ~~`auth`~~ → Consolidado em `authentication`
- ~~`analytics-dashboards`~~ → Simplificado para `dashboards`
- ~~`analytics-reports`~~ → Simplificado para `reports`
- ~~`analytics-insights`~~ → Renomeado para `analysis`
- ~~`analytics-export`~~ → Simplificado para `export`
- ~~`system-alerts`~~ → Simplificado para `alerts`
- ~~`executions-logs`~~ → Consolidado em `executions-monitoring`
- ~~`executions-queue`~~ → Consolidado em `executions-monitoring`
- ~~`executions-validation`~~ → Consolidado em `executions`
- ~~`executions-batch`~~ → Consolidado em `executions-control`

### ✅ **Adicionado** (Melhor Organização)
- **Hierarquia clara**: Categorias principais bem definidas
- **Tags específicas**: Para funcionalidades que precisam de subcategorizações
- **Ordem lógica**: Autenticação primeiro, depois funcionalidades por importância

## 🎯 **Como Navegar na Documentação**

### 1. **Começar pela Autenticação**
- Sempre comece pelos endpoints de `authentication`
- Configure seu token JWT antes de testar outros endpoints

### 2. **Seguir a Hierarquia**
- Use a ordem das seções conforme documentado
- Cada seção tem dependências lógicas da anterior

### 3. **Usar Filtros**
- Use os filtros por tags na documentação Swagger
- Cada tag agrupa endpoints relacionados

### 4. **Testar Progressivamente**
- Comece com endpoints simples (GET)
- Avance para operações mais complexas (POST, PUT, DELETE)

## 📖 **Exemplos de Uso**

### 🔐 **Fluxo de Autenticação**
```bash
1. POST /api/v1/auth/login → Obter token
2. GET /api/v1/auth/me → Verificar usuário
3. Usar token em outros endpoints
```

### ⚙️ **Fluxo de Workflow**
```bash
1. GET /api/v1/workflows/ → Listar workflows
2. POST /api/v1/workflows/ → Criar workflow
3. POST /api/v1/executions/ → Executar workflow
4. GET /api/v1/executions/{id} → Monitorar execução
```

### 📊 **Fluxo de Analytics**
```bash
1. GET /api/v1/analytics/overview → Visão geral
2. POST /api/v1/analytics/dashboards → Criar dashboard
3. GET /api/v1/analytics/dashboards/{id}/data → Ver dados
```

## 🚀 **Benefícios da Nova Organização**

- ✅ **Mais Intuitive**: Navegação lógica e hierárquica
- ✅ **Menos Confuso**: Eliminação de tags duplicadas
- ✅ **Mais Rápido**: Encontre endpoints facilmente
- ✅ **Melhor UX**: Experiência de desenvolvedor aprimorada
- ✅ **Consistente**: Padrões unificados em toda a API

## 📞 **Suporte**

Se você encontrar algum problema com a organização ou tiver sugestões:
- 📧 Email: support@synapscale.com
- 🐛 Issues: GitHub Issues
- 📖 Docs: Documentação completa

---

**💡 Dica**: Use o botão "Authorize" na documentação Swagger para configurar sua autenticação uma vez e testar todos os endpoints facilmente! 