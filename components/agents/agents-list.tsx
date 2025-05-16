"use client"

import { useState, useCallback } from "react"
import { useRouter } from "next/navigation"
import { AgentCard } from "./agent-card"
import { AgentListHeader } from "./agent-list-header"
import { AgentListFilters } from "./agent-list-filters"
import { AgentListEmpty } from "./agent-list-empty"
import { AgentDeleteDialog } from "./agent-delete-dialog"
import { toast } from "@/components/ui/use-toast"
import type { Agent } from "@/types/agent-types"

/**
 * Componente principal para a página de listagem de agentes
 * 
 * Este componente gerencia a exibição, filtragem e ações para a lista de agentes.
 */
export function AgentsList() {
  const router = useRouter()
  
  // Estado para armazenar a lista de agentes
  const [agents, setAgents] = useState<Agent[]>([
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
  ])
  
  // Estado para filtros e busca
  const [searchQuery, setSearchQuery] = useState("")
  const [statusFilter, setStatusFilter] = useState<string[]>([])
  const [typeFilter, setTypeFilter] = useState<string[]>([])
  
  // Estado para agente a ser excluído
  const [agentToDelete, setAgentToDelete] = useState<Agent | null>(null)
  
  // Filtra os agentes com base nos critérios de busca e filtros
  const filteredAgents = agents.filter((agent) => {
    // Filtro de busca
    const matchesSearch = 
      searchQuery === "" || 
      agent.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      agent.description?.toLowerCase().includes(searchQuery.toLowerCase());
    
    // Filtro de status
    const matchesStatus = 
      statusFilter.length === 0 || 
      statusFilter.includes(agent.status);
    
    // Filtro de tipo
    const matchesType = 
      typeFilter.length === 0 || 
      typeFilter.includes(agent.type);
    
    return matchesSearch && matchesStatus && matchesType;
  })
  
  // Formata a data para exibição
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('pt-BR')
  }
  
  // Handlers para ações de agentes
  const handleCreateNew = useCallback(() => {
    router.push("/agentes/novo")
  }, [router])
  
  const handleDuplicate = useCallback((agent: Agent) => {
    const newAgent = {
      ...agent,
      id: `${Date.now()}`,
      name: `${agent.name} (Cópia)`,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    }
    
    setAgents((prev) => [...prev, newAgent])
    
    toast({
      title: "Agente duplicado",
      description: `O agente "${agent.name}" foi duplicado com sucesso.`,
    })
  }, [])
  
  const handleDelete = useCallback((agent: Agent) => {
    setAgentToDelete(agent)
  }, [])
  
  const confirmDelete = useCallback(() => {
    if (!agentToDelete) return
    
    setAgents((prev) => prev.filter((agent) => agent.id !== agentToDelete.id))
    
    toast({
      title: "Agente excluído",
      description: `O agente "${agentToDelete.name}" foi excluído com sucesso.`,
    })
    
    setAgentToDelete(null)
  }, [agentToDelete])
  
  return (
    <div className="space-y-6">
      {/* Cabeçalho da lista */}
      <AgentListHeader 
        title="Meus Agentes" 
        subtitle="Gerencie seus agentes de IA"
        onCreateNew={handleCreateNew}
      />
      
      {/* Filtros */}
      <AgentListFilters
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        statusFilter={statusFilter}
        onStatusFilterChange={setStatusFilter}
        typeFilter={typeFilter}
        onTypeFilterChange={setTypeFilter}
      />
      
      {/* Lista de agentes */}
      {filteredAgents.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredAgents.map((agent) => (
            <AgentCard
              key={agent.id}
              agent={agent}
              onDuplicate={handleDuplicate}
              onDelete={handleDelete}
              formatDate={formatDate}
            />
          ))}
        </div>
      ) : (
        <AgentListEmpty onCreateNew={handleCreateNew} />
      )}
      
      {/* Diálogo de confirmação de exclusão */}
      <AgentDeleteDialog
        agent={agentToDelete}
        onOpenChange={(open) => !open && setAgentToDelete(null)}
        onConfirm={confirmDelete}
      />
    </div>
  )
}
