# Documentação de Integração

## Visão Geral

Este documento detalha a integração completa dos três ambientes principais do projeto AI Agents JC:

1. **Chat Interativo**: Interface avançada de chat com seleção de modelos, personalidades e ferramentas
2. **Ambiente de Agentes**: Sistema de criação, edição e gerenciamento de agentes
3. **Ambiente de Nodes**: Sistema de criação e gerenciamento de nodes para o canvas

A integração foi realizada mantendo a fidelidade visual e funcional absoluta aos designs originais do v0, conforme solicitado.

## Estrutura do Projeto

O projeto segue uma estrutura organizada e modular:

```
/
├── api/                  # Backend e endpoints
│   ├── agent_src/        # Código fonte dos agentes
│   ├── chat.py           # API de chat
│   └── requirements.txt  # Dependências do backend
├── app/                  # Páginas e rotas
│   ├── agentes/          # Páginas de agentes
│   ├── canvas/           # Páginas de canvas
│   ├── chat/             # Páginas de chat
│   └── nodes/            # Páginas de nodes
├── components/           # Componentes React
│   ├── agents/           # Componentes de agentes
│   ├── chat/             # Componentes de chat
│   │   ├── chat-input/   # Componentes de entrada de chat
│   │   ├── header/       # Componentes de cabeçalho
│   │   └── model-selector/ # Seletor de modelos
│   ├── node-sidebar/     # Componentes de sidebar de nodes
│   ├── ui/               # Componentes de UI compartilhados
│   └── sidebar.tsx       # Sidebar principal
├── contexts/             # Contextos React
├── hooks/                # Hooks personalizados
├── lib/                  # Utilitários
├── public/               # Arquivos estáticos
├── styles/               # Estilos globais
└── types/                # Definições de tipos
```

## Componentes Principais

### Chat Interativo

Os componentes do chat foram integrados mantendo o design e funcionalidade originais do v0:

- **ChatInterface**: Componente principal que orquestra a experiência de chat
- **ChatInput**: Entrada de mensagens com suporte a upload de arquivos
- **ModelSelector**: Seleção de modelos de IA
- **PersonalitySelector**: Seleção de personalidades para o chat
- **ToolSelector**: Seleção de ferramentas disponíveis
- **MessagesArea**: Área de exibição de mensagens
- **AIProcessingInfo**: Informações sobre o processamento da IA

### Ambiente de Agentes

Os componentes de agentes foram integrados preservando o design original:

- **AgentCard**: Card de visualização de agentes
- **AgentBasicInfo**: Informações básicas do agente
- **AgentConnectionsTab**: Aba de conexões do agente
- **AgentParametersTab**: Aba de parâmetros do agente
- **AgentPromptTab**: Aba de prompt do agente
- **PromptEditor**: Editor de prompts para agentes
- **AgentsList**: Lista de agentes disponíveis

### Ambiente de Nodes

Os componentes de nodes foram integrados mantendo a fidelidade visual:

- **NodeSidebar**: Sidebar para gerenciamento de nodes
- **NodeCategory**: Categorias de nodes
- **NodeForm**: Formulário de criação/edição de nodes
- **NodeTemplateCard**: Card de template de node

## Navegação

A navegação foi unificada em uma única sidebar, conforme solicitado, permitindo acesso a todas as seções do projeto:

- **Editor de Workflow** (`/canvas`): Ambiente de canvas para workflow
- **Agentes** (`/agentes`): Gerenciamento de agentes
- **Nodes** (`/nodes`): Gerenciamento de nodes
- **Chat Interativo** (`/chat`): Interface de chat
- **Documentação** (`/docs`): Documentação do projeto
- **Configurações** (`/settings`): Configurações do sistema

## Endpoints de Backend

Os endpoints necessários para suportar as funcionalidades foram implementados:

- **/api/chat**: Processamento de mensagens de chat
- **/api/agents**: CRUD de agentes
- **/api/nodes**: CRUD de nodes
- **/api/canvas**: Operações de canvas

## Fluxos de Dados

Os fluxos de dados entre componentes e entre frontend e backend foram implementados de forma robusta:

1. **Fluxo de Chat**:
   - Entrada de usuário → Processamento de mensagem → Resposta da IA
   - Upload de arquivos → Processamento → Inclusão na conversa

2. **Fluxo de Agentes**:
   - Listagem → Visualização → Edição → Salvamento
   - Criação → Configuração → Salvamento

3. **Fluxo de Nodes**:
   - Categorização → Seleção → Configuração → Adição ao canvas

## Considerações Técnicas

- **Fidelidade Visual**: Todos os componentes mantêm o design exato do v0
- **Robustez**: Implementação sem gambiarras ou soluções improvisadas
- **Modularidade**: Componentes organizados de forma clara e modular
- **Responsividade**: Interface adaptável a diferentes tamanhos de tela
- **Acessibilidade**: Componentes seguem práticas de acessibilidade

## Como Utilizar

1. **Instalação**:
   ```bash
   npm install
   # ou
   yarn install
   ```

2. **Execução em Desenvolvimento**:
   ```bash
   npm run dev
   # ou
   yarn dev
   ```

3. **Build para Produção**:
   ```bash
   npm run build
   # ou
   yarn build
   ```

## Próximos Passos

- Implementação de testes automatizados
- Otimização de performance
- Expansão de funcionalidades de marketplace
- Integração com sistemas externos

---

Esta documentação reflete o estado atual da integração, que foi realizada mantendo a fidelidade absoluta aos designs originais do v0, conforme solicitado.
