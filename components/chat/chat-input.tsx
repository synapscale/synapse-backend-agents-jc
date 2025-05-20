"use client"

import type React from "react"

import { useRef } from "react"
import { Send, Paperclip } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { useTextarea } from "../../apps/ai-agents-sidebar/hooks/use-textarea"

interface ChatInputProps {
  onSendMessage: (message: string) => void
  isLoading: boolean
  disabled: boolean
  isDragOver: boolean
  onDragOver: (e: React.DragEvent<HTMLDivElement>) => void
  onDragLeave: (e: React.DragEvent<HTMLDivElement>) => void
  onDrop: (e: React.DragEvent<HTMLDivElement>) => void
}

export function ChatInput({
  onSendMessage,
  isLoading,
  disabled,
  isDragOver,
  onDragOver,
  onDragLeave,
  onDrop,
}: ChatInputProps) {
  const chatAreaRef = useRef<HTMLDivElement>(null)

  const handleSubmit = () => {
    if (textarea.value.trim() && !isLoading && !disabled) {
      onSendMessage(textarea.value)
      textarea.resetTextarea()
    }
  }

  const textarea = useTextarea({
    onSubmit: handleSubmit,
  })

  return (
    <Card
      className={`border ${
        isDragOver ? "border-primary border-dashed bg-primary/5" : "border-gray-200 dark:border-gray-700"
      } rounded-xl overflow-hidden shadow-sm hover:shadow transition-shadow duration-200 bg-white dark:bg-gray-800`}
      onDragOver={onDragOver}
      onDragLeave={onDragLeave}
      onDrop={onDrop}
      ref={chatAreaRef}
    >
      <div className="p-2">
        <div className="relative">
          <textarea
            ref={textarea.textareaRef}
            value={textarea.value}
            onChange={textarea.handleInput}
            onKeyDown={textarea.handleKeyDown}
            placeholder={
              isDragOver ? "Solte o componente aqui..." : "Digite sua mensagem aqui ou @ para chamar outro agente..."
            }
            className={`w-full border-0 focus:ring-0 focus:outline-none resize-none p-3 pr-10 max-h-32 text-gray-700 dark:text-gray-200 placeholder-gray-400 dark:placeholder-gray-500 bg-white dark:bg-gray-800 transition-colors duration-200 ${
              isDragOver ? "border-2 border-dashed border-primary/50 bg-primary/5" : ""
            }`}
            style={{ height: "auto" }}
            disabled={disabled}
            onDragOver={onDragOver}
            onDragLeave={onDragLeave}
            onDrop={onDrop}
          />
          <div className="absolute right-2 bottom-2 flex items-center space-x-1">
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8 text-gray-400 hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-300 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700"
            >
              <Paperclip className="h-5 w-5" />
            </Button>
            <Button
              size="icon"
              className="h-9 w-9 rounded-full bg-primary text-white hover:bg-primary/90 shadow-sm transition-all duration-200 hover:shadow"
              onClick={handleSubmit}
              disabled={!textarea.value.trim() || isLoading || disabled}
            >
              <Send className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>
    </Card>
  )
}
