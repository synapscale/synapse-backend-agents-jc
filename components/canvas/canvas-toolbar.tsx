"use client"

import type React from "react"

import { Undo2, Redo2, ZoomIn, ZoomOut, Save } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"
import { useCanvas } from "@/contexts/canvas-context"
import { ThemeSelector } from "./theme-selector"
import { memo } from "react"

/**
 * ToolbarButton Component
 *
 * Reusable button component for the canvas toolbar with tooltip.
 */
const ToolbarButton = memo(
  ({
    icon: Icon,
    label,
    onClick,
    disabled = false,
    tooltipContent,
  }: {
    icon: React.ElementType
    label: string
    onClick?: () => void
    disabled?: boolean
    tooltipContent: string
  }) => (
    <Tooltip>
      <TooltipTrigger asChild>
        <Button
          variant="ghost"
          size="icon"
          onClick={onClick}
          disabled={disabled}
          className="h-8 w-8"
          aria-label={label}
        >
          <Icon className="h-4 w-4" aria-hidden="true" />
          <span className="sr-only">{label}</span>
        </Button>
      </TooltipTrigger>
      <TooltipContent>
        <p>{tooltipContent}</p>
      </TooltipContent>
    </Tooltip>
  ),
)

ToolbarButton.displayName = "ToolbarButton"

/**
 * Divider Component
 *
 * Simple vertical divider for the toolbar.
 */
const Divider = memo(() => <div className="h-4 mx-1 border-r border-gray-300" aria-hidden="true" />)

Divider.displayName = "Divider"

/**
 * CanvasToolbar Component
 *
 * Toolbar for the canvas with undo, redo, zoom, save, and theme selection options.
 */
export function CanvasToolbar() {
  const { undo, redo, canUndo, canRedo } = useCanvas()

  return (
    <div className="absolute top-4 left-1/2 transform -translate-x-1/2 z-10 bg-background border rounded-lg shadow-md flex items-center p-1">
      <TooltipProvider>
        <ToolbarButton
          icon={Undo2}
          label="Desfazer"
          onClick={undo}
          disabled={!canUndo}
          tooltipContent="Desfazer (Ctrl+Z)"
        />

        <ToolbarButton
          icon={Redo2}
          label="Refazer"
          onClick={redo}
          disabled={!canRedo}
          tooltipContent="Refazer (Ctrl+Y)"
        />

        <Divider />

        <ToolbarButton icon={ZoomIn} label="Ampliar" tooltipContent="Ampliar" />

        <ToolbarButton icon={ZoomOut} label="Reduzir" tooltipContent="Reduzir" />

        <Divider />

        <ToolbarButton icon={Save} label="Salvar" tooltipContent="Salvar Fluxo" />

        <Divider />

        <ThemeSelector />
      </TooltipProvider>
    </div>
  )
}
