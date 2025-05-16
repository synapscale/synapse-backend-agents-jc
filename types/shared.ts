import type { ReactNode } from "react"
import type { Message, Conversation, AIModel } from "./chat"

// Common prop types
export interface BaseProps {
  className?: string
  children?: ReactNode
}

// Button variants for consistent styling
export type ButtonVariant = "default" | "primary" | "secondary" | "ghost" | "link" | "outline" | "destructive"

// Common component props with consistent naming
export interface WithTooltipProps {
  tooltip?: string
  tooltipSide?: "top" | "right" | "bottom" | "left"
  tooltipAlign?: "start" | "center" | "end"
}

// Props for components that can be disabled
export interface DisableableProps {
  disabled?: boolean
}

// Props for components that handle loading states
export interface LoadingProps {
  isLoading?: boolean
}

// Props for components with icons
export interface WithIconProps {
  icon?: ReactNode
  iconPosition?: "left" | "right"
}

// Message-related props
export interface MessageComponentProps {
  message: Message
  showTimestamp?: boolean
  showSender?: boolean
  isSequential?: boolean
  focusMode?: boolean
}

// Conversation-related props
export interface ConversationComponentProps {
  conversation: Conversation
  isActive?: boolean
}

// Model-related props
export interface ModelComponentProps {
  model: AIModel
  isSelected?: boolean
}

// Common event handler types
export type MessageActionHandler = (messageId: string) => void
export type ConversationActionHandler = (conversationId: string) => void
export type ModelSelectionHandler = (model: AIModel) => void
