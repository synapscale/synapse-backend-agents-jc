/**
 * ChatHeader Component
 *
 * Displays the header of the chat interface with conversation title and actions.
 *
 * @ai-pattern header-component
 * Header component with action buttons and conversation title
 */
"use client"

import { useMemo } from "react"
import { IconButton } from "@/components/ui/icon-button"
import { Menu, PlusCircle, Layers, Eye, EyeOff } from "lucide-react"
import { useApp } from "@/contexts/app-context"
import type { Conversation } from "@/types/chat"
import ConversationHeader from "./conversation-header"

/**
 * Props for the ChatHeader component
 */
interface ChatHeaderProps {
  /**
   * Current conversation data
   */
  currentConversation: Conversation | undefined

  /**
   * Current conversation ID
   */
  currentConversationId: string | null

  /**
   * Callback to create a new conversation
   */
  onNewConversation: () => void

  /**
   * Callback to update conversation title
   */
  onUpdateConversationTitle: (title: string) => void

  /**
   * Callback to delete a conversation
   */
  onDeleteConversation: (id: string) => void

  /**
   * Callback to export a conversation
   */
  onExportConversation: () => void

  /**
   * Callback to toggle the sidebar
   */
  onToggleSidebar: () => void

  /**
   * Callback to toggle the component selector
   */
  onToggleComponentSelector?: () => void

  /**
   * Callback to toggle focus mode
   */
  onToggleFocusMode?: () => void
}

/**
 * ChatHeader component
 * @param props Component props
 * @returns ChatHeader component
 */
export function ChatHeader({
  currentConversation,
  currentConversationId,
  onNewConversation,
  onUpdateConversationTitle,
  onDeleteConversation,
  onExportConversation,
  onToggleSidebar,
  onToggleComponentSelector,
  onToggleFocusMode,
}: ChatHeaderProps) {
  const { showConfig, setShowConfig, isComponentSelectorActive, focusMode, setFocusMode } = useApp()

  /**
   * Handle focus mode toggle
   */
  const handleToggleFocusMode = () => {
    if (onToggleFocusMode) {
      onToggleFocusMode()
    } else if (setFocusMode) {
      setFocusMode(!focusMode)
    }
  }

  /**
   * Conversation title display
   */
  const conversationTitleDisplay = useMemo(() => {
    if (!currentConversation) return null

    return (
      <div className="flex items-center">
        <div className="w-2 h-2 bg-green-400 rounded-full mr-2"></div>
        <h2 className="font-medium text-sm truncate ml-1 text-gray-700 dark:text-gray-200">
          {currentConversation.title}
        </h2>
      </div>
    )
  }, [currentConversation])

  return (
    <div
      className="bg-white dark:bg-gray-800 border-b border-gray-100 dark:border-gray-700 shadow-sm flex items-center justify-between p-3 sticky top-0 z-10 transition-colors duration-200"
      data-component="ChatHeader"
      data-component-path="@/components/chat/chat-header"
    >
      <div className="flex items-center">
        {/* Mobile menu button */}
        <IconButton
          icon={<Menu className="h-5 w-5 text-gray-600 dark:text-gray-300" />}
          className="md:hidden mr-2"
          onClick={onToggleSidebar}
          aria-label="Toggle sidebar"
        />

        {/* Mobile new conversation button */}
        <IconButton
          icon={<PlusCircle className="h-5 w-5 text-gray-600 dark:text-gray-300" />}
          tooltip="Nova conversa"
          className="md:hidden"
          onClick={onNewConversation}
          aria-label="New conversation"
        />

        {/* Conversation title */}
        {conversationTitleDisplay}
      </div>

      {/* Header actions */}
      <div className="flex items-center space-x-2">
        {/* Focus mode toggle */}
        <IconButton
          icon={
            focusMode ? (
              <EyeOff className="h-5 w-5 text-gray-600 dark:text-gray-300" />
            ) : (
              <Eye className="h-5 w-5 text-gray-600 dark:text-gray-300" />
            )
          }
          tooltip={focusMode ? "Exit Focus Mode" : "Enter Focus Mode"}
          className={focusMode ? "bg-primary/10 text-primary" : ""}
          onClick={handleToggleFocusMode}
          aria-label={focusMode ? "Exit focus mode" : "Enter focus mode"}
          aria-pressed={focusMode}
        />

        {/* Component selector toggle */}
        {onToggleComponentSelector && (
          <IconButton
            icon={<Layers className="h-5 w-5 text-gray-600 dark:text-gray-300" />}
            tooltip="Seletor de Componentes"
            className={isComponentSelectorActive ? "bg-primary/10 text-primary" : ""}
            onClick={onToggleComponentSelector}
            aria-label="Toggle component selector"
            aria-pressed={isComponentSelectorActive}
          />
        )}

        {/* Conversation header actions */}
        {currentConversation && (
          <ConversationHeader
            conversation={currentConversation}
            onUpdateTitle={onUpdateConversationTitle}
            onDeleteConversation={() => currentConversationId && onDeleteConversation(currentConversationId)}
            onExportConversation={onExportConversation}
          />
        )}
      </div>
    </div>
  )
}
