"use client"

import React from 'react'
import { useChat } from '@/hooks/use-chat'
import { ChatHeader } from './chat-header'
import { MessagesArea } from './messages-area'
import { ChatInput } from './chat-input'
import ConversationSidebar from './conversation-sidebar'
import { ThemeSelector } from '@/components/theme/theme-selector'
import { KeyboardShortcutsDialog } from '@/components/keyboard-shortcuts/keyboard-shortcuts-dialog'
import { useKeyboardShortcuts } from '@/components/keyboard-shortcuts/keyboard-shortcuts-context'
import { useTheme } from '@/components/theme/theme-provider'
import { useOnboarding } from '@/components/onboarding/onboarding-context'
import { Button } from '@/components/ui/button'
import { Maximize2, Minimize2, SidebarClose, SidebarOpen } from 'lucide-react'
import { cn } from '@/lib/utils'

export default function ChatInterface() {
  const { 
    messages, 
    isLoading, 
    sendMessage, 
    currentModel, 
    setCurrentModel,
    availableModels
  } = useChat()
  
  const { registerShortcut } = useKeyboardShortcuts()
  const { theme } = useTheme()
  const { setShowOnboarding, setCurrentTour } = useOnboarding()
  
  const [isSidebarOpen, setIsSidebarOpen] = React.useState(true)
  const [isFullscreen, setIsFullscreen] = React.useState(false)
  const messagesEndRef = React.useRef<HTMLDivElement>(null)
  
  // Registrar atalhos de teclado
  React.useEffect(() => {
    // Alternar barra lateral
    registerShortcut('toggle_sidebar', {
      keys: ['Ctrl', 'b'],
      description: 'Alternar barra lateral',
      category: 'Interface',
      action: () => setIsSidebarOpen(prev => !prev)
    })
    
    // Alternar modo tela cheia
    registerShortcut('toggle_fullscreen', {
      keys: ['F11'],
      description: 'Alternar modo tela cheia',
      category: 'Interface',
      action: () => setIsFullscreen(prev => !prev)
    })
    
    // Mostrar tour de onboarding
    registerShortcut('show_tour', {
      keys: ['Ctrl', 'h'],
      description: 'Mostrar tour de ajuda',
      category: 'Ajuda',
      action: () => {
        setShowOnboarding(true)
        setCurrentTour('chat-tour')
      }
    })
    
    // Foco na entrada de mensagem
    registerShortcut('focus_input', {
      keys: ['Ctrl', '/'],
      description: 'Focar na entrada de mensagem',
      category: 'Chat',
      action: () => {
        const inputElement = document.querySelector('.chat-input textarea')
        if (inputElement instanceof HTMLTextAreaElement) {
          inputElement.focus()
        }
      }
    })
  }, [registerShortcut, setShowOnboarding, setCurrentTour])
  
  // Manipular envio de mensagem
  const handleSendMessage = React.useCallback((content: string, files?: File[]) => {
    sendMessage(content, files)
  }, [sendMessage])
  
  return (
    <div 
      className={cn(
        "flex h-full transition-all duration-300 chat-interface",
        isFullscreen && "fixed inset-0 z-50 bg-background"
      )}
      data-component="ChatInterface"
    >
      {/* Barra lateral de conversas */}
      <ConversationSidebar 
        className={cn(
          "w-64 transition-all duration-300",
          !isSidebarOpen && "w-0 opacity-0 overflow-hidden"
        )}
      />
      
      {/* Área principal do chat */}
      <div className="flex-1 flex flex-col h-full overflow-hidden">
        {/* Cabeçalho */}
        <ChatHeader
          currentModel={currentModel}
          setCurrentModel={setCurrentModel}
          availableModels={availableModels}
          leftAccessory={
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setIsSidebarOpen(prev => !prev)}
              className="mr-2"
            >
              {isSidebarOpen ? (
                <SidebarClose className="h-5 w-5" />
              ) : (
                <SidebarOpen className="h-5 w-5" />
              )}
              <span className="sr-only">
                {isSidebarOpen ? 'Fechar barra lateral' : 'Abrir barra lateral'}
              </span>
            </Button>
          }
          rightAccessory={
            <div className="flex items-center gap-1">
              <ThemeSelector triggerClassName="h-8 w-8" />
              <KeyboardShortcutsDialog triggerClassName="h-8 w-8" />
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setIsFullscreen(prev => !prev)}
                className="h-8 w-8"
              >
                {isFullscreen ? (
                  <Minimize2 className="h-5 w-5" />
                ) : (
                  <Maximize2 className="h-5 w-5" />
                )}
                <span className="sr-only">
                  {isFullscreen ? 'Sair da tela cheia' : 'Modo tela cheia'}
                </span>
              </Button>
            </div>
          }
        />
        
        {/* Área de mensagens */}
        <MessagesArea
          messages={messages}
          isLoading={isLoading}
          messagesEndRef={messagesEndRef}
          theme={theme}
        />
        
        {/* Entrada de mensagem */}
        <div className="p-4 border-t">
          <ChatInput
            onSendMessage={handleSendMessage}
            isLoading={isLoading}
            placeholder="Digite sua mensagem ou '/ajuda' para ver comandos..."
            maxTokens={4096}
          />
        </div>
      </div>
    </div>
  )
}
