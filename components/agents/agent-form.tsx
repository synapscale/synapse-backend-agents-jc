"use client"

import { useState, useCallback } from "react"
import { useRouter } from "next/navigation"
import { AgentFormHeader } from "./agent-form-header"
import { AgentBasicInfo } from "./agent-basic-info"
import { AgentPromptTab } from "./agent-prompt-tab"
import { AgentParametersTab } from "./agent-parameters-tab"
import { AgentConnectionsTab } from "./agent-connections-tab"
import { AgentFormActions } from "./agent-form-actions"
import { toast } from "@/components/ui/use-toast"
import type { Agent } from "@/types/agent-types"

/**
 * Componente principal para o formulário de criação/edição de agentes
 * 
 * Este componente gerencia o formulário completo de agentes com todas as abas e funcionalidades.
 */
export function AgentForm({ agentId }: { agentId?: string }) {
  const router = useRouter()
  const isNewAgent = !agentId
  
  // Estado para as abas
  const [activeTab, setActiveTab] = useState("basic")
  
  // Estado para o formulário
  const [formValues, setFormValues] = useState({
    name: "",
    description: "",
    type: "chat",
    model: "gpt-4",
    status: "draft",
    systemMessage: "",
    examples: "",
    temperature: 0.7,
    maxTokens: 1000,
    topP: 0.9,
    frequencyPenalty: 0,
    presencePenalty: 0,
    stopSequences: "",
    agents: [],
    urls: [],
  })
  
  // Estado para erros de validação
  const [errors, setErrors] = useState<Record<string, string>>({})
  
  // Estado para indicar salvamento em progresso
  const [isSaving, setIsSaving] = useState(false)
  
  // Handlers para mudanças nos campos
  const handleChange = useCallback((field: string, value: any) => {
    setFormValues((prev) => ({ ...prev, [field]: value }))
    
    // Limpa o erro quando o campo é alterado
    if (errors[field]) {
      setErrors((prev) => {
        const newErrors = { ...prev }
        delete newErrors[field]
        return newErrors
      })
    }
  }, [errors])
  
  // Validação do formulário
  const validateForm = useCallback(() => {
    const newErrors: Record<string, string> = {}
    
    if (!formValues.name.trim()) {
      newErrors.name = "O nome do agente é obrigatório"
    }
    
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }, [formValues])
  
  // Handler para salvar o agente
  const handleSave = useCallback(async () => {
    if (!validateForm()) {
      toast({
        title: "Erro de validação",
        description: "Por favor, corrija os erros no formulário antes de salvar.",
        variant: "destructive",
      })
      return
    }
    
    setIsSaving(true)
    
    try {
      // Simulação de salvamento
      await new Promise((resolve) => setTimeout(resolve, 1000))
      
      toast({
        title: "Agente salvo",
        description: `O agente "${formValues.name}" foi salvo com sucesso.`,
      })
      
      // Redireciona para a lista de agentes
      router.push("/agentes")
    } catch (error) {
      toast({
        title: "Erro ao salvar",
        description: "Ocorreu um erro ao salvar o agente. Tente novamente.",
        variant: "destructive",
      })
    } finally {
      setIsSaving(false)
    }
  }, [formValues, validateForm, router])
  
  // Handler para cancelar a edição
  const handleCancel = useCallback(() => {
    router.push("/agentes")
  }, [router])
  
  // Handlers para as abas de conexões
  const handleAddAgent = useCallback(() => {
    // Implementação para adicionar agente relacionado
    console.log("Adicionar agente relacionado")
  }, [])
  
  const handleRemoveAgent = useCallback((id: string) => {
    // Implementação para remover agente relacionado
    console.log("Remover agente relacionado", id)
  }, [])
  
  const handleAddUrl = useCallback(() => {
    // Implementação para adicionar URL
    console.log("Adicionar URL")
  }, [])
  
  const handleRemoveUrl = useCallback((id: string) => {
    // Implementação para remover URL
    console.log("Remover URL", id)
  }, [])
  
  return (
    <div className="space-y-6">
      {/* Cabeçalho do formulário */}
      <AgentFormHeader
        title={isNewAgent ? "Criar Novo Agente" : "Editar Agente"}
        subtitle={isNewAgent ? "Configure seu novo agente de IA" : "Atualize as configurações do seu agente"}
        activeTab={activeTab}
        onTabChange={setActiveTab}
      />
      
      {/* Conteúdo das abas */}
      <div className="space-y-6">
        {/* Aba de informações básicas */}
        {activeTab === "basic" && (
          <AgentBasicInfo
            name={formValues.name}
            type={formValues.type}
            model={formValues.model}
            description={formValues.description}
            status={formValues.status}
            onChangeName={(value) => handleChange("name", value)}
            onChangeType={(value) => handleChange("type", value)}
            onChangeModel={(value) => handleChange("model", value)}
            onChangeDescription={(value) => handleChange("description", value)}
            onChangeStatus={(value) => handleChange("status", value)}
            onBlurName={() => validateForm()}
            nameError={errors.name}
            isNewAgent={isNewAgent}
          />
        )}
        
        {/* Aba de prompt */}
        {activeTab === "prompt" && (
          <AgentPromptTab
            systemMessage={formValues.systemMessage}
            examples={formValues.examples}
            onChangeSystemMessage={(value) => handleChange("systemMessage", value)}
            onChangeExamples={(value) => handleChange("examples", value)}
          />
        )}
        
        {/* Aba de parâmetros */}
        {activeTab === "parameters" && (
          <AgentParametersTab
            temperature={formValues.temperature}
            maxTokens={formValues.maxTokens}
            topP={formValues.topP}
            frequencyPenalty={formValues.frequencyPenalty}
            presencePenalty={formValues.presencePenalty}
            stopSequences={formValues.stopSequences}
            onChangeTemperature={(value) => handleChange("temperature", value)}
            onChangeMaxTokens={(value) => handleChange("maxTokens", value)}
            onChangeTopP={(value) => handleChange("topP", value)}
            onChangeFrequencyPenalty={(value) => handleChange("frequencyPenalty", value)}
            onChangePresencePenalty={(value) => handleChange("presencePenalty", value)}
            onChangeStopSequences={(value) => handleChange("stopSequences", value)}
          />
        )}
        
        {/* Aba de conexões */}
        {activeTab === "connections" && (
          <AgentConnectionsTab
            agents={formValues.agents}
            urls={formValues.urls}
            onAddAgent={handleAddAgent}
            onRemoveAgent={handleRemoveAgent}
            onAddUrl={handleAddUrl}
            onRemoveUrl={handleRemoveUrl}
          />
        )}
      </div>
      
      {/* Ações do formulário */}
      <AgentFormActions
        onSave={handleSave}
        onCancel={handleCancel}
        isSaving={isSaving}
        isValid={Object.keys(errors).length === 0}
      />
    </div>
  )
}
