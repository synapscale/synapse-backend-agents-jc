import type React from "react"
import type { Message } from "@/types/chat"
import type {
  BaseComponentParams,
  AnimationParams,
  TransitionParams,
  HoverStateParams,
  ResponsiveParams,
} from "@/types/component-params"

/**
 * Parameters for the ChatMessage component
 */
export interface ChatMessageParams
  extends BaseComponentParams<HTMLDivElement>,
    AnimationParams,
    TransitionParams,
    HoverStateParams,
    ResponsiveParams {
  /**
   * The message object to display
   */
  message: Message

  /**
   * Whether to show the timestamp on the message
   * @default true
   */
  showTimestamp?: boolean

  /**
   * Whether to show the sender's name on the message
   * @default true
   */
  showSender?: boolean

  /**
   * Whether the message is part of a sequence of messages from the same sender
   * @default false
   */
  isSequential?: boolean

  /**
   * Whether the message is being edited
   * @default false
   */
  isEditing?: boolean

  /**
   * Whether the message should be displayed in focus mode
   * @default false
   */
  focusMode?: boolean

  /**
   * Format for displaying the timestamp
   * @default "relative"
   */
  timestampFormat?: "relative" | "absolute" | "time" | "date" | "datetime"

  /**
   * Whether to show the message actions
   * @default true
   */
  showActions?: boolean

  /**
   * Position of the message actions
   * @default "hover"
   */
  actionsPosition?: "hover" | "always" | "below"

  /**
   * Whether to enable syntax highlighting for code blocks in the message
   * @default true
   */
  enableSyntaxHighlighting?: boolean

  /**
   * Whether to enable markdown rendering for the message
   * @default true
   */
  enableMarkdown?: boolean

  /**
   * Whether to enable auto-linking of URLs in the message
   * @default true
   */
  enableAutoLink?: boolean

  /**
   * Whether to enable emoji rendering in the message
   * @default true
   */
  enableEmoji?: boolean

  /**
   * Maximum height of the message in pixels
   * If the message exceeds this height, it will be truncated with a "Show more" button
   * @default 0 (no limit)
   */
  maxHeight?: number

  /**
   * Whether to highlight the message
   * @default false
   */
  highlight?: boolean

  /**
   * Color scheme for the highlight
   * @default "primary"
   */
  highlightColor?: "primary" | "secondary" | "success" | "warning" | "danger" | "info" | "neutral"

  /**
   * Whether to show the message avatar
   * @default true
   */
  showAvatar?: boolean

  /**
   * Size of the avatar
   * @default "default"
   */
  avatarSize?: "sm" | "default" | "lg"

  /**
   * Whether to enable reactions for the message
   * @default false
   */
  enableReactions?: boolean

  /**
   * Whether to enable threading for the message
   * @default false
   */
  enableThreading?: boolean

  /**
   * Whether to enable forwarding for the message
   * @default false
   */
  enableForwarding?: boolean

  /**
   * Whether to enable translation for the message
   * @default false
   */
  enableTranslation?: boolean

  /**
   * Whether to enable text-to-speech for the message
   * @default false
   */
  enableTextToSpeech?: boolean

  /**
   * Whether to enable copying the message
   * @default true
   */
  enableCopy?: boolean

  /**
   * Whether to enable editing the message
   * @default false
   */
  enableEdit?: boolean

  /**
   * Whether to enable deleting the message
   * @default false
   */
  enableDelete?: boolean

  /**
   * Whether to enable regenerating the message (for AI-generated messages)
   * @default false
   */
  enableRegenerate?: boolean

  /**
   * Whether to enable liking/disliking the message
   * @default false
   */
  enableFeedback?: boolean

  /**
   * Whether to enable saving the message
   * @default false
   */
  enableSave?: boolean

  /**
   * Whether to enable sharing the message
   * @default false
   */
  enableShare?: boolean

  /**
   * Custom renderer for the message content
   * If provided, the default message content renderer will be ignored
   */
  contentRenderer?: (content: string) => React.ReactNode

  /**
   * Custom renderer for the message actions
   * If provided, the default message actions renderer will be ignored
   */
  actionsRenderer?: (message: Message) => React.ReactNode

  /**
   * Custom renderer for the message timestamp
   * If provided, the default message timestamp renderer will be ignored
   */
  timestampRenderer?: (timestamp: number) => React.ReactNode

  /**
   * Custom renderer for the message sender
   * If provided, the default message sender renderer will be ignored
   */
  senderRenderer?: (sender: string) => React.ReactNode

  /**
   * Custom renderer for the message avatar
   * If provided, the default message avatar renderer will be ignored
   */
  avatarRenderer?: (sender: string) => React.ReactNode

  /**
   * Callback fired when the edit button is clicked
   */
  onEdit?: () => void

  /**
   * Callback fired when the delete button is clicked
   */
  onDelete?: () => void

  /**
   * Callback fired when the copy button is clicked
   */
  onCopy?: () => void

  /**
   * Callback fired when the regenerate button is clicked
   */
  onRegenerate?: () => void

  /**
   * Callback fired when the like button is clicked
   */
  onLike?: () => void

  /**
   * Callback fired when the dislike button is clicked
   */
  onDislike?: () => void

  /**
   * Callback fired when the save button is clicked
   */
  onSave?: () => void

  /**
   * Callback fired when the share button is clicked
   */
  onShare?: () => void

  /**
   * Callback fired when the translate button is clicked
   */
  onTranslate?: () => void

  /**
   * Callback fired when the text-to-speech button is clicked
   */
  onTextToSpeech?: () => void

  /**
   * Callback fired when the forward button is clicked
   */
  onForward?: () => void

  /**
   * Callback fired when the thread button is clicked
   */
  onThread?: () => void

  /**
   * Callback fired when a reaction is added
   */
  onReactionAdd?: (reaction: string) => void

  /**
   * Callback fired when a reaction is removed
   */
  onReactionRemove?: (reaction: string) => void

  /**
   * Callback fired when the message is clicked
   */
  onClick?: (event: React.MouseEvent<HTMLDivElement>) => void

  /**
   * Callback fired when the message is hovered
   */
  onHover?: (isHovered: boolean) => void
}

