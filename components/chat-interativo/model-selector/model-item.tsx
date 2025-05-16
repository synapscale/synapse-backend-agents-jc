/**
 * ModelItem Component
 *
 * Displays a single AI model in the model list with its details.
 * Used by the ModelList component.
 */
"use client"
import Image from "next/image"
import { Check, Zap, MessageSquare, ImageIcon, FileText, Lock } from "lucide-react"
import type { AIModel } from "@/types/chat"

/**
 * Props for the ModelItem component
 */
export interface ModelItemProps {
  /**
   * The model to display
   */
  model: AIModel

  /**
   * Whether this model is currently selected
   * @default false
   */
  isSelected?: boolean

  /**
   * Whether to show the model description
   * @default true
   */
  showDescription?: boolean

  /**
   * Whether to show the provider logo
   * @default true
   */
  showProviderLogo?: boolean

  /**
   * Whether to show model capabilities
   * @default true
   */
  showCapabilities?: boolean

  /**
   * Whether to show the model's token limit
   * @default true
   */
  showTokenLimit?: boolean

  /**
   * Whether the component is disabled
   * @default false
   */
  disabled?: boolean

  /**
   * CSS class name for the component
   */
  className?: string

  /**
   * Click handler
   */
  onClick?: () => void
}

/**
 * Get the provider logo URL
 * @param provider Provider name
 * @returns URL to the provider logo
 */
function getProviderLogoUrl(provider: string): string {
  const providerLogos: Record<string, string> = {
    OpenAI: "/google-g-logo.png",
    Anthropic: "/anthropic-logo.png",
    Google: "/google-g-logo.png",
    DeepSeek: "/deepseek-logo-inspired.png",
    Mistral: "/placeholder-ct6n6.png",
    Meta: "/placeholder-akjv1.png",
    Cohere: "/abstract-infinity-logo.png",
  }

  return providerLogos[provider] || "/abstract-ai-network.png"
}

/**
 * ModelItem component
 */
export function ModelItem({
  model,
  isSelected = false,
  showDescription = true,
  showProviderLogo = true,
  showCapabilities = true,
  showTokenLimit = true,
  disabled = false,
  className = "",
  onClick,
}: ModelItemProps) {
  // SECTION: Render helpers

  /**
   * Get capability icons based on model capabilities
   */
  const getCapabilityIcons = () => {
    const icons = []

    if (model.capabilities?.text) {
      icons.push(
        <div key="text" className="flex items-center" title="Text generation">
          <MessageSquare className="h-3 w-3 text-gray-400" />
        </div>,
      )
    }

    if (model.capabilities?.vision) {
      icons.push(
        <div key="vision" className="flex items-center" title="Vision capabilities">
          <ImageIcon className="h-3 w-3 text-gray-400" />
        </div>,
      )
    }

    if (model.capabilities?.files) {
      icons.push(
        <div key="files" className="flex items-center" title="File processing">
          <FileText className="h-3 w-3 text-gray-400" />
        </div>,
      )
    }

    if (model.capabilities?.fast) {
      icons.push(
        <div key="fast" className="flex items-center" title="Fast response time">
          <Zap className="h-3 w-3 text-gray-400" />
        </div>,
      )
    }

    return icons
  }

  // SECTION: Render
  return (
    <button
      className={`w-full px-3 py-2 text-left hover:bg-gray-50 dark:hover:bg-gray-800 flex items-center justify-between transition-colors duration-200 ${
        isSelected ? "bg-primary/5 dark:bg-primary/10" : ""
      } ${disabled ? "opacity-50 cursor-not-allowed" : "cursor-pointer"} ${className}`}
      onClick={onClick}
      disabled={disabled}
    >
      <div className="flex items-center">
        {/* Provider logo */}
        {showProviderLogo && (
          <div className="w-8 h-8 rounded-full overflow-hidden mr-3 bg-gray-100 dark:bg-gray-700 flex items-center justify-center">
            <Image
              src={getProviderLogoUrl(model.provider) || "/placeholder.svg"}
              alt={model.provider}
              width={32}
              height={32}
              className="object-cover"
            />
          </div>
        )}

        {/* Model info */}
        <div>
          <div className="flex items-center">
            <span className="font-medium text-gray-800 dark:text-gray-200">{model.name}</span>
            {model.isPaid && <Lock className="h-3 w-3 ml-1 text-gray-400" title="Paid model" />}
          </div>

          {showDescription && model.description && (
            <div className="text-xs text-gray-500 dark:text-gray-400 mt-0.5 max-w-[200px] truncate">
              {model.description}
            </div>
          )}

          {/* Capabilities and token limit */}
          <div className="flex items-center mt-1 space-x-2">
            {showCapabilities && <div className="flex items-center space-x-1">{getCapabilityIcons()}</div>}

            {showTokenLimit && model.contextLength && (
              <div className="text-xs text-gray-500 dark:text-gray-400">
                {model.contextLength.toLocaleString()} tokens
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Selection indicator */}
      {isSelected && (
        <div className="flex-shrink-0 ml-2">
          <Check className="h-4 w-4 text-primary" />
        </div>
      )}
    </button>
  )
}
