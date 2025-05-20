"use client"

import { Avatar } from "@/components/ui/avatar"
import type { ReactNode } from "react"
import { useChatMessage } from "."
import { MessageActions } from "./message-actions"

interface AssistantMessageProps {
  content: ReactNode
}

export function AssistantMessage({ content }: AssistantMessageProps) {
  const { message, showActions, setShowActions } = useChatMessage()

  return (
    <div
      className="flex my-4 group"
      onMouseEnter={() => setShowActions(true)}
      onMouseLeave={() => setShowActions(false)}
      data-component="ChatMessage"
      data-component-path="@/components/chat/chat-message"
    >
      <Avatar className="h-8 w-8 mr-3 bg-gradient-to-br from-primary to-purple-500 shadow-sm">
        <span>AI</span>
      </Avatar>
      <div className="flex-1">
        <div className="flex items-center mb-1">
          <span className="font-medium text-sm text-gray-700 dark:text-gray-300">Tess AI v5</span>
          {message.model && (
            <span className="ml-2 text-xs bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 px-2 py-0.5 rounded-full transition-colors duration-200">
              {message.model}
            </span>
          )}
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-2xl p-4 text-gray-800 dark:text-gray-200 shadow-sm border border-gray-100 dark:border-gray-700 transition-colors duration-200">
          {content}
        </div>

        <MessageActions visible={showActions} />
      </div>
    </div>
  )
}
