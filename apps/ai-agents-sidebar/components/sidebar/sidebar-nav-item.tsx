import * as React from "react"
import Link from "next/link"
import { cn } from "@/lib/utils"
import { SidebarMenuButton, SidebarMenuItem } from "@/components/ui/sidebar"

interface SidebarNavItemProps {
  href: string
  icon: React.ReactNode
  label: string
  isActive: boolean
  className?: string
}

export function SidebarNavItem({ href, icon, label, isActive, className }: SidebarNavItemProps) {
  return (
    <SidebarMenuItem>
      <SidebarMenuButton
        asChild
        isActive={isActive}
        className={cn("transition-colors py-1.5 sm:py-2 text-xs sm:text-sm", className)}
      >
        <Link href={href}>
          {React.cloneElement(icon as React.ReactElement, {
            className: "mr-2 h-3.5 w-3.5 sm:h-4 sm:w-4",
            "aria-hidden": "true",
          })}
          <span>{label}</span>
        </Link>
      </SidebarMenuButton>
    </SidebarMenuItem>
  )
}

// Arquivo migrado para packages/ui/sidebar/SidebarNavItem.tsx
// Utilize apenas o componente compartilhado.
