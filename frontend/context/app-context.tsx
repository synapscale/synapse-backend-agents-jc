"use client"

import React, { createContext, useContext, useState, useCallback } from 'react'
import { Message, Conversation } from '@/types/chat'

interface AppSettings {
  defaultModel: string;
  defaultTheme: 'light' | 'dark' | 'system';
  notifications: boolean;
  autoSave: boolean;
}

interface AppContextType {
  sidebarOpen: boolean
  setSidebarOpen: (open: boolean) => void
  currentTab: string
  setCurrentTab: (tab: string) => void
  theme: 'light' | 'dark' | 'system'
  setTheme: (theme: 'light' | 'dark' | 'system') => void
  conversations: Conversation[]
  currentConversationId: string | null
  addConversation: (conversation: Conversation) => void
  updateConversation: (id: string, updates: Partial<Conversation>) => void
  deleteConversation: (id: string) => void
  setCurrentConversationId: (id: string | null) => void
  settings: AppSettings
  updateSettings: (updates: Partial<AppSettings>) => void
}

const defaultSettings: AppSettings = {
  defaultModel: 'gpt-4o',
  defaultTheme: 'system',
  notifications: true,
  autoSave: true
};

const AppContext = createContext<AppContextType | undefined>(undefined)

export function AppProvider({ children }: { children: React.ReactNode }) {
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [currentTab, setCurrentTab] = useState('canvas')
  const [theme, setTheme] = useState<'light' | 'dark' | 'system'>('system')
  const [conversations, setConversations] = useState<Conversation[]>([])
  // Garante que sempre retorna array
  const conversationsSafe = Array.isArray(conversations) ? conversations : [];
  const [currentConversationId, setCurrentConversationId] = useState<string | null>(null)
  const [settings, setSettings] = useState<AppSettings>(defaultSettings)

  const addConversation = useCallback((conversation: Conversation) => {
    setConversations(prev => [...prev, conversation])
  }, [])

  const updateConversation = useCallback((id: string, updates: Partial<Conversation>) => {
    setConversations(prev => 
      prev.map(conv => conv.id === id ? { ...conv, ...updates } : conv)
    )
  }, [])

  const deleteConversation = useCallback((id: string) => {
    setConversations(prev => prev.filter(conv => conv.id !== id))
    if (currentConversationId === id) {
      setCurrentConversationId(null)
    }
  }, [currentConversationId])

  const updateSettings = useCallback((updates: Partial<AppSettings>) => {
    setSettings(prev => ({ ...prev, ...updates }))
  }, [])

  return (
    <AppContext.Provider
      value={{
        sidebarOpen,
        setSidebarOpen,
        currentTab,
        setCurrentTab,
        theme,
        setTheme,
        conversations: conversationsSafe,
        currentConversationId,
        addConversation,
        updateConversation,
        deleteConversation,
        setCurrentConversationId,
        settings,
        updateSettings
      }}
    >
      {children}
    </AppContext.Provider>
  )
}

// Exportando com ambos os nomes para manter compatibilidade
export function useApp() {
  const context = useContext(AppContext)
  if (context === undefined) {
    throw new Error('useApp must be used within an AppProvider')
  }
  return context
}

// Alias para manter compatibilidade com imports existentes
export const useAppContext = useApp;

export default useApp
