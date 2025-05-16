"use client"

import type React from "react"

import { ChevronRight, MoreHorizontal } from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"
import { useTheme } from "@/contexts/theme-context"
import type { NodeCategoryProps } from "@/types/core/node-types"

/**
 * NodeCategory Component
 *
 * Displays a draggable category item representing a node type or category.
 * Supports actions like edit and delete through a dropdown menu.
 * Uses theme context to apply appropriate styling based on the category.
 *
 * @example
 * \`\`\`tsx
 * <NodeCategory
 *   id="text-processor"
 *   name="Text Processor"
 *   description="Processes text input using NLP techniques"
 *   category="text-processing"
 *   isUserNode={true}
 *   onEdit={() => handleEdit("text-processor")}
 *   onDelete={() => handleDelete("text-processor")}
 * />
 * \`\`\`
 */
export function NodeCategory({
  // Required props
  name,
  description,

  // Optional identification props
  id,
  category = "core",

  // State props
  isUserNode = false,
  isExpanded = false,
  disabled = false,

  // Action handlers
  onClick,
  onEdit,
  onDelete,
  onExpandedChange,

  // Drag-related props
  isDraggable = true,
  dragData,
  onDragStart,
  onDragEnd,

  // Visual customization
  icon,
  showActions = true,
  nodeCount,

  // Tooltip props
  tooltip,
  tooltipPosition = "top",
  tooltipDelay = 500,
  tooltipDisabled = false,

  // Accessibility and testing
  className,
  testId,
  ariaLabel,

  // Other props
  ...otherProps
}: NodeCategoryProps) {
  // Get theme context
  const { currentTheme } = useTheme()

  // Get theme colors for this node type
  const nodeTheme = currentTheme.nodeColors[category] || currentTheme.nodeColors.core

  // Prepare drag data
  const handleDragStart = (e: React.DragEvent) => {
    if (disabled || !isDraggable) {
      e.preventDefault()
      return
    }

    // Set drag data
    const data = dragData || { type: "node", id, name, category }
    e.dataTransfer.setData("application/json", JSON.stringify(data))

    // Create a preview image for the drag
    const dragPreview = document.createElement("div")
    dragPreview.className = `bg-white p-2 rounded border shadow-md text-sm ${nodeTheme.border}`
    dragPreview.textContent = name
    dragPreview.style.position = "absolute"
    dragPreview.style.top = "-1000px"
    document.body.appendChild(dragPreview)

    // Set the preview image
    try {
      e.dataTransfer.setDragImage(dragPreview, 0, 0)
    } catch (err) {
      console.error("Error setting drag image:", err)
    }

    // Remove the element after a short period
    setTimeout(() => {
      document.body.removeChild(dragPreview)
    }, 0)

    // Call custom drag start handler if provided
    onDragStart?.(e)
  }

  // Handle click
  const handleClick = (e: React.MouseEvent) => {
    if (!disabled) {
      onClick?.(e)

      // Toggle expanded state if handler provided
      if (onExpandedChange) {
        onExpandedChange(!isExpanded)
      }
    }
  }

  // Render the component
  const categoryItem = (
    <div
      className={cn(
        "relative flex items-start gap-3 rounded-md border p-3 transition-colors",
        !disabled && "hover:bg-accent cursor-pointer group",
        disabled && "opacity-60 cursor-not-allowed",
        nodeTheme.border,
        className,
      )}
      draggable={isDraggable && !disabled}
      onDragStart={handleDragStart}
      onDragEnd={onDragEnd}
      onClick={handleClick}
      data-testid={testId}
      aria-label={ariaLabel || `Node category: ${name}`}
      aria-disabled={disabled}
      aria-expanded={isExpanded}
      {...otherProps}
    >
      {isUserNode && showActions && (
        <div className="absolute right-2 top-2">
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                variant="ghost"
                size="icon"
                className="h-7 w-7 opacity-0 group-hover:opacity-100"
                disabled={disabled}
                aria-label="Category options"
              >
                <MoreHorizontal className="h-4 w-4" />
                <span className="sr-only">Mais opções</span>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              {onEdit && (
                <DropdownMenuItem
                  onClick={(e) => {
                    e.stopPropagation()
                    onEdit()
                  }}
                >
                  Editar
                </DropdownMenuItem>
              )}
              {onDelete && (
                <DropdownMenuItem
                  onClick={(e) => {
                    e.stopPropagation()
                    onDelete()
                  }}
                  className="text-destructive"
                >
                  Excluir
                </DropdownMenuItem>
              )}
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      )}

      {icon && <div className="flex-shrink-0 mt-0.5">{icon}</div>}

      <div className="flex-1 min-w-0">
        <div className="flex items-center">
          <h4 className={cn("text-sm font-medium leading-none truncate", nodeTheme.text)}>{name}</h4>
          {nodeCount !== undefined && <span className="ml-2 text-xs text-muted-foreground">({nodeCount})</span>}
        </div>
        <p className="mt-1 text-xs text-muted-foreground line-clamp-2">{description}</p>
      </div>

      <ChevronRight
        className={cn(
          "h-4 w-4 text-muted-foreground transition-all",
          isExpanded ? "transform rotate-90" : "opacity-0 group-hover:opacity-100",
        )}
      />
    </div>
  )

  // Add tooltip if provided
  if (tooltip && !tooltipDisabled) {
    return (
      <TooltipProvider>
        <Tooltip delayDuration={tooltipDelay}>
          <TooltipTrigger asChild>{categoryItem}</TooltipTrigger>
          <TooltipContent side={tooltipPosition}>{tooltip}</TooltipContent>
        </Tooltip>
      </TooltipProvider>
    )
  }

  return categoryItem
}
