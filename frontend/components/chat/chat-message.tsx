/**
 * ChatMessage
 * 
 * Componente que renderiza uma mensagem individual no chat,
 * com suporte para diferentes tipos de mensagens (usuário, assistente)
 * e ações contextuais.
 */
"use client"

import { useMemo } from "react"
import { Message } from "@/types/chat"
import UserMessage from "./chat-message/user-message"
import AssistantMessage from "./chat-message/assistant-message"
import MessageActions from "./chat-message/message-actions"
import MessageTimestamp from "./chat-message/message-timestamp"

interface ChatMessageProps {
  message: Message
  showTimestamp?: boolean
  showSender?: boolean
  isLastMessage?: boolean
}

/**
 * Componente de mensagem de chat
 */
export default function ChatMessage({
  message,
  showTimestamp = true,
  showSender = true,
  isLastMessage = false,
}: ChatMessageProps) {
  // Determina o componente de mensagem com base no papel (role)
  const MessageComponent = useMemo(() => {
    switch (message.role) {
      case "user":
        return UserMessage
      case "assistant":
        return AssistantMessage
      default:
        return UserMessage
    }
  }, [message.role])

  return (
    <div
      className={`group relative flex flex-col ${
        message.role === "user" ? "items-end" : "items-start"
      }`}
    >
      {/* Conteúdo da mensagem */}
      <div className="max-w-[85%] md:max-w-[75%]">
        <MessageComponent
          message={message}
          showSender={showSender}
          isLastMessage={isLastMessage}
        />
      </div>

      {/* Timestamp */}
      {showTimestamp && (
        <MessageTimestamp timestamp={message.timestamp} />
      )}

      {/* Ações da mensagem */}
      <div className="absolute top-0 right-0 opacity-0 group-hover:opacity-100 transition-opacity">
        <MessageActions message={message} />
      </div>
    </div>
  )
}
