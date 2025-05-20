/**
 * ChatMessage Component
 *
 * Renders a single message in the chat interface, handling different message types
 * and providing appropriate styling and interactions.
 *
 * @ai-pattern message-component
 * Displays user and assistant messages with various interactive features
 */
"use client"

import { useState, createContext, useContext, useCallback, useMemo } from "react"
import type { Message } from "@/types/chat"
import { UserMessage } from "./user-message"
import { AssistantMessage } from "./assistant-message"
import { processMessageContent } from "./utils"
import { MessageActions } from "./message-actions"
import { MessageTimestamp } from "./message-timestamp"
import type { ChatMessageParams } from "./types"
import { cn } from "@/lib/utils"

/**
 * Chat message context type
 */
interface ChatMessageContextType {
  message: Message
  copied: boolean
  setCopied: (copied: boolean) => void
  liked: boolean | null
  setLiked: (liked: boolean | null) => void
  showActions: boolean
  setShowActions: (show: boolean) => void
  copyToClipboard: () => void
  regenerateResponse: () => void
  focusMode: boolean
  enableCopy: boolean
  enableEdit: boolean
  enableDelete: boolean
  enableRegenerate: boolean
  enableFeedback: boolean
  actionsPosition: "hover" | "always" | "below"
  onEdit?: () => void
  onDelete?: () => void
  onRegenerate?: () => void
  onLike?: () => void
  onDislike?: () => void
}

// Create context with undefined default value
const ChatMessageContext = createContext<ChatMessageContextType | undefined>(undefined)

/**
 * Hook to access the chat message context
 * @returns Chat message context
 * @throws {Error} If used outside of a ChatMessageProvider
 */
export function useChatMessage() {
  const context = useContext(ChatMessageContext)
  if (!context) {
    throw new Error("useChatMessage must be used within a ChatMessageProvider")
  }
  return context
}

/**
 * ChatMessage component
 * @param props Component props
 * @returns ChatMessage component
 */
