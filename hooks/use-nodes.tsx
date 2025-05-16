"use client"

import { createContext, useContext, useState, useCallback, useEffect } from "react"
import { toast } from "@/components/ui/use-toast"
import type { Node } from "@/types/node-types"

// Definição do contexto para os nodes
interface NodesContextType {
  nodes: Node[]
  addNode: (node: Omit<Node, "id" | "createdAt" | "updatedAt">) => void
  updateNode: (id: string, node: Partial<Omit<Node, "id" | "createdAt" | "updatedAt">>) => void
  deleteNode: (id: string) => void
  getNodeById: (id: string) => Node | undefined
  isLoading: boolean
}

// Criação do contexto
const NodesContext = createContext<NodesContextType | undefined>(undefined)

// Hook para usar o contexto
export function useNodes() {
  const context = useContext(NodesContext)
  if (!context) {
    throw new Error("useNodes deve ser usado dentro de um NodesProvider")
  }
  return context
}

// Provider do contexto
export function NodesProvider({ children }: { children: React.ReactNode }) {
  // Estado para armazenar os nodes
  const [nodes, setNodes] = useState<Node[]>([])
  
  // Estado para controlar o carregamento
  const [isLoading, setIsLoading] = useState(true)
  
  // Carregar nodes ao iniciar
  useEffect(() => {
    const loadNodes = async () => {
      try {
        // Simulação de carregamento de dados
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        // Dados de exemplo
        const exampleNodes: Node[] = [
          {
            id: "1",
            name: "Processador de Texto",
            description: "Processa texto usando técnicas de NLP",
            category: "processing",
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
          },
          {
            id: "2",
            name: "Gerador de Imagens",
            description: "Gera imagens a partir de descrições textuais",
            category: "ai",
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
          },
        ]
        
        setNodes(exampleNodes)
      } catch (error) {
        console.error("Erro ao carregar nodes:", error)
        toast({
          title: "Erro ao carregar nodes",
          description: "Não foi possível carregar os nodes. Tente novamente mais tarde.",
          variant: "destructive",
        })
      } finally {
        setIsLoading(false)
      }
    }
    
    loadNodes()
  }, [])
  
  // Adicionar um novo node
  const addNode = useCallback((nodeData: Omit<Node, "id" | "createdAt" | "updatedAt">) => {
    const now = new Date().toISOString()
    const newNode: Node = {
      ...nodeData,
      id: `node-${Date.now()}`,
      createdAt: now,
      updatedAt: now,
    }
    
    setNodes(prev => [...prev, newNode])
    return newNode
  }, [])
  
  // Atualizar um node existente
  const updateNode = useCallback((id: string, nodeData: Partial<Omit<Node, "id" | "createdAt" | "updatedAt">>) => {
    setNodes(prev => 
      prev.map(node => 
        node.id === id 
          ? { 
              ...node, 
              ...nodeData, 
              updatedAt: new Date().toISOString() 
            } 
          : node
      )
    )
  }, [])
  
  // Excluir um node
  const deleteNode = useCallback((id: string) => {
    setNodes(prev => prev.filter(node => node.id !== id))
  }, [])
  
  // Obter um node pelo ID
  const getNodeById = useCallback((id: string) => {
    return nodes.find(node => node.id === id)
  }, [nodes])
  
  // Valor do contexto
  const value = {
    nodes,
    addNode,
    updateNode,
    deleteNode,
    getNodeById,
    isLoading,
  }
  
  return <NodesContext.Provider value={value}>{children}</NodesContext.Provider>
}
