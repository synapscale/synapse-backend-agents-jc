/**
 * ModelSelector Component
 *
 * A component for selecting AI models to use with the chat interface.
 * Displays available models grouped by provider and allows searching and filtering.
 */
"use client"
import { useState, useCallback } from "react"
import { ModelTrigger } from "./model-trigger"
import { ModelList } from "./model-list"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { useApp } from "@/contexts/app-context"
import type { BaseComponentProps } from "@/types/component-types"
import type { AIModel } from "@/types/chat"

/**
 * Props for the ModelSelector component
 */
export interface ModelSelectorProps extends BaseComponentProps {
  /**
   * List of available models to display
   * If not provided, models from the app context will be used
   */
  models?: AIModel[]

  /**
   * Callback fired when a model is selected
   * @param model The selected model
   */
  onModelSelect?: (model: AIModel) => void

  /**
   * Size of the selector button
   * @default "default"
   */
  size?: "sm" | "default" | "lg"

  /**
   * Width of the popover content
   * @default "320px"
   */
  contentWidth?: string

  /**
   * Maximum height of the model list
   * @default "400px"
   */
  maxHeight?: string

  /**
   * Whether to show the search input
   * @default true
   */
  showSearch?: boolean

  /**
   * Whether to show model descriptions
   * @default true
   */
  showDescriptions?: boolean

  /**
   * Whether to show model provider logos
   * @default true
   */
  showProviderLogos?: boolean

  /**
   * Whether to group models by provider
   * @default true
   */
  groupByProvider?: boolean

  /**
   * Placeholder text for the search input
   * @default "Search models..."
   */
  searchPlaceholder?: string

  /**
   * Text to display when no models are found
   * @default "No models found"
   */
  emptyStateText?: string

  /**
   * Side where the popover should be anchored
   * @default "bottom"
   */
  popoverSide?: "top" | "right" | "bottom" | "left"

  /**
   * Alignment of the popover
   * @default "start"
   */
  popoverAlign?: "start" | "center" | "end"
}

/**
 * ModelSelector component
 */
export default function ModelSelector({
  className = "",
  style,
  id,
  disabled = false,
  dataAttributes,
  models,
  onModelSelect,
  size = "default",
  contentWidth = "320px",
  maxHeight = "400px",
  showSearch = true,
  showDescriptions = true,
  showProviderLogos = true,
  groupByProvider = true,
  searchPlaceholder = "Search models...",
  emptyStateText = "No models found",
  popoverSide = "bottom",
  popoverAlign = "start",
}: ModelSelectorProps) {
  // SECTION: Local state
  const [open, setOpen] = useState(false)

  // SECTION: Application context
  const { selectedModel, setSelectedModel, availableModels } = useApp()

  // SECTION: Derived data
  const modelsToDisplay = models || availableModels

  // SECTION: Event handlers

  /**
   * Handle model selection
   */
  const handleSelectModel = useCallback(
    (model: AIModel) => {
      setSelectedModel(model)
      onModelSelect?.(model)
      setOpen(false)
    },
    [setSelectedModel, onModelSelect],
  )

  // Prepare data attributes
  const allDataAttributes = {
    "data-component": "ModelSelector",
    "data-component-path": "@/components/chat/model-selector",
    ...(dataAttributes || {}),
  }

  // SECTION: Render
  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <div className={className} style={style} id={id} {...allDataAttributes}>
          <ModelTrigger model={selectedModel} showLogo={showProviderLogos} size={size} disabled={disabled} />
        </div>
      </PopoverTrigger>
      <PopoverContent
        className="p-0 border border-gray-200 dark:border-gray-700 shadow-lg"
        style={{ width: contentWidth }}
        side={popoverSide}
        align={popoverAlign}
        sideOffset={4}
      >
        <ModelList
          models={modelsToDisplay}
          selectedModel={selectedModel}
          onSelect={handleSelectModel}
          showSearch={showSearch}
          showDescriptions={showDescriptions}
          showProviderLogos={showProviderLogos}
          groupByProvider={groupByProvider}
          searchPlaceholder={searchPlaceholder}
          emptyStateText={emptyStateText}
          maxHeight={maxHeight}
          disabled={disabled}
        />
      </PopoverContent>
    </Popover>
  )
}
