/**
 * ModelList Component
 *
 * Displays a list of AI models with search, filtering, and grouping capabilities.
 * Used by the ModelSelector component.
 */
"use client"
import { useState, useMemo } from "react"
import { Search } from "lucide-react"
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"
import { ModelItem } from "./model-item"
import { groupModelsByProvider } from "./utils"
import type { AIModel } from "@/types/chat"

/**
 * Props for the ModelList component
 */
export interface ModelListProps {
  /**
   * List of models to display
   */
  models: AIModel[]

  /**
   * Currently selected model
   */
  selectedModel: AIModel

  /**
   * Callback fired when a model is selected
   * @param model The selected model
   */
  onSelect: (model: AIModel) => void

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
   * Maximum height of the model list
   * @default "400px"
   */
  maxHeight?: string

  /**
   * Whether the component is disabled
   * @default false
   */
  disabled?: boolean

  /**
   * CSS class name for the component
   */
  className?: string
}

/**
 * ModelList component
 */
export function ModelList({
  models,
  selectedModel,
  onSelect,
  showSearch = true,
  showDescriptions = true,
  showProviderLogos = true,
  groupByProvider = true,
  searchPlaceholder = "Search models...",
  emptyStateText = "No models found",
  maxHeight = "400px",
  disabled = false,
  className = "",
}: ModelListProps) {
  // SECTION: Local state
  const [searchQuery, setSearchQuery] = useState("")

  // SECTION: Derived data

  /**
   * Filter models based on search query
   */
  const filteredModels = useMemo(() => {
    if (!searchQuery.trim()) return models

    const query = searchQuery.toLowerCase()
    return models.filter(
      (model) =>
        model.name.toLowerCase().includes(query) ||
        model.provider.toLowerCase().includes(query) ||
        (model.description && model.description.toLowerCase().includes(query)) ||
        (model.capabilities &&
          Object.values(model.capabilities).some(
            (cap) => cap && typeof cap === "string" && cap.toLowerCase().includes(query),
          )),
    )
  }, [models, searchQuery])

  /**
   * Group models by provider if needed
   */
  const modelGroups = useMemo(() => {
    if (!groupByProvider) {
      return { "All Models": filteredModels }
    }

    return groupModelsByProvider(filteredModels)
  }, [filteredModels, groupByProvider])

  // SECTION: Render
  return (
    <div className={`model-list ${className}`}>
      {/* Search input */}
      {showSearch && (
        <div className="p-3 border-b border-gray-200 dark:border-gray-700">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400 dark:text-gray-500" />
            <Input
              placeholder={searchPlaceholder}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-9 h-9 text-sm bg-gray-50 dark:bg-gray-800 border-gray-200 dark:border-gray-700 focus:border-primary/30 focus:ring-primary/20"
              disabled={disabled}
            />
          </div>
        </div>
      )}

      {/* Models list */}
      <ScrollArea className={`max-h-[${maxHeight}]`}>
        {Object.keys(modelGroups).length === 0 ? (
          <div className="p-4 text-center text-gray-500 dark:text-gray-400">{emptyStateText}</div>
        ) : (
          <div className="py-2">
            {Object.entries(modelGroups).map(([provider, providerModels]) => (
              <div key={provider} className="mb-2">
                {groupByProvider && (
                  <div className="px-3 py-1 text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                    {provider}
                  </div>
                )}

                <div>
                  {providerModels.map((model) => (
                    <ModelItem
                      key={model.id}
                      model={model}
                      isSelected={selectedModel.id === model.id}
                      showDescription={showDescriptions}
                      showProviderLogo={showProviderLogos}
                      onClick={() => onSelect(model)}
                      disabled={disabled}
                    />
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </ScrollArea>
    </div>
  )
}
