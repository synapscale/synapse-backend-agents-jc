"use client"

import type * as React from "react"
import { Button } from "@/components/ui/button"
import { Plus } from "lucide-react"
import { cn } from "@/lib/utils"

interface PromptTool {
  id: string
  name: string
  icon: React.ReactNode
}

interface PromptToolsBarProps {
  tools: PromptTool[]
  onToolClick?: (toolId: string) => void
  className?: string
}

/**
 * PromptToolsBar - Barra de ferramentas para o editor de prompt
 */
export function PromptToolsBar({ tools, onToolClick, className }: PromptToolsBarProps) {
  return (
    <div
      className={cn(
        "flex flex-nowrap gap-2 mb-3 overflow-x-auto pb-1 sm:pb-0 sm:flex-wrap sm:gap-3 scrollbar-hide",
        className,
      )}
      role="toolbar"
      aria-label="Ferramentas de prompt"
    >
      {tools.map((tool) => (
        <Button
          key={tool.id}
          variant="outline"
          size="sm"
          className="h-7 sm:h-8 text-xs rounded-full whitespace-nowrap flex-shrink-0"
          onClick={() => onToolClick?.(tool.id)}
          aria-label={`Adicionar ${tool.name}`}
        >
          {tool.icon}
          {tool.name}
          <Plus className="h-3 w-3 sm:h-3.5 sm:w-3.5 ml-1" aria-hidden="true" />
        </Button>
      ))}
    </div>
  )
}
