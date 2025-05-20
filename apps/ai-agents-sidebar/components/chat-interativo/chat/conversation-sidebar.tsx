"use client"

import { useState } from "react"
import { PlusCircle, MessageSquare, Search, Trash2, MoreVertical, X, Filter, SortDesc } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Badge } from "@/components/ui/badge"
import { useApp } from "@/contexts/app-context"
import type { Conversation } from "@/types/chat"

interface ConversationSidebarProps {
  conversations: Conversation[]
  currentConversationId: string | null
  onSelectConversation: (id: string) => void
  onNewConversation: () => void
  onDeleteConversation: (id: string) => void
  onClearConversations: () => void
}

export default function ConversationSidebar({
  conversations,
  currentConversationId,
  onSelectConversation,
  onNewConversation,
  onDeleteConversation,
  onClearConversations,
}: ConversationSidebarProps) {
  const [searchQuery, setSearchQuery] = useState("")
  const [showSearch, setShowSearch] = useState(false)
  const { setLastAction } = useApp()

  // Formata a data para exibição
  const formatDate = (timestamp: number) => {
    const date = new Date(timestamp)
    const today = new Date()
    const yesterday = new Date(today)
    yesterday.setDate(yesterday.getDate() - 1)

    if (date.toDateString() === today.toDateString()) {
      return `Hoje, ${date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}`
    } else if (date.toDateString() === yesterday.toDateString()) {
      return `Ontem, ${date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}`
    } else {
      return date.toLocaleDateString([], {
        day: "2-digit",
        month: "2-digit",
        year: "numeric",
      })
    }
  }

  // Filtra as conversas com base na pesquisa
  const filteredConversations = conversations
    .filter((conv) => searchQuery === "" || conv.title.toLowerCase().includes(searchQuery.toLowerCase()))
    .sort((a, b) => b.updatedAt - a.updatedAt) // Ordena por mais recente primeiro

  return (
    <div
      className="w-72 h-full flex flex-col border-r border-gray-100 dark:border-gray-700 bg-white dark:bg-gray-800 shadow-sm conversation-sidebar transition-colors duration-200"
      data-component="ConversationSidebar"
      data-component-path="@/components/chat/conversation-sidebar"
    >
      <div className="p-4 border-b border-gray-100 dark:border-gray-700">
        <div className="flex items-center justify-between mb-3">
          <h2 className="font-semibold text-gray-800 dark:text-gray-200">Conversas</h2>
          <div className="flex items-center space-x-1">
            {showSearch ? (
              <Button
                variant="ghost"
                size="icon"
                className="h-8 w-8 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700"
                onClick={() => {
                  setShowSearch(false)
                  setSearchQuery("")
                }}
              >
                <X className="h-4 w-4 text-gray-600 dark:text-gray-300" />
              </Button>
            ) : (
              <Button
                variant="ghost"
                size="icon"
                className="h-8 w-8 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700"
                onClick={() => setShowSearch(true)}
              >
                <Search className="h-4 w-4 text-gray-600 dark:text-gray-300" />
              </Button>
            )}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-8 w-8 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700"
                >
                  <MoreVertical className="h-4 w-4 text-gray-600 dark:text-gray-300" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-48">
                <DropdownMenuItem
                  className="text-red-600 dark:text-red-400 cursor-pointer"
                  onClick={onClearConversations}
                >
                  <Trash2 className="h-4 w-4 mr-2" />
                  Limpar todas as conversas
                </DropdownMenuItem>
                <DropdownMenuItem>
                  <Filter className="h-4 w-4 mr-2" />
                  Filtrar conversas
                </DropdownMenuItem>
                <DropdownMenuItem>
                  <SortDesc className="h-4 w-4 mr-2" />
                  Ordenar por data
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>

        {showSearch && (
          <div className="mt-2 animate-in">
            <Input
              placeholder="Pesquisar conversas..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="h-9 text-sm rounded-full bg-gray-50 dark:bg-gray-700 border-gray-100 dark:border-gray-600 focus:border-primary/30 focus:ring-primary/20 pl-4"
            />
          </div>
        )}

        <Button
          variant="default"
          className="w-full mt-3 bg-primary hover:bg-primary/90 text-white rounded-full h-10 shadow-sm transition-all duration-200 hover:shadow"
          onClick={() => {
            onNewConversation()
            // Use a more stable way to set the last action
            setTimeout(() => {
              setLastAction("Nova conversa criada")
            }, 0)
          }}
        >
          <PlusCircle className="h-4 w-4 mr-2" />
          Nova conversa
        </Button>
      </div>

      <ScrollArea className="flex-1 overflow-y-auto scrollbar-thin">
        {filteredConversations.length === 0 ? (
          <div className="p-4 text-center text-gray-500 dark:text-gray-400 text-sm">
            {searchQuery ? "Nenhuma conversa encontrada" : "Nenhuma conversa ainda"}
          </div>
        ) : (
          <ul className="py-2">
            {filteredConversations.map((conversation) => (
              <li key={conversation.id} className="group px-2">
                <button
                  className={`w-full text-left px-3 py-2.5 flex items-start rounded-lg transition-all duration-200 ${
                    conversation.id === currentConversationId
                      ? "bg-primary/10 dark:bg-primary/20 text-primary"
                      : "hover:bg-gray-50 dark:hover:bg-gray-700"
                  }`}
                  onClick={() => onSelectConversation(conversation.id)}
                >
                  <MessageSquare
                    className={`h-5 w-5 mr-3 flex-shrink-0 mt-0.5 ${
                      conversation.id === currentConversationId ? "text-primary" : "text-gray-400 dark:text-gray-500"
                    }`}
                  />
                  <div className="flex-1 min-w-0">
                    <div className="font-medium text-sm truncate text-gray-700 dark:text-gray-200">
                      {conversation.title}
                    </div>
                    <div className="text-xs text-gray-500 dark:text-gray-400 mt-1 flex items-center justify-between">
                      <span>{formatDate(conversation.updatedAt)}</span>
                      {conversation.id === currentConversationId && (
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-6 w-6 ml-2 opacity-0 group-hover:opacity-100 hover:bg-red-100 dark:hover:bg-red-900/30 hover:text-red-600 dark:hover:text-red-400 rounded-full transition-opacity duration-200"
                          onClick={(e) => {
                            e.stopPropagation()
                            onDeleteConversation(conversation.id)
                            setLastAction("Conversa excluída")
                          }}
                        >
                          <Trash2 className="h-3 w-3" />
                        </Button>
                      )}
                    </div>
                    {conversation.metadata && (
                      <div className="mt-1.5 flex flex-wrap gap-1">
                        {conversation.metadata.model && (
                          <Badge
                            variant="outline"
                            className="text-[10px] h-5 px-1.5 bg-gray-50 dark:bg-gray-700 text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-600 border-gray-100 dark:border-gray-600"
                          >
                            {conversation.metadata.model.split("-")[0]}
                          </Badge>
                        )}
                        {conversation.metadata.tool && conversation.metadata.tool !== "No Tools" && (
                          <Badge
                            variant="outline"
                            className="text-[10px] h-5 px-1.5 bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 hover:bg-blue-100 dark:hover:bg-blue-900/50 border-blue-100 dark:border-blue-800"
                          >
                            {conversation.metadata.tool}
                          </Badge>
                        )}
                      </div>
                    )}
                  </div>
                </button>
              </li>
            ))}
          </ul>
        )}
      </ScrollArea>

      <div className="p-4 border-t border-gray-100 dark:border-gray-700">
        <div className="flex items-center bg-gray-50 dark:bg-gray-700 rounded-lg p-2 transition-colors duration-200">
          <div className="h-8 w-8 rounded-full bg-gray-200 dark:bg-gray-600 flex items-center justify-center mr-2">
            <span className="text-sm text-gray-600 dark:text-gray-300">J</span>
          </div>
          <div>
            <p className="text-sm font-medium text-gray-700 dark:text-gray-200">João Victor</p>
            <p className="text-xs text-gray-500 dark:text-gray-400 flex items-center">
              <span className="w-1.5 h-1.5 bg-green-500 rounded-full mr-1"></span>
              Online
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