/**
 * Parameters for the MessageContent component
 */
export interface MessageContentParams extends BaseComponentParams<HTMLDivElement> {
  /**
   * The content of the message
   */
  content: string

  /**
   * Whether to enable syntax highlighting for code blocks in the message
   * @default true
   */
  enableSyntaxHighlighting?: boolean

  /**
   * Whether to enable markdown rendering for the message
   * @default true
   */
  enableMarkdown?: boolean

  /**
   * Whether to enable auto-linking of URLs in the message
   * @default true
   */
  enableAutoLink?: boolean

  /**
   * Whether to enable emoji rendering in the message
   * @default true
   */
  enableEmoji?: boolean

  /**
   * Maximum height of the message in pixels
   * If the message exceeds this height, it will be truncated with a "Show more" button
   * @default 0 (no limit)
   */
  maxHeight?: number

  /**
   * Custom renderer for the message content
   * If provided, the default message content renderer will be ignored
   */
  contentRenderer?: (content: string) => React.ReactNode
}

/**
 * Parameters for the MessageActions component
 */
export interface MessageActionsParams extends BaseComponentParams<HTMLDivElement> {
  /**
   * Whether the actions should be visible
   * @default false
   */
  visible?: boolean

  /**
   * Position of the actions
   * @default "hover"
   */
  position?: "hover" | "always" | "below"

  /**
   * Whether to enable copying the message
   * @default true
   */
  enableCopy?: boolean

  /**
   * Whether to enable editing the message
   * @default false
   */
  enableEdit?: boolean

  /**
   * Whether to enable deleting the message
   * @default false
   */
  enableDelete?: boolean

  /**
   * Whether to enable regenerating the message (for AI-generated messages)
   * @default false
   */
  enableRegenerate?: boolean

  /**
   * Whether to enable liking/disliking the message
   * @default false
   */
  enableFeedback?: boolean

  /**
   * Whether to enable saving the message
   * @default false
   */
  enableSave?: boolean

  /**
   * Whether to enable sharing the message
   * @default false
   */
  enableShare?: boolean

  /**
   * Whether to enable translation for the message
   * @default false
   */
  enableTranslation?: boolean

  /**
   * Whether to enable text-to-speech for the message
   * @default false
   */
  enableTextToSpeech?: boolean

  /**
   * Whether to enable forwarding for the message
   * @default false
   */
  enableForwarding?: boolean

  /**
   * Whether to enable threading for the message
   * @default false
   */
  enableThreading?: boolean

  /**
   * Custom renderer for the message actions
   * If provided, the default message actions renderer will be ignored
   */
  actionsRenderer?: (message: Message) => React.ReactNode

  /**
   * Callback fired when the edit button is clicked
   */
  onEdit?: () => void

  /**
   * Callback fired when the delete button is clicked
   */
  onDelete?: () => void

  /**
   * Callback fired when the copy button is clicked
   */
  onCopy?: () => void

  /**
   * Callback fired when the regenerate button is clicked
   */
  onRegenerate?: () => void

  /**
   * Callback fired when the like button is clicked
   */
  onLike?: () => void

  /**
   * Callback fired when the dislike button is clicked
   */
  onDislike?: () => void

