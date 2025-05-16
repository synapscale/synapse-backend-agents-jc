"use client"

import { useState, useRef, useCallback } from "react"
import { Send, Paperclip, X } from "lucide-react"
import { Button } from "@/components/ui/button"
import { estimateTokenCount } from "@/lib/ai-utils"
import { useTextarea } from "@/hooks/use-textarea"

interface ChatInputProps {
  onSendMessage?: (content: string, files?: File[]) => void
  isLoading?: boolean
  disabled?: boolean
  isDragOver?: boolean
  onDragOver?: (e: React.DragEvent) => void
  onDragLeave?: (e: React.DragEvent) => void
  onDrop?: (e: React.DragEvent) => void
  maxTokens?: number
  placeholder?: string
}

/**
 * Componente de entrada de chat
 */
export function ChatInput({
  onSendMessage = () => {},
  isLoading = false,
  disabled = false,
  isDragOver = false,
  onDragOver,
  onDragLeave,
  onDrop,
  maxTokens = 4000,
  placeholder = "Digite sua mensagem...",
}: ChatInputProps) {
  // Estados
  const [message, setMessage] = useState("")
  const [files, setFiles] = useState<File[]>([])
  const fileInputRef = useRef<HTMLInputElement>(null)

  // Estimativa de tokens
  const tokenCount = estimateTokenCount(message)
  const isApproachingLimit = tokenCount > maxTokens * 0.8
  const isOverLimit = tokenCount > maxTokens

  // Hook personalizado para textarea
  const { textareaRef, handleInput, handleKeyDown } = useTextarea({
    onEnter: (e) => {
      if (!e.shiftKey && !isLoading && !disabled && !isOverLimit) {
        e.preventDefault()
        handleSendMessage()
      }
    },
  })

  /**
   * Manipula o envio de mensagem
   */
  const handleSendMessage = useCallback(() => {
    if (message.trim() || files.length > 0) {
      onSendMessage(message, files.length > 0 ? files : undefined)
      setMessage("")
      setFiles([])
    }
  }, [message, files, onSendMessage])

  /**
   * Manipula o clique no botão de upload
   */
  const handleFileButtonClick = useCallback(() => {
    fileInputRef.current?.click()
  }, [])

  /**
   * Manipula a seleção de arquivos
   */
  const handleFileChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFiles(Array.from(e.target.files))
    }
  }, [])

  /**
   * Remove um arquivo da lista
   */
  const handleRemoveFile = useCallback((index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index))
  }, [])

  return (
    <div
      className={`relative rounded-lg border ${
        isDragOver
          ? "border-primary border-dashed bg-primary/5"
          : "border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800"
      } transition-colors duration-200`}
      onDragOver={onDragOver}
      onDragLeave={onDragLeave}
      onDrop={onDrop}
    >
      {/* Área de arquivos */}
      {files.length > 0 && (
        <div className="px-3 pt-2">
          <div className="flex flex-wrap gap-2 mb-2">
            {files.map((file, index) => (
              <div
                key={index}
                className="flex items-center gap-1 text-xs bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded"
              >
                <Paperclip className="h-3 w-3" />
                <span className="max-w-[150px] truncate">{file.name}</span>
                <button
                  type="button"
                  onClick={() => handleRemoveFile(index)}
                  className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
                >
                  <X className="h-3 w-3" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Área de entrada */}
      <div className="flex items-end p-2">
        <div className="relative flex-1">
          <textarea
            ref={textareaRef}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            onInput={handleInput}
            placeholder={placeholder}
            disabled={isLoading || disabled}
            className={`w-full resize-none bg-transparent px-3 py-2 outline-none placeholder:text-gray-400 dark:placeholder:text-gray-500 ${
              isOverLimit ? "text-red-500 dark:text-red-400" : ""
            }`}
            rows={1}
            style={{ maxHeight: "200px", minHeight: "44px" }}
          />
          
          {/* Contador de tokens */}
          {message.length > 0 && (
            <div
              className={`absolute right-2 bottom-1 text-xs ${
                isOverLimit
                  ? "text-red-500 dark:text-red-400"
                  : isApproachingLimit
                  ? "text-amber-500 dark:text-amber-400"
                  : "text-gray-400 dark:text-gray-500"
              }`}
            >
              {tokenCount}/{maxTokens}
            </div>
          )}
        </div>

        {/* Botão de upload */}
        <Button
          type="button"
          variant="ghost"
          size="icon"
          onClick={handleFileButtonClick}
          disabled={isLoading || disabled}
          className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
        >
          <Paperclip className="h-5 w-5" />
          <span className="sr-only">Anexar arquivo</span>
        </Button>
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileChange}
          className="hidden"
          multiple
        />

        {/* Botão de envio */}
        <Button
          type="button"
          variant="default"
          size="icon"
          onClick={handleSendMessage}
          disabled={isLoading || disabled || (message.trim() === "" && files.length === 0) || isOverLimit}
          className={isOverLimit ? "bg-gray-300 dark:bg-gray-700 cursor-not-allowed" : ""}
        >
          <Send className="h-5 w-5" />
          <span className="sr-only">Enviar mensagem</span>
        </Button>
      </div>

      {/* Mensagem de drag and drop */}
      {isDragOver && (
        <div className="absolute inset-0 flex items-center justify-center bg-primary/5 rounded-lg border border-primary border-dashed pointer-events-none">
          <div className="text-primary font-medium">Solte os arquivos aqui</div>
        </div>
      )}
    </div>
  )
}

// Adicionar export default para compatibilidade com importações existentes
export default ChatInput
