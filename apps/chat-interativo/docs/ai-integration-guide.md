# Guia de Integração com IA

Este documento fornece orientações sobre como o código deste projeto foi estruturado para facilitar a integração e manipulação por ferramentas de IA.

## Princípios AI-Friendly

O código deste projeto segue vários princípios para ser facilmente compreendido e modificado por ferramentas de IA:

1. **Documentação abrangente**: Componentes, funções e tipos são documentados com comentários JSDoc detalhados.
2. **Tipagem explícita**: TypeScript é usado com tipos explícitos para todas as estruturas de dados.
3. **Nomes descritivos**: Variáveis, funções e componentes têm nomes que descrevem claramente seu propósito.
4. **Estrutura modular**: O código é organizado em módulos coesos com responsabilidades bem definidas.
5. **Separação de preocupações**: Lógica de negócios, UI e gerenciamento de estado são separados.
6. **Padrões consistentes**: Convenções de nomenclatura e estrutura são aplicadas consistentemente.

## Estrutura de Arquivos

O projeto segue uma estrutura organizada para facilitar a navegação:

- `/components`: Componentes React reutilizáveis
  - `/chat`: Componentes específicos para a interface de chat
  - `/component-selector`: Componentes para seleção e inspeção de elementos da UI
  - `/common`: Componentes utilitários compartilhados
  - `/ui`: Componentes de UI básicos (botões, inputs, etc.)
- `/contexts`: Contextos React para gerenciamento de estado global
- `/hooks`: Hooks React personalizados
- `/lib`: Funções utilitárias e constantes
- `/types`: Definições de tipos TypeScript
- `/app`: Rotas e páginas da aplicação Next.js

## Tipos AI-Friendly

O arquivo `types/ai-helpers.ts` contém tipos especialmente projetados para facilitar a integração com IA:

- `AIDetectableComponent`: Representa um componente que pode ser detectado e manipulado
- `AIProcessableMessage`: Representa uma mensagem que pode ser processada por modelos de IA
- `AIModelConfig`: Configuração para interação com modelos de IA
- `AIPersonalityConfig`: Configuração para personalidade do assistente de IA
- `AIToolConfig`: Configuração para ferramentas que podem ser usadas pela IA
- `AIUserPreferences`: Configuração para preferências do usuário relacionadas à IA

## Utilitários AI-Friendly

O arquivo `lib/ai-utils.ts` contém funções utilitárias para facilitar a interação com modelos de IA:

- `formatMessageForAI`: Formata uma mensagem para processamento por IA
- `extractReferencedComponents`: Extrai componentes referenciados de uma mensagem
- `formatComponentForPrompt`: Formata um componente para uso em prompts
- `estimateTokenCount`: Estima o número de tokens em um texto
- `modelHasCapability`: Verifica se um modelo tem uma capacidade específica
- `extractCodeFromResponse`: Extrai blocos de código de uma resposta de IA

## Componentes Principais

### ChatInterface

O componente principal que integra todos os elementos da interface de chat. Foi projetado para ser facilmente compreendido e modificado por IA, com:

- Tipos explícitos para todas as props e estados
- Funções com nomes descritivos e propósito claro
- Comentários explicando a lógica complexa
- Separação clara entre UI e lógica de negócios

### ComponentSelector

Uma ferramenta que permite selecionar e inspecionar componentes na interface. É especialmente útil para interações com IA onde componentes específicos precisam ser referenciados.

### AppContext

O contexto global da aplicação que gerencia o estado compartilhado. Foi projetado para ser facilmente compreendido e manipulado por IA, com:

- Tipos explícitos para todos os valores e funções
- Valores padrão bem definidos
- Funções de atualização com lógica clara
- Persistência de estado no localStorage

## Melhores Práticas para Modificações por IA

Ao solicitar modificações por IA, considere as seguintes práticas:

1. **Referencie componentes específicos**: Use o nome exato do componente e seu caminho de arquivo.
2. **Especifique tipos**: Mencione os tipos relevantes ao solicitar modificações.
3. **Descreva comportamentos**: Explique o comportamento esperado, não apenas a aparência.
4. **Forneça exemplos**: Quando possível, forneça exemplos de uso ou comportamento esperado.
5. **Use a terminologia do projeto**: Utilize os mesmos termos e conceitos usados no código.

## Exemplo de Solicitação Eficaz

\`\`\`
Modifique o componente ChatInput em components/chat/chat-input/index.tsx para:
1. Adicionar suporte para envio de imagens
2. Implementar um contador de tokens usando a função estimateTokenCount do lib/ai-utils.ts
3. Adicionar um indicador visual quando o usuário se aproximar do limite de tokens

Certifique-se de atualizar o tipo ChatInputProps em components/chat/chat-input/types.ts para incluir as novas propriedades.
\`\`\`

## Recursos Adicionais

- [Documentação do TypeScript](https://www.typescriptlang.org/docs/)
- [Documentação do React](https://reactjs.org/docs/getting-started.html)
- [Documentação do Next.js](https://nextjs.org/docs)
\`\`\`

## 7. Vamos criar um arquivo de constantes AI-friendly:
