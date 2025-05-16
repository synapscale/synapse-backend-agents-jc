"use client"

import { createContext, useContext, useState, useCallback, useEffect } from "react"
import { toast } from "@/components/ui/use-toast"
import type { Agent } from "@/types/agent-types"

// Definição do contexto para os agentes
interface AgentsContextType {
  agents: Agent[]
  addAgent: (agent: Omit<Agent, "id" | "createdAt" | "updatedAt">) => void
  updateAgent: (id: string, agent: Partial<Omit<Agent, "id" | "createdAt" | "updatedAt">>) => void
  deleteAgent: (id: string) => void
  getAgentById: (id: string) => Agent | undefined
  isLoading: boolean
}

// Criação do contexto
const AgentsContext = createContext<AgentsContextType | undefined>(undefined)

// Hook para usar o contexto
export function useAgents() {
  const context = useContext(AgentsContext)
  if (!context) {
    throw new Error("useAgents deve ser usado dentro de um AgentsProvider")
  }
  return context
}

// Provider do contexto
export function AgentsProvider({ children }: { children: React.ReactNode }) {
  // Estado para armazenar os agentes
  const [agents, setAgents] = useState<Agent[]>([])
  
  // Estado para controlar o carregamento
  const [isLoading, setIsLoading] = useState(true)
  
  // Carregar agentes ao iniciar
  useEffect(() => {
    const loadAgents = async () => {
      try {
        // Simulação de carregamento de dados
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        // Dados de exemplo
        const exampleAgents: Agent[] = [
          {
            id: "1",
            name: "Assistente de Atendimento",
            description: "Agente para atendimento ao cliente",
            model: "gpt-4",
            type: "chat",
            status: "active",
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
          },
          {
            id: "2",
            name: "Gerador de Conteúdo",
            description: "Agente para criação de conteúdo de marketing",
            model: "gpt-3.5-turbo",
            type: "texto",
            status: "draft",
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
          },
        ]
        
        setAgents(exampleAgents)
      } catch (error) {
        console.error("Erro ao carregar agentes:", error)
        toast({
          title: "Erro ao carregar agentes",
          description: "Não foi possível carregar os agentes. Tente novamente mais tarde.",
          variant: "destructive",
        })
      } finally {
        setIsLoading(false)
      }
    }
    
    loadAgents()
  }, [])
  
  // Adicionar um novo agente
  const addAgent = useCallback((agentData: Omit<Agent, "id" | "createdAt" | "updatedAt">) => {
    const now = new Date().toISOString()
    const newAgent: Agent = {
      ...agentData,
      id: `agent-${Date.now()}`,
      createdAt: now,
      updatedAt: now,
    }
    
    setAgents(prev => [...prev, newAgent])
    return newAgent
  }, [])
  
  // Atualizar um agente existente
  const updateAgent = useCallback((id: string, agentData: Partial<Omit<Agent, "id" | "createdAt" | "updatedAt">>) => {
    setAgents(prev => 
      prev.map(agent => 
        agent.id === id 
          ? { 
              ...agent, 
              ...agentData, 
              updatedAt: new Date().toISOString() 
            } 
          : agent
      )
    )
  }, [])
  
  // Excluir um agente
  const deleteAgent = useCallback((id: string) => {
    setAgents(prev => prev.filter(agent => agent.id !== id))
  }, [])
  
  // Obter um agente pelo ID
  const getAgentById = useCallback((id: string) => {
    return agents.find(agent => agent.id === id)
  }, [agents])
  
  // Valor do contexto
  const value = {
    agents,
    addAgent,
    updateAgent,
    deleteAgent,
    getAgentById,
    isLoading,
  }
  
  return <AgentsContext.Provider value={value}>{children}</AgentsContext.Provider>
}