  /**
   * Callback fired when the save button is clicked
   */
  onSave?: () => void

  /**
   * Callback fired when the share button is clicked
   */
  onShare?: () => void

  /**
   * Callback fired when the translate button is clicked
   */
  onTranslate?: () => void

  /**
   * Callback fired when the text-to-speech button is clicked
   */
  onTextToSpeech?: () => void

  /**
   * Callback fired when the forward button is clicked
   */
  onForward?: () => void

  /**
   * Callback fired when the thread button is clicked
   */
  onThread?: () => void
}

/**
 * Parameters for the MessageTimestamp component
 */
export interface MessageTimestampParams extends BaseComponentParams<HTMLDivElement> {
  /**
   * The timestamp to display
   */
  timestamp: number

  /**
   * Format for displaying the timestamp
   * @default "relative"
   */
  format?: "relative" | "absolute" | "time" | "date" | "datetime"

  /**
   * Whether the timestamp is for mobile display
   * @default false
   */
  isMobile?: boolean

  /**
   * Custom renderer for the timestamp
   * If provided, the default timestamp renderer will be ignored
   */
  renderer?: (timestamp: number) => React.ReactNode
}

/**
 * Parameters for the UserMessage component
 */
export interface UserMessageParams extends BaseComponentParams<HTMLDivElement> {
  /**
   * The content of the message
   */
  content: string

  /**
   * Whether to show the sender's name
   * @default true
   */
  showSender?: boolean

  /**
   * Whether the message is part of a sequence
   * @default false
   */
  isSequential?: boolean

  /**
   * Whether the message is being edited
   * @default false
   */
  isEditing?: boolean

  /**
   * Whether to show the timestamp
   * @default true
   */
  showTimestamp?: boolean

  /**
   * Format for displaying the timestamp
   * @default "relative"
   */
  timestampFormat?: "relative" | "absolute" | "time" | "date" | "datetime"

  /**
   * Whether to show the avatar
   * @default true
   */
  showAvatar?: boolean

  /**
   * Size of the avatar
   * @default "default"
   */
  avatarSize?: "sm" | "default" | "lg"

  /**
   * Custom renderer for the message content
   * If provided, the default message content renderer will be ignored
   */
  contentRenderer?: (content: string) => React.ReactNode

  /**
   * Custom renderer for the timestamp
   * If provided, the default timestamp renderer will be ignored
   */
  timestampRenderer?: (timestamp: number) => React.ReactNode

  /**
   * Custom renderer for the sender
   * If provided, the default sender renderer will be ignored
   */
  senderRenderer?: (sender: string) => React.ReactNode

  /**
   * Custom renderer for the avatar
   * If provided, the default avatar renderer will be ignored
   */
  avatarRenderer?: (sender: string) => React.ReactNode
}

/**
 * Parameters for the AssistantMessage component
 */
export interface AssistantMessageParams extends BaseComponentParams<HTMLDivElement> {
  /**
   * The content of the message
   */
  content: string

  /**
   * Whether to show the sender's name
   * @default true
   */
  showSender?: boolean

  /**
   * Whether the message is part of a sequence
   * @default false
   */
  isSequential?: boolean

  /**
   * Whether to show the timestamp
   * @default true
   */
  showTimestamp?: boolean

  /**
   * Format for displaying the timestamp
   * @default "relative"
   */
  timestampFormat?: "relative" | "absolute" | "time" | "date" | "datetime"

  /**
   * Whether to show the avatar
   * @default true
   */
  showAvatar?: boolean

  /**
   * Size of the avatar
   * @default "default"
   */
  avatarSize?: "sm" | "default" | "lg"

  /**
   * Whether to enable syntax highlighting for code blocks
   * @default true
   */
  enableSyntaxHighlighting?: boolean

  /**
   * Whether to enable markdown rendering
   * @default true
   */
  enableMarkdown?: boolean

  /**
   * Whether to enable auto-linking of URLs
   * @default true
   */
  enableAutoLink?: boolean

  /**
   * Whether to enable emoji rendering
   * @default true
   */
  enableEmoji?: boolean

  /**
   * Custom renderer for the message content
   * If provided, the default message content renderer will be ignored
   */
  contentRenderer?: (content: string) => React.ReactNode

  /**
   * Custom renderer for the timestamp
   * If provided, the default timestamp renderer will be ignored
   */
  timestampRenderer?: (timestamp: number) => React.ReactNode

  /**
   * Custom renderer for the sender
   * If provided, the default sender renderer will be ignored
   */
  senderRenderer?: (sender: string) => React.ReactNode

  /**
   * Custom renderer for the avatar
   * If provided, the default avatar renderer will be ignored
   */
  avatarRenderer?: (sender: string) => React.ReactNode
}
