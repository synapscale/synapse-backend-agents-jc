"use client"

import { useRef, useEffect, useMemo } from "react"
import { Message } from "@/types/chat"
import ChatMessage from "./chat-message"
import { Loader2 } from "lucide-react"

interface MessagesAreaProps {
  messages?: Message[]
  isLoading?: boolean
  showTimestamps?: boolean
  showSenders?: boolean
  focusMode?: boolean
  theme?: "light" | "dark" | "system"
  chatBackground?: string | null
  messagesEndRef?: React.RefObject<HTMLDivElement>
}

/**
 * Área de mensagens do chat
 */
export function MessagesArea({
  messages = [],
  isLoading = false,
  showTimestamps = true,
  showSenders = true,
  focusMode = false,
  theme = "light",
  chatBackground = null,
  messagesEndRef,
}: MessagesAreaProps) {
  // Referência para o contêiner de mensagens
  const containerRef = useRef<HTMLDivElement>(null)

  // Efeito para rolar para o final quando novas mensagens são adicionadas
  useEffect(() => {
    if (messagesEndRef?.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" })
    }
  }, [messages, messagesEndRef])

  // Estilo do background
  const backgroundStyle = useMemo(() => {
    if (chatBackground) {
      return { backgroundImage: `url(${chatBackground})`, backgroundSize: "cover" }
    }
    return {}
  }, [chatBackground])

  // Classes CSS
  const containerClassName = useMemo(
    () =>
      `flex-1 overflow-y-auto p-4 ${
        focusMode ? "focus-mode" : ""
      } bg-gray-50 dark:bg-gray-900 transition-colors duration-200`,
    [focusMode]
  )

  return (
    <div className={containerClassName} ref={containerRef} style={backgroundStyle}>
      <div className="max-w-3xl mx-auto space-y-4">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full min-h-[200px] text-center p-4">
            <div className="text-gray-500 dark:text-gray-400 mb-2">
              Nenhuma mensagem ainda. Comece uma conversa!
            </div>
          </div>
        ) : (
          messages.map((message, index) => (
            <ChatMessage
              key={message.id}
              message={message}
              showTimestamp={showTimestamps}
              showSender={showSenders}
              isLastMessage={index === messages.length - 1}
            />
          ))
        )}

        {/* Indicador de carregamento */}
        {isLoading && (
          <div className="flex items-center text-gray-500 dark:text-gray-400 animate-in">
            <Loader2 className="h-4 w-4 mr-2 animate-spin" />
            <span className="text-sm">Processando...</span>
          </div>
        )}

        {/* Elemento para rolar para o final */}
        <div ref={messagesEndRef} />
      </div>
    </div>
  )
}

// Adicionar export default para compatibilidade com importações existentes
export default MessagesArea
