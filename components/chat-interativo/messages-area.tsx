"use client"

import type React from "react"

import type { RefObject } from "react"
import { Sparkles } from "lucide-react"
import ChatMessage from "./chat-message"
import type { Message } from "@/types/chat"

interface MessagesAreaProps {
  messages: Message[]
  isLoading: boolean
  showTimestamps?: boolean
  showSenders?: boolean
  focusMode?: boolean
  theme: string
  chatBackground?: string | React.ReactNode
  messagesEndRef: RefObject<HTMLDivElement>
}

export function MessagesArea({
  messages,
  isLoading,
  showTimestamps = true,
  showSenders = true,
  focusMode = false,
  theme,
  chatBackground,
  messagesEndRef,
}: MessagesAreaProps) {
  return (
    <div
      className="flex-1 overflow-y-auto p-4 scrollbar-thin"
      style={{
        backgroundImage: chatBackground
          ? typeof chatBackground === "string"
            ? chatBackground
            : undefined
          : theme === "light"
            ? "radial-gradient(circle at center, rgba(243, 244, 246, 0.6) 0%, rgba(249, 250, 251, 0.3) 100%)"
            : "radial-gradient(circle at center, rgba(31, 41, 55, 0.6) 0%, rgba(17, 24, 39, 0.3) 100%)",
        backgroundSize: "cover",
      }}
    >
      <div className="max-w-3xl mx-auto">
        {/* Render messages */}
        {messages.map((message) => (
          <ChatMessage
            key={message.id}
            message={message}
            showTimestamp={showTimestamps}
            showSender={showSenders}
            focusMode={focusMode}
          />
        ))}

        {/* Loading indicator */}
        {isLoading && (
          <div className="flex items-center mt-4 text-gray-500 animate-pulse">
            <div className="ml-12 bg-white dark:bg-gray-800 bg-opacity-70 dark:bg-opacity-70 backdrop-blur-sm rounded-lg p-3 shadow-sm border border-gray-100 dark:border-gray-700 transition-colors duration-200">
              <div className="flex items-center space-x-2">
                <Sparkles className="h-4 w-4 text-primary" />
                <span className="dark:text-gray-300">Generating response...</span>
              </div>
            </div>
          </div>
        )}

        {/* Anchor for auto-scrolling */}
        <div ref={messagesEndRef} />
      </div>
    </div>
  )
}
