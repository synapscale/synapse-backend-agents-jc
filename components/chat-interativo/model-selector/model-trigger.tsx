/**
 * ModelTrigger Component
 *
 * The button that triggers the model selector dropdown.
 * Displays the currently selected model with its logo.
 */
"use client"
import Image from "next/image"
import { ChevronDown } from "lucide-react"
import { Button } from "@/components/ui/button"
import type { AIModel } from "@/types/chat"

/**
 * Props for the ModelTrigger component
 */
export interface ModelTriggerProps {
  /**
   * The currently selected model
   */
  model: AIModel

  /**
   * Whether to show the provider logo
   * @default true
   */
  showLogo?: boolean

  /**
   * Size of the trigger button
   * @default "default"
   */
  size?: "sm" | "default" | "lg"

  /**
   * Whether to show the model provider name
   * @default false
   */
  showProvider?: boolean

  /**
   * Whether to show the chevron icon
   * @default true
   */
  showChevron?: boolean

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
 * ModelTrigger component
 */
export function ModelTrigger({
  model,
  showLogo = true,
  size = "default",
  showProvider = false,
  showChevron = true,
  disabled = false,
  className = "",
}: ModelTriggerProps) {
  // SECTION: Size mappings
  const sizeClasses = {
    sm: "h-8 text-xs",
    default: "h-10 text-sm",
    lg: "h-12 text-base",
  }

  const logoSizes = {
    sm: 16,
    default: 20,
    lg: 24,
  }

  // SECTION: Render
  return (
    <Button
      variant="outline"
      className={`flex items-center gap-2 bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700 ${
        sizeClasses[size]
      } ${className}`}
      disabled={disabled}
    >
      {showLogo && (
        <div className="rounded-full overflow-hidden bg-gray-100 dark:bg-gray-700 flex-shrink-0">
          <Image
            src={getProviderLogoUrl(model.provider) || "/placeholder.svg"}
            alt={model.provider}
            width={logoSizes[size]}
            height={logoSizes[size]}
            className="object-cover"
          />
        </div>
      )}

      <span className="truncate max-w-[120px]">
        {model.name}
        {showProvider && <span className="text-gray-500 dark:text-gray-400 ml-1">({model.provider})</span>}
      </span>

      {showChevron && <ChevronDown className={size === "sm" ? "h-3 w-3" : "h-4 w-4"} />}
    </Button>
  )
}
