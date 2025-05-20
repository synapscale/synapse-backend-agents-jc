# Documentação do Fluxo de Desenvolvimento

## Visão Geral

Este projeto foi unificado para integrar todos os setores (dashboard, agentes, chat, workflow) em uma única aplicação coesa, com uma sidebar centralizada e estrutura de componentes padronizada.

## Estrutura do Projeto

- `/components`: Componentes centralizados e reutilizáveis
  - `/sidebar`: Componentes de navegação lateral
  - `/chat`: Componentes do chat interativo
  - `/workflow`: Componentes do editor de workflow
  - `/ui`: Componentes de UI compartilhados
  - `/forms`: Componentes de formulários

- `/apps/ai-agents-sidebar`: Aplicação principal Next.js
  - `/app`: Rotas e páginas da aplicação
    - `/dashboard`: Dashboard principal
    - `/agentes`: Gerenciamento de agentes
    - `/chat`: Chat interativo integrado
    - `/workflow`: Editor de workflow integrado
    - `/settings`: Configurações

- `/shared`: Utilitários, hooks e tipos compartilhados
  - `/constants`: Constantes compartilhadas
  - `/hooks`: Hooks personalizados
  - `/types`: Definições de tipos
  - `/utils`: Funções utilitárias

## Aliases de Importação

Para facilitar as importações, foram configurados os seguintes aliases:

```javascript
// Exemplos de importação
import { Sidebar } from "@components/sidebar";
import { ChatInterface } from "@chat/chat-interface";
import { NodeSidebar } from "@workflow/node-sidebar";
import { useForm } from "@hooks/use-form";
```

## Scripts Disponíveis

- `pnpm dev`: Inicia o servidor de desenvolvimento
- `pnpm build`: Compila o projeto para produção
- `pnpm start`: Inicia o servidor de produção
- `pnpm lint`: Executa verificação de linting

## Fluxo de Trabalho Recomendado

1. Clone o repositório
2. Instale as dependências com `pnpm install`
3. Execute o servidor de desenvolvimento com `pnpm dev`
4. Acesse http://localhost:3000 para visualizar a aplicação

## Boas Práticas

- Utilize os aliases de importação para manter o código limpo
- Mantenha componentes relacionados nos diretórios apropriados
- Siga a estrutura de exportação via barrel files (index.ts)
- Evite importações circulares ou redundantes
- Mantenha a fidelidade visual e funcional dos designs originais
