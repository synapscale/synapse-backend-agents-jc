# Guia de Contribuição

Este documento descreve as convenções e práticas recomendadas para contribuir com o projeto.

## Estrutura do Projeto

- **`packages/`**: Contém utilitários, constantes, hooks e outros módulos compartilhados entre os aplicativos.
- **`apps/`**: Contém os aplicativos individuais, como `ai-agents-sidebar`, `chat-interativo` e `node-sidebar`.
- **`components/`**: Contém componentes reutilizáveis específicos de UI.

## Convenções de Nomeação

- Use nomes descritivos para arquivos e pastas.
  - Exemplo: `date-utils.ts` para funções relacionadas a datas.
- Evite nomes genéricos como `utils.ts`.

## Organização de Código

- Centralize funções utilitárias em `packages/utils`.
- Evite duplicação de código entre os aplicativos.
- Cada arquivo deve ter uma responsabilidade clara.

## Estilo de Código

- Siga as regras definidas no arquivo `.eslintrc`.
- Use TypeScript para tipagem estática.

## Utilização de Utilitários Centralizados

- Todos os utilitários devem ser importados de `packages/utils`.
- Exemplos:
  ```typescript
  import { formatDate } from 'packages/utils/date-utils';
  import { validateForm } from 'packages/utils/form-validation';
  ```

## Como Contribuir

1. Faça um fork do repositório.
2. Crie uma branch para sua feature ou correção de bug.
3. Certifique-se de que seu código segue as convenções descritas acima.
4. Abra um pull request com uma descrição clara das mudanças.

## Testes

- Adicione testes para novas funcionalidades.
- Certifique-se de que todos os testes existentes passam antes de abrir um pull request.

Obrigado por contribuir com este projeto!
