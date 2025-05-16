"use client"

import { useState, useCallback } from "react"
import { Conversation } from "@/types/chat"
import { Button } from "@/components/ui/button"
import { 
  Menu, 
  Plus, 
  MoreVertical, 
  Trash, 
  Download, 
  Edit, 
  AlignJustify 
} from "lucide-react"
import { 
  DropdownMenu, 
  DropdownMenuContent, 
  DropdownMenuItem, 
  DropdownMenuSeparator, 
  DropdownMenuTrigger 
} from "@/components/ui/dropdown-menu"

interface ChatHeaderProps {
  currentConversation?: Conversation | null
  currentConversationId?: string | null
  onNewConversation?: () => void
  onUpdateConversationTitle?: (id: string, title: string) => void
  onDeleteConversation?: (id: string) => void
  onExportConversation?: (id: string) => void
  onToggleSidebar?: () => void
  onToggleComponentSelector?: () => void
}

/**
 * Componente de cabeçalho do chat
 */
export function ChatHeader({
  currentConversation,
  currentConversationId,
  onNewConversation = () => {},
  onUpdateConversationTitle = () => {},
  onDeleteConversation = () => {},
  onExportConversation = () => {},
  onToggleSidebar = () => {},
  onToggleComponentSelector,
}: ChatHeaderProps) {
  // Estados
  const [isEditing, setIsEditing] = useState(false)
  const [editedTitle, setEditedTitle] = useState("")

  /**
   * Inicia a edição do título
   */
  const handleStartEditing = useCallback(() => {
    if (currentConversation) {
      setEditedTitle(currentConversation.title)
      setIsEditing(true)
    }
  }, [currentConversation])

  /**
   * Salva o título editado
   */
  const handleSaveTitle = useCallback(() => {
    if (currentConversationId && editedTitle.trim()) {
      onUpdateConversationTitle(currentConversationId, editedTitle.trim())
      setIsEditing(false)
    }
  }, [currentConversationId, editedTitle, onUpdateConversationTitle])

  /**
   * Manipula teclas durante a edição
   */
  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === "Enter") {
        e.preventDefault()
        handleSaveTitle()
      } else if (e.key === "Escape") {
        setIsEditing(false)
      }
    },
    [handleSaveTitle]
  )

  return (
    <header className="flex items-center justify-between p-4 border-b border-gray-100 dark:border-gray-700 bg-white dark:bg-gray-800 transition-colors duration-200">
      <div className="flex items-center">
        {/* Botão de toggle da barra lateral (visível em dispositivos móveis) */}
        <Button
          variant="ghost"
          size="icon"
          onClick={onToggleSidebar}
          className="mr-2 md:hidden"
          aria-label="Toggle sidebar"
        >
          <AlignJustify className="h-5 w-5" />
        </Button>

        {/* Título da conversa (editável) */}
        {isEditing ? (
          <input
            type="text"
            value={editedTitle}
            onChange={(e) => setEditedTitle(e.target.value)}
            onBlur={handleSaveTitle}
            onKeyDown={handleKeyDown}
            autoFocus
            className="bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded text-sm font-medium focus:outline-none focus:ring-2 focus:ring-primary"
          />
        ) : (
          <h1
            className="text-sm font-medium cursor-pointer hover:underline"
            onClick={handleStartEditing}
          >
            {currentConversation?.title || "Nova conversa"}
          </h1>
        )}
      </div>

      <div className="flex items-center space-x-1">
        {/* Botão de nova conversa */}
        <Button
          variant="ghost"
          size="icon"
          onClick={onNewConversation}
          aria-label="Nova conversa"
        >
          <Plus className="h-5 w-5" />
        </Button>

        {/* Menu de ações */}
        {currentConversationId && (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="icon" aria-label="Mais ações">
                <MoreVertical className="h-5 w-5" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem onClick={handleStartEditing}>
                <Edit className="h-4 w-4 mr-2" />
                Renomear conversa
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => onExportConversation(currentConversationId)}>
                <Download className="h-4 w-4 mr-2" />
                Exportar conversa
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem
                onClick={() => onDeleteConversation(currentConversationId)}
                className="text-red-500 dark:text-red-400"
              >
                <Trash className="h-4 w-4 mr-2" />
                Excluir conversa
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        )}

        {/* Botão de toggle do seletor de componentes (se disponível) */}
        {onToggleComponentSelector && (
          <Button
            variant="ghost"
            size="icon"
            onClick={onToggleComponentSelector}
            aria-label="Toggle component selector"
          >
            <Menu className="h-5 w-5" />
          </Button>
        )}
      </div>
    </header>
  )
}

// Adicionar export default para compatibilidade com importações existentes
export default ChatHeader
