"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Search, X, Clock, Star, Trash, ChevronLeft } from "lucide-react"
import type { Conversation } from "@/types/chat"
import { motion, AnimatePresence } from "framer-motion"

interface ChatHistorySidebarProps {
  isOpen: boolean
  onClose: () => void
  conversations: Conversation[]
  currentConversationId: string | null
  onSelectConversation: (id: string) => void
  onDeleteConversation: (id: string) => void
  onNewConversation: () => void
}

export function ChatHistorySidebar({
  isOpen,
  onClose,
  conversations,
  currentConversationId,
  onSelectConversation,
  onDeleteConversation,
  onNewConversation,
}: ChatHistorySidebarProps) {
  const [searchQuery, setSearchQuery] = useState("")
  const [filteredConversations, setFilteredConversations] = useState<Conversation[]>(conversations)

  // Filtrar conversas quando a busca ou a lista de conversas mudar
  useEffect(() => {
    if (!searchQuery.trim()) {
      setFilteredConversations(conversations)
      return
    }

    const query = searchQuery.toLowerCase()
    const filtered = conversations.filter(
      (conversation) =>
        conversation.title?.toLowerCase().includes(query) ||
        conversation.messages.some((message) => message.content.toLowerCase().includes(query))
    )
    setFilteredConversations(filtered)
  }, [searchQuery, conversations])

  // Agrupar conversas por data
  const groupedConversations = filteredConversations.reduce<Record<string, Conversation[]>>(
    (groups, conversation) => {
      const date = new Date(conversation.createdAt || Date.now())
      const today = new Date()
      const yesterday = new Date(today)
      yesterday.setDate(yesterday.getDate() - 1)

      let groupKey: string

      if (date.toDateString() === today.toDateString()) {
        groupKey = "Hoje"
      } else if (date.toDateString() === yesterday.toDateString()) {
        groupKey = "Ontem"
      } else {
        groupKey = date.toLocaleDateString("pt-BR", {
          year: "numeric",
          month: "long",
          day: "numeric",
        })
      }

      if (!groups[groupKey]) {
        groups[groupKey] = []
      }
      groups[groupKey].push(conversation)
      return groups
    },
    {}
  )

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ x: "100%" }}
          animate={{ x: 0 }}
          exit={{ x: "100%" }}
          transition={{ duration: 0.3, ease: "easeInOut" }}
          className="fixed top-0 right-0 z-50 h-full w-80 bg-white dark:bg-gray-900 border-l border-gray-200 dark:border-gray-800 shadow-lg"
        >
          <div className="flex flex-col h-full">
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-800">
              <h2 className="text-lg font-semibold">Histórico de Conversas</h2>
              <Button
                variant="ghost"
                size="icon"
                onClick={onClose}
                className="h-8 w-8"
                aria-label="Fechar histórico"
              >
                <X className="h-4 w-4" />
              </Button>
            </div>

            {/* Search */}
            <div className="p-4 border-b border-gray-200 dark:border-gray-800">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  placeholder="Buscar conversas..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-9 h-9"
                />
                {searchQuery && (
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => setSearchQuery("")}
                    className="absolute right-1 top-1/2 transform -translate-y-1/2 h-7 w-7"
                    aria-label="Limpar busca"
                  >
                    <X className="h-3 w-3" />
                  </Button>
                )}
              </div>
            </div>

            {/* Conversation List */}
            <ScrollArea className="flex-1 p-4">
              {Object.entries(groupedConversations).length > 0 ? (
                Object.entries(groupedConversations).map(([date, dateConversations]) => (
                  <div key={date} className="mb-6">
                    <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">{date}</h3>
                    <div className="space-y-2">
                      {dateConversations.map((conversation) => (
                        <div
                          key={conversation.id}
                          className={`p-3 rounded-lg cursor-pointer transition-colors duration-200 ${
                            conversation.id === currentConversationId
                              ? "bg-primary/10 dark:bg-primary/20"
                              : "hover:bg-gray-100 dark:hover:bg-gray-800"
                          }`}
                          onClick={() => onSelectConversation(conversation.id)}
                        >
                          <div className="flex items-start justify-between">
                            <div className="flex-1 min-w-0">
                              <h4 className="text-sm font-medium truncate">
                                {conversation.title || "Nova conversa"}
                              </h4>
                              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1 truncate">
                                {conversation.messages.length > 0
                                  ? conversation.messages[conversation.messages.length - 1].content.substring(0, 50) +
                                    (conversation.messages[conversation.messages.length - 1].content.length > 50
                                      ? "..."
                                      : "")
                                  : "Sem mensagens"}
                              </p>
                            </div>
                            <div className="flex items-center ml-2">
                              {conversation.isFavorite && <Star className="h-3 w-3 text-yellow-500 fill-yellow-500" />}
                              <Button
                                variant="ghost"
                                size="icon"
                                onClick={(e) => {
                                  e.stopPropagation()
                                  onDeleteConversation(conversation.id)
                                }}
                                className="h-6 w-6 ml-1 opacity-0 group-hover:opacity-100 hover:opacity-100 focus:opacity-100"
                                aria-label="Excluir conversa"
                              >
                                <Trash className="h-3 w-3 text-gray-400 hover:text-red-500" />
                              </Button>
                            </div>
                          </div>
                          <div className="flex items-center mt-2 text-xs text-gray-500 dark:text-gray-400">
                            <Clock className="h-3 w-3 mr-1" />
                            <span>
                              {new Date(conversation.createdAt || Date.now()).toLocaleTimeString("pt-BR", {
                                hour: "2-digit",
                                minute: "2-digit",
                              })}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                ))
              ) : (
                <div className="flex flex-col items-center justify-center h-full text-center p-4">
                  <div className="bg-gray-100 dark:bg-gray-800 rounded-full p-3 mb-4">
                    <Clock className="h-6 w-6 text-gray-400" />
                  </div>
                  <h3 className="text-sm font-medium mb-1">Nenhuma conversa encontrada</h3>
                  <p className="text-xs text-gray-500 dark:text-gray-400 mb-4">
                    {searchQuery
                      ? "Tente uma busca diferente"
                      : "Inicie uma nova conversa para começar"}
                  </p>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={onNewConversation}
                    className="text-xs"
                  >
                    Nova conversa
                  </Button>
                </div>
              )}
            </ScrollArea>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
