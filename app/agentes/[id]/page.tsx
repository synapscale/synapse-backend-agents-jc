"use client"

import { useCallback, useMemo, useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { toast } from "@/components/ui/use-toast"
import { AgentFormHeader } from "@/components/agents/agent-form-header"
import { TemplatesModal } from "@/components/templates-modal"
import { useForm } from "@/hooks/use-form"
import { useDisclosure } from "@/hooks/use-disclosure"
import { useLocalStorage } from "@/hooks/use-local-storage"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { AgentBasicInfo } from "@/components/agents/agent-basic-info"
import { AgentPromptTab } from "@/components/agents/agent-prompt-tab"
import { AgentParametersTab } from "@/components/agents/agent-parameters-tab"
import { AgentConnectionsTab } from "@/components/agents/agent-connections-tab"
import { AgentFormActions } from "@/components/agents/agent-form-actions"
import { AgentFormLoading } from "@/components/agents/agent-form-loading"
import { AgentNotFound } from "@/components/agents/agent-not-found"
import { UnsavedChangesDialog } from "@/components/agents/unsaved-changes-dialog"
import { validateAgentForm } from "@/utils/form-validation"
import { DEFAULT_PROMPT } from "@/constants/agent-constants"
import type { Agent, AgentFormData } from "@/types/agent-types"

export default function AgentePage({ params }: { params: { id: string } }) {
  const router = useRouter()
  const isNewAgent = params.id === "novo"

  // State for loading
  const [isLoading, setIsLoading] = useState(true)

  // State for unsaved changes
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false)
  const [showUnsavedDialog, setShowUnsavedDialog] = useState(false)
  const [pendingAction, setPendingAction] = useState<"navigate" | "reset" | null>(null)

  // State for active tab
  const [activeTab, setActiveTab] = useState("prompt")

  // Get agents from local storage
  const [agents, setAgents] = useLocalStorage<Agent[]>("agents", [])

  // Estado do modal de templates
  const templatesModal = useDisclosure()

  // Find existing agent if editing
  const existingAgent = useMemo(() => {
    if (isNewAgent) return null
    return agents.find((agent) => agent.id === params.id)
  }, [agents, isNewAgent, params.id])

  // Inicializar o formulário com valores padrão ou existentes
  const initialValues: AgentFormData = useMemo(() => {
    if (isNewAgent) {
      return {
        id: Date.now().toString(),
        name: "",
        type: "chat",
        prompt: DEFAULT_PROMPT,
        model: "gpt-4o",
        status: "draft",
        description: "",
        maxTokens: 2048,
        temperature: 0.7,
        topP: 1,
        frequencyPenalty: 0,
        presencePenalty: 0,
        stopSequences: [],
        userDecision: false,
        urls: [],
        agents: [],
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      }
    } else if (existingAgent) {
      // Convert existing agent to full AgentFormData
      return {
        ...existingAgent,
        prompt: existingAgent.prompt || DEFAULT_PROMPT,
        status: existingAgent.status || "active",
        description: existingAgent.description || "",
        maxTokens: existingAgent.maxTokens || 2048,
        temperature: existingAgent.temperature || 0.7,
        topP: existingAgent.topP || 1,
        frequencyPenalty: existingAgent.frequencyPenalty || 0,
        presencePenalty: existingAgent.presencePenalty || 0,
        stopSequences: existingAgent.stopSequences || [],
        userDecision: existingAgent.userDecision || false,
        urls: existingAgent.urls || [],
        agents: existingAgent.agents || [],
      }
    } else {
      // Fallback for when agent is not found
      return {
        id: params.id,
        name: "Agente não encontrado",
        type: "chat",
        prompt: "Agente não encontrado",
        model: "gpt-4o",
        status: "draft",
        description: "",
        maxTokens: 2048,
        temperature: 0.7,
        topP: 1,
        frequencyPenalty: 0,
        presencePenalty: 0,
        stopSequences: [],
        userDecision: false,
        urls: [],
        agents: [],
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      }
    }
  }, [isNewAgent, existingAgent, params.id])

  // Simulate loading state
  useEffect(() => {
    const timer = setTimeout(() => {
      setIsLoading(false)
    }, 800)

    return () => clearTimeout(timer)
  }, [])

  // Check for unsaved changes
  useEffect(() => {
    const handleBeforeUnload = (e: BeforeUnloadEvent) => {
      if (hasUnsavedChanges) {
        e.preventDefault()
        e.returnValue = ""
        return ""
      }
    }

    window.addEventListener("beforeunload", handleBeforeUnload)
    return () => window.removeEventListener("beforeunload", handleBeforeUnload)
  }, [hasUnsavedChanges])

  // Manipulador de envio do formulário
  const handleSubmitForm = useCallback(
    async (values: AgentFormData) => {
      try {
        // Update timestamps
        const now = new Date().toISOString()
        const updatedAgent: Agent = {
          ...values,
          updatedAt: now,
          createdAt: values.createdAt || now,
        }

        // Update agents in local storage
        setAgents((prev) => {
          if (isNewAgent) {
            return [...prev, updatedAgent]
          } else {
            return prev.map((agent) => (agent.id === updatedAgent.id ? updatedAgent : agent))
          }
        })

        // Reset unsaved changes flag
        setHasUnsavedChanges(false)

        // Show success toast
        toast({
          title: isNewAgent ? "Agente criado com sucesso!" : "Alterações salvas com sucesso!",
          description: isNewAgent
            ? "Seu novo agente foi criado e está pronto para uso."
            : "As alterações no agente foram salvas.",
          duration: 3000,
        })

        // Redirect to agents list
        router.push("/agentes")
      } catch (error) {
        toast({
          title: "Erro ao salvar",
          description: "Ocorreu um erro ao salvar o agente. Tente novamente.",
          variant: "destructive",
          duration: 3000,
        })
        throw error
      }
    },
    [isNewAgent, router, setAgents],
  )

  // Usar o hook de formulário
  const form = useForm<AgentFormData>({
    initialValues,
    onSubmit: handleSubmitForm,
    validate: validateAgentForm,
    validateOnBlur: true,
    onChange: () => setHasUnsavedChanges(true),
  })

  // Handle back navigation with unsaved changes
  const handleBack = useCallback(() => {
    if (hasUnsavedChanges) {
      setPendingAction("navigate")
      setShowUnsavedDialog(true)
    } else {
      router.push("/agentes")
    }
  }, [hasUnsavedChanges, router])

  // Handle form reset with unsaved changes
  const handleReset = useCallback(() => {
    if (hasUnsavedChanges) {
      setPendingAction("reset")
      setShowUnsavedDialog(true)
    } else {
      form.reset()
    }
  }, [hasUnsavedChanges, form])

  // Confirm pending action
  const confirmPendingAction = useCallback(() => {
    if (pendingAction === "navigate") {
      router.push("/agentes")
    } else if (pendingAction === "reset") {
      form.reset()
      setHasUnsavedChanges(false)
    }

    setShowUnsavedDialog(false)
    setPendingAction(null)
  }, [pendingAction, router, form])

  // Manipuladores para adicionar URLs e agentes
  const addUrl = useCallback(() => {
    form.setValues((prev) => {
      const newId = Date.now().toString()
      return {
        ...prev,
        urls: [...prev.urls, { id: newId, label: `URL ${prev.urls.length + 1}` }],
      }
    })
  }, [form])

  const addAgent = useCallback(() => {
    form.setValues((prev) => {
      const newId = Date.now().toString()
      return {
        ...prev,
        agents: [...prev.agents, { id: newId, label: `AGENTE ${prev.agents.length + 1}` }],
      }
    })
  }, [form])

  // Manipulador para remover URLs
  const removeUrl = useCallback(
    (id: string) => {
      form.setValues((prev) => ({
        ...prev,
        urls: prev.urls.filter((url) => url.id !== id),
      }))
    },
    [form],
  )

  // Manipulador para remover agentes
  const removeAgent = useCallback(
    (id: string) => {
      form.setValues((prev) => ({
        ...prev,
        agents: prev.agents.filter((agent) => agent.id !== id),
      }))
    },
    [form],
  )

  // Manipulador para selecionar um template
  const handleSelectTemplate = useCallback(
    (template: any) => {
      form.handleChange("prompt", template.content)
      templatesModal.close()
    },
    [form, templatesModal],
  )

  // Título dinâmico para o cabeçalho
  const headerTitle = useMemo(() => {
    if (isLoading) return isNewAgent ? "Novo Agente" : "Carregando..."
    return isNewAgent ? "Novo Agente" : `Editar: ${form.values.name}`
  }, [isNewAgent, isLoading, form.values.name])

  // Render loading state
  if (isLoading) {
    return <AgentFormLoading />
  }

  // If agent not found and not creating new
  if (!isNewAgent && !existingAgent) {
    return <AgentNotFound />
  }

  return (
    <div className="flex flex-col w-full h-full bg-gray-50/50">
      {/* Cabeçalho do formulário */}
      <AgentFormHeader
        isNewAgent={isNewAgent}
        isSubmitting={form.isSubmitting}
        onSubmit={form.handleSubmit}
        onOpenTemplates={templatesModal.open}
        isValid={form.isValid}
        title={headerTitle}
        onBack={handleBack}
      />

      {/* Conteúdo principal */}
      <main className="flex-1 p-3 sm:p-4 md:p-6 overflow-auto">
        <div className="max-w-5xl mx-auto">
          <form className="space-y-4 sm:space-y-6" onSubmit={(e) => form.handleSubmit(e)}>
            {/* Seção de detalhes do agente */}
            <AgentBasicInfo
              name={form.values.name}
              type={form.values.type}
              model={form.values.model}
              description={form.values.description}
              status={form.values.status}
              onChangeName={(value) => form.handleChange("name", value)}
              onChangeType={(value) => form.handleChange("type", value)}
              onChangeModel={(value) => form.handleChange("model", value)}
              onChangeDescription={(value) => form.handleChange("description", value)}
              onChangeStatus={(value) => form.handleChange("status", value as "active" | "draft" | "archived")}
              onBlurName={() => form.handleBlur("name")}
              nameError={form.touched.name ? form.errors.name : undefined}
              isNewAgent={isNewAgent}
            />

            {/* Tabs para diferentes seções */}
            <Tabs value={activeTab} onValueChange={setActiveTab} className="mt-6">
              <TabsList className="mb-4 grid w-full grid-cols-3 md:w-auto md:inline-flex">
                <TabsTrigger
                  value="prompt"
                  className="data-[state=active]:bg-purple-50 data-[state=active]:text-purple-900"
                >
                  Prompt
                </TabsTrigger>
                <TabsTrigger
                  value="parameters"
                  className="data-[state=active]:bg-purple-50 data-[state=active]:text-purple-900"
                >
                  Parâmetros
                </TabsTrigger>
                <TabsTrigger
                  value="connections"
                  className="data-[state=active]:bg-purple-50 data-[state=active]:text-purple-900"
                >
                  Conexões
                </TabsTrigger>
              </TabsList>

              <TabsContent value="prompt" className="focus-visible:outline-none focus-visible:ring-0">
                <AgentPromptTab
                  prompt={form.values.prompt}
                  onChangePrompt={(value) => form.handleChange("prompt", value)}
                  onBlurPrompt={() => form.handleBlur("prompt")}
                  promptError={form.touched.prompt ? form.errors.prompt : undefined}
                  onOpenTemplates={templatesModal.open}
                />
              </TabsContent>

              <TabsContent value="parameters" className="focus-visible:outline-none focus-visible:ring-0">
                <AgentParametersTab
                  maxTokens={form.values.maxTokens?.toString() || ""}
                  temperature={form.values.temperature?.toString() || ""}
                  topP={form.values.topP?.toString() || ""}
                  frequencyPenalty={form.values.frequencyPenalty?.toString() || ""}
                  presencePenalty={form.values.presencePenalty?.toString() || ""}
                  userDecision={form.values.userDecision}
                  onChangeMaxTokens={(value) => form.handleChange("maxTokens", Number.parseInt(value) || undefined)}
                  onChangeTemperature={(value) =>
                    form.handleChange("temperature", Number.parseFloat(value) || undefined)
                  }
                  onChangeTopP={(value) => form.handleChange("topP", Number.parseFloat(value) || undefined)}
                  onChangeFrequencyPenalty={(value) =>
                    form.handleChange("frequencyPenalty", Number.parseFloat(value) || undefined)
                  }
                  onChangePresencePenalty={(value) =>
                    form.handleChange("presencePenalty", Number.parseFloat(value) || undefined)
                  }
                  onChangeUserDecision={(checked) => form.handleChange("userDecision", checked)}
                  onBlurMaxTokens={() => form.handleBlur("maxTokens")}
                  onBlurTemperature={() => form.handleBlur("temperature")}
                  onBlurTopP={() => form.handleBlur("topP")}
                  onBlurFrequencyPenalty={() => form.handleBlur("frequencyPenalty")}
                  onBlurPresencePenalty={() => form.handleBlur("presencePenalty")}
                  maxTokensError={form.touched.maxTokens ? form.errors.maxTokens : undefined}
                  temperatureError={form.touched.temperature ? form.errors.temperature : undefined}
                  topPError={form.touched.topP ? form.errors.topP : undefined}
                  frequencyPenaltyError={form.touched.frequencyPenalty ? form.errors.frequencyPenalty : undefined}
                  presencePenaltyError={form.touched.presencePenalty ? form.errors.presencePenalty : undefined}
                />
              </TabsContent>

              <TabsContent value="connections" className="focus-visible:outline-none focus-visible:ring-0">
                <AgentConnectionsTab
                  agents={form.values.agents}
                  urls={form.values.urls}
                  onAddAgent={addAgent}
                  onRemoveAgent={removeAgent}
                  onAddUrl={addUrl}
                  onRemoveUrl={removeUrl}
                />
              </TabsContent>
            </Tabs>

            {/* Botões de ação */}
            <AgentFormActions
              onReset={handleReset}
              isSubmitting={form.isSubmitting}
              isValid={form.isValid}
              hasUnsavedChanges={hasUnsavedChanges}
              isNewAgent={isNewAgent}
            />
          </form>
        </div>
      </main>

      {/* Modal de templates */}
      <TemplatesModal
        isOpen={templatesModal.isOpen}
        onClose={templatesModal.close}
        onSelectTemplate={handleSelectTemplate}
        currentPrompt={form.values.prompt}
      />

      {/* Dialog for unsaved changes */}
      <UnsavedChangesDialog
        open={showUnsavedDialog}
        onOpenChange={setShowUnsavedDialog}
        onConfirm={confirmPendingAction}
      />
    </div>
  )
}
