// Arquivo migrado para packages/ui/sidebar/SidebarNavSection.tsx
// Utilize apenas o componente compartilhado.

import type * as React from "react"
import { SidebarGroup, SidebarGroupContent, SidebarGroupLabel, SidebarMenu } from "@/components/ui/sidebar"

interface SidebarNavSectionProps {
  title: string
  children: React.ReactNode
}

export function SidebarNavSection({ title, children }: SidebarNavSectionProps) {
  return (
    <SidebarGroup>
      <SidebarGroupLabel className="text-xs font-medium text-muted-foreground">{title}</SidebarGroupLabel>
      <SidebarGroupContent>
        <SidebarMenu>{children}</SidebarMenu>
      </SidebarGroupContent>
    </SidebarGroup>
  )
}
