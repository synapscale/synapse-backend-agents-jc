# Pasta shared/

Esta pasta contém todo o código compartilhado entre os projetos do monorepo.

- `components/` — componentes React reutilizáveis
- `ui/` — componentes de UI atômicos (botão, input, etc)
- `hooks/` — hooks customizados
- `utils/` — funções utilitárias
- `constants/` — constantes globais
- `types/` — tipos TypeScript globais
- `icons/` — ícones SVG/componentes

## Como usar

Importe qualquer recurso compartilhado usando o alias `@shared`:

```tsx
import { SidebarNavItem } from '@shared/sidebar/sidebar-nav-item'
import { useMobile } from '@shared/hooks/use-mobile'
```

Se criar algo reutilizável, coloque aqui!
