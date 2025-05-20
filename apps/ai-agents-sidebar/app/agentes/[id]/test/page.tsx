"use client"

import { useState, useEffect, useRef, useMemo } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { ArrowLeft, Send, Loader2, Bot, User } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Textarea } from "@/components/ui/textarea"
import { Skeleton } from "@/components/ui/skeleton"
import { toast } from "@/components/ui/use-toast"
import { useLocalStorage } from "@/hooks/use-local-storage"

// Interface for agents in storage
interface Agent {
  id: string
  name: string
  type: string
  model: string
  prompt?: string
  createdAt: string
  updatedAt: string
  status?: "active" | "draft" | "archived"
  urls?: Array<{ id: string; label: string }>
  agents?: Array<{ id: string; label: string }>
}

// Message type
interface Message {
  id: string
  role: "user" | "assistant" | "system"
  content: string
  timestamp: string
}

// Conversation type
interface Conversation {
  id: string
  agentId: string
  messages: Message[]
  title: string
  createdAt: string
  updatedAt: string
}

export default function AgentTestPage({ params }: { params: { id: string } }) {
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(true)
  const [agents, setAgents] = useLocalStorage<Agent[]>("agents", [])
  const [conversations, setConversations] = useLocalStorage<Conversation[]>("conversations", [])
  const [currentConversation, setCurrentConversation] = useState<Conversation | null>(null)
  const [input, setInput] = useState("")
  const [isProcessing, setIsProcessing] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Find the agent
  const agent = useMemo(() => {
    return agents.find((a) => a.id === params.id)
  }, [agents, params.id])

  // Initialize or find conversation
  useEffect(() => {
    if (!agent) return

    // Find existing conversation or create new one
    const existingConversation = conversations.find((c) => c.agentId === agent.id)

    if (existingConversation) {
      setCurrentConversation(existingConversation)
    } else {
      // Create new conversation
      const newConversation: Conversation = {
        id: Date.now().toString(),
        agentId: agent.id,
        messages: [
          {
            id: Date.now().toString(),
            role: "system",
            content: agent.prompt || "Você é um assistente útil.",
            timestamp: new Date().toISOString(),
          },
        ],
        title: `Conversa com ${agent.name}`,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      }

      setConversations((prev) => [...prev, newConversation])
      setCurrentConversation(newConversation)
    }

    setIsLoading(false)
  }, [agent, conversations, setConversations])

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [currentConversation?.messages])

  // Handle send message
  const handleSendMessage = async () => {
    if (!input.trim() || !currentConversation || !agent) return

    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input,
      timestamp: new Date().toISOString(),
    }

    // Update conversation
    const updatedConversation = {
      ...currentConversation,
      messages: [...currentConversation.messages, userMessage],
      updatedAt: new Date().toISOString(),
    }

    setCurrentConversation(updatedConversation)
    setConversations((prev) => prev.map((c) => (c.id === updatedConversation.id ? updatedConversation : c)))

    // Clear input
    setInput("")

    // Simulate AI response
    setIsProcessing(true)

    try {
      // In a real app, this would be an API call to your AI service
      await new Promise((resolve) => setTimeout(resolve, 2000))

      // Generate a response based on the agent's type
      let responseContent = ""

      switch (agent.type) {
        case "chat":
          responseContent = `Aqui está uma resposta simulada do agente ${agent.name} usando o modelo ${agent.model}.\n\nEsta é uma demonstração de como o agente responderia à sua mensagem: "${input}"\n\nEm uma implementação real, esta resposta seria gerada pelo modelo de IA especificado.`
          break
        case "imagem":
          responseContent = `[Imagem gerada com base no prompt: "${input}"]\n\nEm uma implementação real, uma imagem seria gerada aqui.`
          break
        case "texto":
          responseContent = `Texto gerado com base no prompt: "${input}"\n\nEm uma implementação real, este texto seria gerado pelo modelo de IA especificado.`
          break
        default:
          responseContent = "Resposta simulada do agente."
      }

      // Add assistant message
      const assistantMessage: Message = {
        id: Date.now().toString(),
        role: "assistant",
        content: responseContent,
        timestamp: new Date().toISOString(),
      }

      // Update conversation again
      const finalConversation = {
        ...updatedConversation,
        messages: [...updatedConversation.messages, assistantMessage],
        updatedAt: new Date().toISOString(),
      }

      setCurrentConversation(finalConversation)
      setConversations((prev) => prev.map((c) => (c.id === finalConversation.id ? finalConversation : c)))
    } catch (error) {
      toast({
        title: "Erro ao processar mensagem",
        description: "Ocorreu um erro ao processar sua mensagem. Tente novamente.",
        variant: "destructive",
      })
    } finally {
      setIsProcessing(false)
    }
  }

  // Format timestamp
  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp)
    return new Intl.DateTimeFormat("pt-BR", {
      hour: "2-digit",
      minute: "2-digit",
    }).format(date)
  }

  // Loading state
  if (isLoading) {
    return (
      <div className="flex flex-col h-screen">
        <header className="flex items-center justify-between p-4 border-b bg-white">
          <div className="flex items-center gap-2">
            <Skeleton className="h-9 w-24" />
            <div className="w-px h-6 bg-gray-200" aria-hidden="true"></div>
            <Skeleton className="h-8 w-48" />
          </div>
          <Skeleton className="h-9 w-9" />
        </header>

        <div className="flex-1 overflow-auto p-4">
          <div className="space-y-4">
            <Skeleton className="h-16 w-3/4 ml-auto" />
            <Skeleton className="h-24 w-3/4" />
            <Skeleton className="h-16 w-3/4 ml-auto" />
            <Skeleton className="h-32 w-3/4" />
          </div>
        </div>

        <div className="p-4 border-t bg-white">
          <Skeleton className="h-20 w-full" />
        </div>
      </div>
    )
  }

  // Agent not found
  if (!agent) {
    return (
      <div className="flex flex-col h-screen">
        <header className="flex items-center p-4 border-b bg-white">
          <Link href="/agentes" className="flex items-center text-gray-500 hover:text-gray-900">
            <ArrowLeft className="mr-1 h-4 w-4" />
            Voltar
          </Link>
          <div className="w-px h-6 bg-gray-200 mx-2" aria-hidden="true"></div>
          <h1 className="text-xl font-bold">Agente não encontrado</h1>
        </header>

        <div className="flex-1 flex items-center justify-center">
          <div className="text-center p-6">
            <p className="text-muted-foreground mb-4">O agente solicitado não foi encontrado.</p>
            <Link href="/agentes">
              <Button className="bg-purple-600 hover:bg-purple-700">Voltar para a lista de agentes</Button>
            </Link>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="flex flex-col h-screen">
      <header className="flex items-center justify-between p-4 border-b bg-white">
        <div className="flex items-center gap-2">
          <Link href={`/agentes/${agent.id}/view`} className="flex items-center text-gray-500 hover:text-gray-900">
            <ArrowLeft className="mr-1 h-4 w-4" />
            Voltar
          </Link>
          <div className="w-px h-6 bg-gray-200" aria-hidden="true"></div>
          <h1 className="text-lg font-medium truncate">{agent.name}</h1>
          <Badge variant="outline" className="bg-muted/30">
            {agent.model}
          </Badge>
        </div>
      </header>

      <div className="flex-1 overflow-auto p-4 bg-gray-50">
        <div className="max-w-3xl mx-auto space-y-4">
          {currentConversation?.messages.filter((m) => m.role !== "system").length === 0 ? (
            <div className="text-center py-12">
              <Bot className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
              <h2 className="text-lg font-medium mb-2">Comece uma conversa com {agent.name}</h2>
              <p className="text-muted-foreground mb-6">
                Digite uma mensagem abaixo para começar a interagir com este agente.
              </p>
              <div className="max-w-md mx-auto p-4 bg-white rounded-lg border">
                <h3 className="font-medium mb-2">Sobre este agente</h3>
                <p className="text-sm text-muted-foreground mb-2">
                  {agent.prompt?.substring(0, 100) ||
                    `Este é um agente do tipo ${agent.type} usando o modelo ${agent.model}.`}
                  ...
                </p>
                <div className="text-xs text-muted-foreground">
                  Criado em {new Date(agent.createdAt).toLocaleDateString()}
                </div>
              </div>
            </div>
          ) : (
            currentConversation?.messages
              .filter((m) => m.role !== "system")
              .map((message) => (
                <div key={message.id} className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}>
                  <div
                    className={`max-w-[80%] rounded-lg p-4 ${
                      message.role === "user" ? "bg-purple-600 text-white" : "bg-white border"
                    }`}
                  >
                    <div className="flex items-center gap-2 mb-1">
                      {message.role === "assistant" ? <Bot className="h-4 w-4" /> : <User className="h-4 w-4" />}
                      <span className="text-xs font-medium">{message.role === "assistant" ? agent.name : "Você"}</span>
                      <span className="text-xs opacity-70">{formatTimestamp(message.timestamp)}</span>
                    </div>
                    <div className="whitespace-pre-wrap">{message.content}</div>
                  </div>
                </div>
              ))
          )}

          {isProcessing && (
            <div className="flex justify-start">
              <div className="max-w-[80%] rounded-lg p-4 bg-white border">
                <div className="flex items-center gap-2">
                  <Bot className="h-4 w-4" />
                  <span className="text-xs font-medium">{agent.name}</span>
                  <Loader2 className="h-3 w-3 animate-spin" />
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      <div className="p-4 border-t bg-white">
        <div className="max-w-3xl mx-auto">
          <form
            onSubmit={(e) => {
              e.preventDefault()
              handleSendMessage()
            }}
            className="flex flex-col gap-2"
          >
            <Textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={`Envie uma mensagem para ${agent.name}...`}
              className="min-h-[100px] resize-none"
              disabled={isProcessing}
            />
            <div className="flex justify-end">
              <Button
                type="submit"
                className="bg-purple-600 hover:bg-purple-700"
                disabled={!input.trim() || isProcessing}
              >
                {isProcessing ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Processando...
                  </>
                ) : (
                  <>
                    <Send className="mr-2 h-4 w-4" />
                    Enviar
                  </>
                )}
              </Button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}
