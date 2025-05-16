"use client"

import { useState, useEffect, useMemo } from "react"
import Link from "next/link"
import { ArrowLeft, BarChart } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Section } from "@/components/ui/section"
import { Skeleton } from "@/components/ui/skeleton"
import { useLocalStorage } from "@/hooks/use-local-storage"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

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

export default function AgentStatsPage() {
  const [isLoading, setIsLoading] = useState(true)
  const [agents] = useLocalStorage<Agent[]>("agents", [])

  // Simulate loading
  useEffect(() => {
    const timer = setTimeout(() => {
      setIsLoading(false)
    }, 800)

    return () => clearTimeout(timer)
  }, [])

  // Calculate statistics
  const stats = useMemo(() => {
    // Count by type
    const typeCount = agents.reduce(
      (acc, agent) => {
        acc[agent.type] = (acc[agent.type] || 0) + 1
        return acc
      },
      {} as Record<string, number>,
    )

    // Count by model
    const modelCount = agents.reduce(
      (acc, agent) => {
        acc[agent.model] = (acc[agent.model] || 0) + 1
        return acc
      },
      {} as Record<string, number>,
    )

    // Count by status
    const statusCount = agents.reduce(
      (acc, agent) => {
        const status = agent.status || "active"
        acc[status] = (acc[status] || 0) + 1
        return acc
      },
      {} as Record<string, number>,
    )

    return {
      total: agents.length,
      typeCount,
      modelCount,
      statusCount,
    }
  }, [agents])

  // Loading state
  if (isLoading) {
    return (
      <div className="p-4 md:p-6">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center gap-2 mb-6">
            <Skeleton className="h-9 w-24" />
            <div className="w-px h-6 bg-gray-200" aria-hidden="true"></div>
            <Skeleton className="h-8 w-48" />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            {Array(4)
              .fill(0)
              .map((_, i) => (
                <Skeleton key={i} className="h-32 w-full" />
              ))}
          </div>

          <Skeleton className="h-64 w-full" />
        </div>
      </div>
    )
  }

  return (
    <div className="p-4 md:p-6">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center gap-2 mb-6">
          <Link href="/agentes" className="flex items-center text-gray-500 hover:text-gray-900">
            <ArrowLeft className="mr-1 h-4 w-4" />
            Voltar
          </Link>
          <div className="w-px h-6 bg-gray-200" aria-hidden="true"></div>
          <h1 className="text-xl font-bold">Estatísticas de Agentes</h1>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Total de Agentes</CardTitle>
              <BarChart className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.total}</div>
              <CardDescription>{stats.statusCount.active || 0} ativos</CardDescription>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Por Tipo</CardTitle>
              <BarChart className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {stats.typeCount.chat || 0} <span className="text-sm font-normal">chat</span>
              </div>
              <CardDescription>
                {stats.typeCount.imagem || 0} imagem, {stats.typeCount.texto || 0} texto
              </CardDescription>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Por Modelo</CardTitle>
              <BarChart className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {stats.modelCount["gpt-4o"] || 0} <span className="text-sm font-normal">GPT-4o</span>
              </div>
              <CardDescription>
                {stats.modelCount["gpt-4"] || 0} GPT-4, {stats.modelCount["gpt-3.5-turbo"] || 0} GPT-3.5
              </CardDescription>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Por Status</CardTitle>
              <BarChart className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {stats.statusCount.active || 0} <span className="text-sm font-normal">ativos</span>
              </div>
              <CardDescription>
                {stats.statusCount.draft || 0} rascunhos, {stats.statusCount.archived || 0} arquivados
              </CardDescription>
            </CardContent>
          </Card>
        </div>

        <Section title="Visão Geral dos Agentes">
          <div className="text-center py-12 border rounded-lg">
            <p className="text-muted-foreground mb-4">Estatísticas detalhadas estarão disponíveis em breve.</p>
            <Link href="/agentes">
              <Button className="bg-purple-600 hover:bg-purple-700">Voltar para a lista de agentes</Button>
            </Link>
          </div>
        </Section>
      </div>
    </div>
  )
}