export default function ChatMessage({
  message,
  showTimestamp = true,
  showSender = true,
  isSequential = false,
  isEditing = false,
  focusMode = false,
  timestampFormat = "relative",
  showActions = true,
  actionsPosition = "hover",
  enableSyntaxHighlighting = true,
  enableMarkdown = true,
  enableAutoLink = true,
  enableEmoji = true,
  maxHeight = 0,
  highlight = false,
  highlightColor = "primary",
  showAvatar = true,
  avatarSize = "default",
  enableReactions = false,
  enableThreading = false,
  enableForwarding = false,
  enableTranslation = false,
  enableTextToSpeech = false,
  enableCopy = true,
  enableEdit = false,
  enableDelete = false,
  enableRegenerate = false,
  enableFeedback = false,
  enableSave = false,
  enableShare = false,
  contentRenderer,
  actionsRenderer,
  timestampRenderer,
  senderRenderer,
  avatarRenderer,
  onEdit,
  onDelete,
  onCopy,
  onRegenerate,
  onLike,
  onDislike,
  onSave,
  onShare,
  onTranslate,
  onTextToSpeech,
  onForward,
  onThread,
  onReactionAdd,
  onReactionRemove,
  onClick,
  onHover,
  className = "",
  style,
  id,
  disabled = false,
  dataAttributes,
  animated = true,
  animation = "fade",
  animationDuration = 300,
  animationDelay = 0,
  animationEasing = "ease",
  transition = true,
  transitionDuration = 200,
  transitionProperties = ["all"],
  transitionEasing = "ease",
  showHoverEffect = true,
  hoverColor = "primary",
  hoverEffect = "highlight",
  hideOnMobile = false,
  hideOnTablet = false,
  hideOnDesktop = false,
  responsive = true,
}: ChatMessageParams) {
  // Local state
  const [copied, setCopied] = useState(false)
  const [liked, setLiked] = useState<boolean | null>(null)
  const [showActionsState, setShowActionsState] = useState(false)
  const [isHovered, setIsHovered] = useState(false)

  // Determine if actions should be visible based on hover state and actionsPosition
  const showActionsVisible = useMemo(() => {
    if (!showActions) return false
    if (actionsPosition === "always") return true
    if (actionsPosition === "below") return true
    return isHovered || showActionsState
  }, [showActions, actionsPosition, isHovered, showActionsState])

  /**
   * Copy message content to clipboard
   */
  const copyToClipboard = useCallback(() => {
    if (!enableCopy) return

    navigator.clipboard.writeText(message.content)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)

    onCopy?.()
  }, [message.content, enableCopy, onCopy])

  /**
   * Regenerate assistant response
   */
  const regenerateResponse = useCallback(() => {
    if (!enableRegenerate) return

    onRegenerate?.()
  }, [enableRegenerate, onRegenerate])

  /**
   * Handle like action
   */
  const handleLike = useCallback(() => {
    if (!enableFeedback) return

    setLiked(true)
    onLike?.()
  }, [enableFeedback, onLike])

  /**
   * Handle dislike action
   */
  const handleDislike = useCallback(() => {
    if (!enableFeedback) return

    setLiked(false)
    onDislike?.()
  }, [enableFeedback, onDislike])

  // Create context value
  const contextValue = useMemo(
    () => ({
      message,
      copied,
      setCopied,
      liked,
      setLiked,
      showActions: showActionsState,
      setShowActions: setShowActionsState,
      copyToClipboard,
      regenerateResponse,
      focusMode,
      enableCopy,
      enableEdit,
      enableDelete,
      enableRegenerate,
      enableFeedback,
      actionsPosition,
      onEdit,
      onDelete,
      onRegenerate,
      onLike: handleLike,
      onDislike: handleDislike,
    }),
    [
      message,
      copied,
      liked,
      showActionsState,
      copyToClipboard,
      regenerateResponse,
      focusMode,
      enableCopy,
      enableEdit,
      enableDelete,
      enableRegenerate,
      enableFeedback,
      actionsPosition,
      onEdit,
      onDelete,
      onRegenerate,
      handleLike,
      handleDislike,
    ],
  )

  // Process the message content
  const processedContent = useMemo(() => {
    if (contentRenderer) {
      return contentRenderer(message.content)
    }
    return processMessageContent(message.content, {
      enableSyntaxHighlighting,
      enableMarkdown,
      enableAutoLink,
      enableEmoji,
    })
  }, [message.content, contentRenderer, enableSyntaxHighlighting, enableMarkdown, enableAutoLink, enableEmoji])

  // Prepare animation and transition styles
  const animationStyle = useMemo(() => {
    if (!animated) return {}

    return {
      animation: `${animation} ${animationDuration}ms ${animationEasing} ${animationDelay}ms`,
    }
  }, [animated, animation, animationDuration, animationEasing, animationDelay])

  const transitionStyle = useMemo(() => {
    if (!transition) return {}

    return {
      transition: `${transitionProperties.join(", ")} ${transitionDuration}ms ${transitionEasing}`,
    }
  }, [transition, transitionProperties, transitionDuration, transitionEasing])

  // Combine all styles
  const combinedStyle = useMemo(
    () => ({
      ...style,
      ...animationStyle,
      ...transitionStyle,
    }),
    [style, animationStyle, transitionStyle],
  )

  // Prepare responsive classes
  const responsiveClasses = useMemo(() => {
    if (!responsive) return ""

    return cn(hideOnMobile && "hidden sm:flex", hideOnTablet && "hidden md:flex", hideOnDesktop && "flex md:hidden")
  }, [responsive, hideOnMobile, hideOnTablet, hideOnDesktop])

  // Prepare hover effect classes
  const hoverClasses = useMemo(() => {
    if (!showHoverEffect) return ""

    return cn(
      hoverEffect === "highlight" && `hover:bg-${hoverColor}-50 dark:hover:bg-${hoverColor}-900/20`,
      hoverEffect === "glow" && `hover:shadow-${hoverColor}`,
      hoverEffect === "scale" && "hover:scale-[1.01]",
    )
  }, [showHoverEffect, hoverEffect, hoverColor])

  // Prepare highlight classes
  const highlightClasses = useMemo(() => {
    if (!highlight) return ""

    return cn(`bg-${highlightColor}-50 dark:bg-${highlightColor}-900/20 border-l-2 border-${highlightColor}-500`)
  }, [highlight, highlightColor])

  // Combine all classes
  const allClasses = useMemo(
    () =>
      cn(
        `message flex ${message.role === "user" ? "justify-end" : "justify-start"} mb-4`,
        focusMode && "message-actions-below",
        responsiveClasses,
        hoverClasses,
        highlightClasses,
        className,
      ),
    [message.role, focusMode, responsiveClasses, hoverClasses, highlightClasses, className],
  )

  // Prepare data attributes
  const allDataAttributes = useMemo(
    () => ({
      "data-message-id": message.id,
      "data-message-role": message.role,
      "data-message-sequential": isSequential ? "true" : "false",
      "data-message-editing": isEditing ? "true" : "false",
      "data-message-focus-mode": focusMode ? "true" : "false",
      "data-component": "ChatMessage",
      "data-component-path": "@/components/chat/chat-message",
      ...(dataAttributes || {}),
    }),
    [message.id, message.role, isSequential, isEditing, focusMode, dataAttributes],
  )

  /**
   * Handle mouse enter event
   */
  const handleMouseEnter = useCallback(() => {
    setIsHovered(true)
    onHover?.(true)
  }, [onHover])

  /**
   * Handle mouse leave event
   */
  const handleMouseLeave = useCallback(() => {
    setIsHovered(false)
    onHover?.(false)
  }, [onHover])

  return (
    <ChatMessageContext.Provider value={contextValue}>
      <div
        className={allClasses}
        style={combinedStyle}
        id={id}
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
        onClick={onClick}
        {...allDataAttributes}
      >
        <div className={`flex flex-col ${message.role === "user" ? "items-end" : "items-start"}`}>
          {message.role === "user" ? (
            <UserMessage
              content={processedContent}
              showSender={showSender}
              isSequential={isSequential}
              isEditing={isEditing}
              showTimestamp={showTimestamp}
              timestampFormat={timestampFormat}
              showAvatar={showAvatar}
              avatarSize={avatarSize}
              contentRenderer={contentRenderer}
              timestampRenderer={timestampRenderer}
              senderRenderer={senderRenderer}
              avatarRenderer={avatarRenderer}
              disabled={disabled}
            />
          ) : (
            <AssistantMessage
              content={processedContent}
              showSender={showSender}
              isSequential={isSequential}
              showTimestamp={showTimestamp}
              timestampFormat={timestampFormat}
              showAvatar={showAvatar}
              avatarSize={avatarSize}
              enableSyntaxHighlighting={enableSyntaxHighlighting}
              enableMarkdown={enableMarkdown}
              enableAutoLink={enableAutoLink}
              enableEmoji={enableEmoji}
              contentRenderer={contentRenderer}
              timestampRenderer={timestampRenderer}
              senderRenderer={senderRenderer}
              avatarRenderer={avatarRenderer}
              disabled={disabled}
            />
          )}

          {showTimestamp && timestampRenderer
            ? timestampRenderer(message.timestamp)
            : showTimestamp && (
                <MessageTimestamp timestamp={message.timestamp} format={timestampFormat} isMobile={true} />
              )}

          {/* Message actions */}
          {showActions && (
            <div className={`message-actions-container ${actionsPosition === "below" || focusMode ? "mt-2" : "mt-0"}`}>
              {actionsRenderer ? (
                actionsRenderer(message)
              ) : (
                <MessageActions
                  visible={showActionsVisible}
                  position={actionsPosition}
                  enableCopy={enableCopy}
                  enableEdit={enableEdit}
                  enableDelete={enableDelete}
                  enableRegenerate={enableRegenerate && message.role === "assistant"}
                  enableFeedback={enableFeedback && message.role === "assistant"}
                  enableSave={enableSave}
                  enableShare={enableShare}
                  enableTranslation={enableTranslation}
                  enableTextToSpeech={enableTextToSpeech}
                  enableForwarding={enableForwarding}
                  enableThreading={enableThreading}
                  onEdit={onEdit}
                  onDelete={onDelete}
                  onCopy={copyToClipboard}
                  onRegenerate={regenerateResponse}
                  onLike={handleLike}
                  onDislike={handleDislike}
                  onSave={onSave}
                  onShare={onShare}
                  onTranslate={onTranslate}
                  onTextToSpeech={onTextToSpeech}
                  onForward={onForward}
                  onThread={onThread}
                />
              )}
            </div>
          )}
        </div>
      </div>
    </ChatMessageContext.Provider>
  )
}
