"use client"

import type React from "react"
import { useState, useRef, useEffect } from "react"
import { X, Plus } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"
import type { BadgeListProps } from "@/types/component-params"

/**
 * A component for displaying and managing a list of badges
 *
 * This component allows users to view, add, edit, and remove badges.
 * It's useful for managing tags, categories, or any other list of items.
 *
 * @example
 * ```tsx
 * <BadgeList
 *   items={tags}
 *   onAdd={addTag}
 *   onRemove={removeTag}
 *   onEdit={editTag}
 *   addLabel="Tag"
 *   maxItems={10}
 *   emptyMessage="No tags added yet"
 * />
 * ```
 *
 * @param props - Component properties
 * @returns React component
 */
export function BadgeList({
  // Required props
  items,
  onAdd,
  onRemove,

  // Optional props with defaults
  onEdit,
  addLabel = "Item",
  maxItems = 10,
  className,
  emptyMessage = "Nenhum item adicionado",
  readOnly = false,
  addButtonVariant = "outline",
  badgeVariant = "secondary",
  sortable = false,
  onReorder,
  confirmRemoval = false,
  removeBadgeAriaLabel,

  // Accessibility props
  id,
  testId,
  ariaLabel,
}: BadgeListProps) {
  const [editingId, setEditingId] = useState<string | null>(null)
  const [editValue, setEditValue] = useState("")
  const inputRef = useRef<HTMLInputElement>(null)

  // Focus input when editing starts
  useEffect(() => {
    if (editingId && inputRef.current) {
      inputRef.current.focus()
    }
  }, [editingId])

  const handleStartEdit = (item: { id: string; label: string }) => {
    if (onEdit && !readOnly) {
      setEditingId(item.id)
      setEditValue(item.label)
    }
  }

  const handleSaveEdit = () => {
    if (editingId && onEdit && editValue.trim()) {
      onEdit(editingId, editValue.trim())
      setEditingId(null)
      setEditValue("")
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      e.preventDefault()
      handleSaveEdit()
    } else if (e.key === "Escape") {
      setEditingId(null)
      setEditValue("")
    }
  }

  const handleRemove = (id: string) => {
    if (confirmRemoval) {
      if (window.confirm("Are you sure you want to remove this item?")) {
        onRemove(id)
      }
    } else {
      onRemove(id)
    }
  }

  const componentId = id || "badge-list"

  return (
    <div
      className={cn("space-y-3", className)}
      id={componentId}
      data-testid={testId}
      aria-label={ariaLabel || `List of ${addLabel.toLowerCase()}s`}
    >
      <div className="flex flex-wrap gap-2">
        {items.length === 0 ? (
          <p className="text-sm text-muted-foreground">{emptyMessage}</p>
        ) : (
          items.map((item) => (
            <div key={item.id} className="flex items-center">
              {editingId === item.id && onEdit && !readOnly ? (
                <div className="flex items-center border rounded-md overflow-hidden">
                  <Input
                    ref={inputRef}
                    type="text"
                    value={editValue}
                    onChange={(e) => setEditValue(e.target.value)}
                    onBlur={handleSaveEdit}
                    onKeyDown={handleKeyDown}
                    className="h-7 min-w-[150px] border-0 focus-visible:ring-0 focus-visible:ring-offset-0"
                    aria-label={`Edit ${addLabel.toLowerCase()}`}
                    data-testid={`${componentId}-edit-input-${item.id}`}
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    className="h-7 px-2"
                    onClick={() => setEditingId(null)}
                    aria-label="Cancel editing"
                  >
                    <X className="h-3 w-3" aria-hidden="true" />
                    <span className="sr-only">Cancelar</span>
                  </Button>
                </div>
              ) : (
                <Badge
                  variant={badgeVariant}
                  className="px-2 py-1 h-7 text-xs font-normal bg-gray-100 hover:bg-gray-200 group"
                >
                  <span
                    className={cn("mr-1", onEdit && !readOnly && "cursor-pointer hover:underline")}
                    onClick={() => onEdit && !readOnly && handleStartEdit(item)}
                    data-testid={`${componentId}-label-${item.id}`}
                  >
                    {item.label}
                  </span>
                  {!readOnly && (
                    <button
                      type="button"
                      onClick={() => handleRemove(item.id)}
                      className="inline-flex items-center justify-center rounded-full h-4 w-4 bg-gray-200 group-hover:bg-gray-300 transition-colors"
                      aria-label={
                        removeBadgeAriaLabel
                          ? removeBadgeAriaLabel.replace("{label}", item.label)
                          : `Remover ${item.label}`
                      }
                      data-testid={`${componentId}-remove-${item.id}`}
                    >
                      <X className="h-2.5 w-2.5" aria-hidden="true" />
                    </button>
                  )}
                </Badge>
              )}
            </div>
          ))
        )}
      </div>

      {!readOnly && items.length < maxItems && (
        <Button
          type="button"
          variant={addButtonVariant}
          size="sm"
          onClick={onAdd}
          className="h-8 text-xs bg-white hover:bg-gray-50"
          aria-label={`Adicionar ${addLabel}`}
          data-testid={`${componentId}-add-button`}
        >
          <Plus className="mr-1 h-3.5 w-3.5" aria-hidden="true" />
          Adicionar {addLabel}
        </Button>
      )}
    </div>
  )
}
