# Monorepo AI Agents JC (Consolidado)

## Estrutura

- `apps/ai-agents-sidebar/` — App Next.js para gerenciamento de agentes
- `apps/chat-interativo/` — App Next.js para chat interativo
- `apps/node-sidebar/` — App Next.js para visualização e manipulação de nodes
- `components/` — Componentes React compartilhados entre as aplicações
- `shared/` — Código compartilhado entre os projetos (hooks, utils, types, etc)
- `packages/` — Pacotes específicos e bibliotecas internas

## Como rodar

### Método Rápido
Execute o script de setup que configura tudo automaticamente:
```bash
./setup.sh
```

### Método Manual
1. Instale as dependências na raiz:
   ```bash
   pnpm install
   ```
2. Rode o projeto principal:
   ```bash
   pnpm dev
   ```
   Ou rode um app específico:
   ```bash
   cd apps/ai-agents-sidebar && pnpm dev
   # ou
   cd apps/chat-interativo && pnpm dev
   # ou
   cd node-sidebar && pnpm dev
   ```

## Boas práticas
- Sempre que criar algo reutilizável, coloque em `shared/`.
- Use o alias `@shared` para importar do compartilhado.
- Mantenha cada app isolado, mas aproveite o máximo de código comum.

---

Dúvidas? Consulte os READMEs de cada projeto ou abra uma issue.
