"use client"

import { useState, useEffect, useMemo } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { ArrowLeft, Edit, Copy, Trash2, AlertCircle, CheckCircle2, MessageSquare } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Section } from "@/components/ui/section"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Skeleton } from "@/components/ui/skeleton"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog"
import { toast } from "@/components/ui/use-toast"
import { useLocalStorage } from "@/hooks/use-local-storage"
import { cn } from "@/lib/utils"

// Define the Agent interface
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

export default function AgentViewPage({ params }: { params: { id: string } }) {
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(true)
  const [agents, setAgents] = useLocalStorage<Agent[]>("agents", [])
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)

  // Find the agent
  const agent = useMemo(() => {
    return agents.find((a) => a.id === params.id)
  }, [agents, params.id])

  // Simulate loading
  useEffect(() => {
    const timer = setTimeout(() => {
      setIsLoading(false)
    }, 1000)

    return () => clearTimeout(timer)
  }, [])

  // Handle delete
  const handleDelete = () => {
    setAgents((prev) => prev.filter((a) => a.id !== params.id))
    toast({
      title: "Agente excluído",
      description: "O agente foi removido com sucesso.",
      variant: "default",
    })
    router.push("/agentes")
  }

  // Handle duplicate
  const handleDuplicate = () => {
    if (!agent) return

    const newAgent: Agent = {
      ...agent,
      id: Date.now().toString(),
      name: `${agent.name} (Cópia)`,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      status: "draft",
    }

    setAgents((prev) => [...prev, newAgent])
    toast({
      title: "Agente duplicado",
      description: "Uma cópia do agente foi criada com sucesso.",
    })
    router.push(`/agentes/${newAgent.id}/view`)
  }

  // Handle archive/unarchive
  const handleToggleArchive = () => {
    if (!agent) return

    setAgents((prev) =>
      prev.map((a) =>
        a.id === agent.id
          ? {
              ...a,
              status: a.status === "archived" ? "active" : "archived",
              updatedAt: new Date().toISOString(),
            }
          : a,
      ),
    )

    toast({
      title: agent.status === "archived" ? "Agente ativado" : "Agente arquivado",
      description:
        agent.status === "archived"
          ? "O agente foi movido para ativos."
          : "O agente foi arquivado e não aparecerá nas listas padrão.",
    })
  }

  // Format date
  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return new Intl.DateTimeFormat("pt-BR", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    }).format(date)
  }

  // Get status badge
  const getStatusBadge = (status?: string) => {
    switch (status) {
      case "active":
        return (
          <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">
            <CheckCircle2 className="mr-1 h-3 w-3" />
            Ativo
          </Badge>
        )
      case "draft":
        return (
          <Badge variant="outline" className="bg-yellow-50 text-yellow-700 border-yellow-200">
            <Edit className="mr-1 h-3 w-3" />
            Rascunho
          </Badge>
        )
      case "archived":
        return (
          <Badge variant="outline" className="bg-gray-50 text-gray-700 border-gray-200">
            <AlertCircle className="mr-1 h-3 w-3" />
            Arquivado
          </Badge>
        )
      default:
        return null
    }
  }

  // Loading state
  if (isLoading) {
    return (
      <div className="p-4 md:p-6">
        <div className="max-w-5xl mx-auto">
          <div className="flex items-center gap-2 mb-6">
            <Skeleton className="h-9 w-24" />
            <div className="w-px h-6 bg-gray-200" aria-hidden="true"></div>
            <Skeleton className="h-8 w-64" />
          </div>

          <div className="flex justify-between items-center mb-6">
            <div className="flex items-center gap-2">
              <Skeleton className="h-6 w-20" />
              <Skeleton className="h-6 w-16" />
              <Skeleton className="h-6 w-24" />
            </div>
            <div className="flex gap-2">
              <Skeleton className="h-9 w-24" />
              <Skeleton className="h-9 w-24" />
              <Skeleton className="h-9 w-24" />
            </div>
          </div>

          <Skeleton className="h-10 w-full mb-6" />

          <Skeleton className="h-64 w-full mb-6" />

          <Skeleton className="h-32 w-full" />
        </div>
      </div>
    )
  }

  // Agent not found
  if (!agent) {
    return (
      <div className="p-4 md:p-6">
        <div className="max-w-5xl mx-auto">
          <div className="flex items-center gap-2 mb-6">
            <Link href="/agentes" className="flex items-center text-gray-500 hover:text-gray-900">
              <ArrowLeft className="mr-1 h-4 w-4" />
              Voltar
            </Link>
            <div className="w-px h-6 bg-gray-200" aria-hidden="true"></div>
            <h1 className="text-xl font-bold">Agente não encontrado</h1>
          </div>

          <div className="text-center py-12 border rounded-lg bg-muted/20">
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
    <div className="p-4 md:p-6">
      <div className="max-w-5xl mx-auto">
        <div className="flex items-center gap-2 mb-6">
          <Link href="/agentes" className="flex items-center text-gray-500 hover:text-gray-900">
            <ArrowLeft className="mr-1 h-4 w-4" />
            Voltar
          </Link>
          <div className="w-px h-6 bg-gray-200" aria-hidden="true"></div>
          <h1 className="text-xl font-bold truncate">{agent.name}</h1>
        </div>

        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
          <div className="flex flex-wrap items-center gap-2">
            {getStatusBadge(agent.status)}
            <Badge variant="outline" className="bg-muted/30">
              {agent.type}
            </Badge>
            <Badge variant="outline" className="bg-muted/30">
              {agent.model}
            </Badge>
          </div>

          <div className="flex flex-wrap gap-2">
            <Button variant="outline" size="sm" className="h-9" onClick={handleToggleArchive}>
              {agent.status === "archived" ? (
                <>
                  <CheckCircle2 className="mr-1.5 h-4 w-4" />
                  Ativar
                </>
              ) : (
                <>
                  <AlertCircle className="mr-1.5 h-4 w-4" />
                  Arquivar
                </>
              )}
            </Button>

            <Button variant="outline" size="sm" className="h-9" onClick={handleDuplicate}>
              <Copy className="mr-1.5 h-4 w-4" />
              Duplicar
            </Button>

            <Link href={`/agentes/${agent.id}`}>
              <Button variant="outline" size="sm" className="h-9">
                <Edit className="mr-1.5 h-4 w-4" />
                Editar
              </Button>
            </Link>

            <Button
              variant="outline"
              size="sm"
              className="h-9 text-destructive hover:text-destructive"
              onClick={() => setDeleteDialogOpen(true)}
            >
              <Trash2 className="mr-1.5 h-4 w-4" />
              Excluir
            </Button>

            <Button className="h-9 bg-purple-600 hover:bg-purple-700 text-white">
              <MessageSquare className="mr-1.5 h-4 w-4" />
              Conversar
            </Button>
          </div>
        </div>

        <Tabs defaultValue="prompt" className="mb-6">
          <TabsList className="mb-4">
            <TabsTrigger value="prompt">Prompt</TabsTrigger>
            <TabsTrigger value="details">Detalhes</TabsTrigger>
            <TabsTrigger value="connections">Conexões</TabsTrigger>
          </TabsList>

          <TabsContent value="prompt">
            <Section title="Prompt do Agente">
              <div className="bg-muted/20 p-4 rounded-md border font-mono text-sm whitespace-pre-wrap">
                {agent.prompt}
              </div>
            </Section>
          </TabsContent>

          <TabsContent value="details">
            <Section title="Informações do Agente">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <div>
                    <h3 className="text-sm font-medium text-muted-foreground">Nome</h3>
                    <p>{agent.name}</p>
                  </div>

                  <div>
                    <h3 className="text-sm font-medium text-muted-foreground">Tipo</h3>
                    <p>{agent.type}</p>
                  </div>

                  <div>
                    <h3 className="text-sm font-medium text-muted-foreground">Modelo</h3>
                    <p>{agent.model}</p>
                  </div>

                  <div>
                    <h3 className="text-sm font-medium text-muted-foreground">Status</h3>
                    <p>{getStatusBadge(agent.status)}</p>
                  </div>
                </div>

                <div className="space-y-2">
                  <div>
                    <h3 className="text-sm font-medium text-muted-foreground">Criado em</h3>
                    <p>{formatDate(agent.createdAt)}</p>
                  </div>

                  <div>
                    <h3 className="text-sm font-medium text-muted-foreground">Atualizado em</h3>
                    <p>{formatDate(agent.updatedAt)}</p>
                  </div>

                  <div>
                    <h3 className="text-sm font-medium text-muted-foreground">ID</h3>
                    <p className="font-mono text-xs">{agent.id}</p>
                  </div>
                </div>
              </div>
            </Section>
          </TabsContent>

          <TabsContent value="connections">
            <div className="space-y-6">
              <Section title="Agentes Relacionados">
                {agent.agents && agent.agents.length > 0 ? (
                  <div className="flex flex-wrap gap-2">
                    {agent.agents.map((relatedAgent) => (
                      <Badge key={relatedAgent.id} variant="secondary" className="px-2 py-1">
                        {relatedAgent.label}
                      </Badge>
                    ))}
                  </div>
                ) : (
                  <p className="text-muted-foreground">Nenhum agente relacionado.</p>
                )}
              </Section>

              <Section title="URLs Relacionadas">
                {agent.urls && agent.urls.length > 0 ? (
                  <div className="flex flex-wrap gap-2">
                    {agent.urls.map((url) => (
                      <Badge key={url.id} variant="secondary" className="px-2 py-1">
                        {url.label}
                      </Badge>
                    ))}
                  </div>
                ) : (
                  <p className="text-muted-foreground">Nenhuma URL relacionada.</p>
                )}
              </Section>
            </div>
          </TabsContent>
        </Tabs>

        <div className={cn("p-4 rounded-md border", agent.status === "archived" ? "bg-gray-50" : "bg-blue-50")}>
          <h3 className="font-medium mb-1">{agent.status === "archived" ? "Agente arquivado" : "Dica"}</h3>
          <p className="text-sm text-muted-foreground">
            {agent.status === "archived"
              ? "Este agente está arquivado e não aparecerá nas listas padrão. Você pode ativá-lo novamente clicando no botão 'Ativar'."
              : "Você pode testar este agente clicando no botão 'Conversar' acima."}
          </p>
        </div>
      </div>

      {/* Delete confirmation dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Excluir agente</AlertDialogTitle>
            <AlertDialogDescription>
              Esta ação não pode ser desfeita. Isso excluirá permanentemente o agente e removerá seus dados de nossos
              servidores.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancelar</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDelete}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              Excluir
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}
