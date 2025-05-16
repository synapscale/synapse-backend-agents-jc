"use client"

import { AgentsProvider } from "@/hooks/use-agents"
import { NodesProvider } from "@/hooks/use-nodes"
import { ThemeProvider } from "@/contexts/theme-context"

/**
 * Layout principal da aplicação
 * 
 * Este componente envolve toda a aplicação com os providers necessários
 * para compartilhamento de estado global.
 */
export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <ThemeProvider>
      <AgentsProvider>
        <NodesProvider>
          {children}
        </NodesProvider>
      </AgentsProvider>
    </ThemeProvider>
  )
}
