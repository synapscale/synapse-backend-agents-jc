/**
 * @fileoverview
 * Componente que exibe informações sobre o processamento de IA,
 * como contagem de tokens, tempo de resposta e modelo utilizado.
 */

"use client"

import { useState, useEffect } from "react"
import { Cpu, Clock, Hash, AlertCircle } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { Tooltip, TooltipTrigger, TooltipContent, TooltipProvider } from "@/components/ui/tooltip"
import { TOKEN_LIMITS } from "@/lib/ai-constants"

/**
 * Props para o componente AIProcessingInfo
 */
interface AIProcessingInfoProps {
  /** Modelo de IA utilizado */
  model: string

  /** Contagem estimada de tokens */
  tokenCount: number

  /** Tempo de resposta em milissegundos */
  responseTimeMs?: number

  /** Indica se deve mostrar a contagem de tokens */
  showTokenCount?: boolean

  /** Indica se deve mostrar o tempo de resposta */
  showResponseTime?: boolean

  /** Indica se deve mostrar alertas de limite */
  showLimitAlerts?: boolean

  /** Classe CSS adicional */
  className?: string
}

/**
 * Componente que exibe informações sobre o processamento de IA
 */
export function AIProcessingInfo({
  model,
  tokenCount,
  responseTimeMs,
  showTokenCount = true,
  showResponseTime = true,
  showLimitAlerts = true,
  className = "",
}: AIProcessingInfoProps) {
  // Formata o tempo de resposta
  const [formattedTime, setFormattedTime] = useState<string>("")

  // Obtém o limite de tokens para o modelo
  const tokenLimit = TOKEN_LIMITS[model as keyof typeof TOKEN_LIMITS] || 4096

  // Calcula a porcentagem de uso de tokens
  const tokenPercentage = Math.round((tokenCount / tokenLimit) * 100)

  // Determina a cor do indicador de tokens
  const getTokenColor = () => {
    if (tokenPercentage >= 90) return "text-red-500 dark:text-red-400"
    if (tokenPercentage >= 75) return "text-amber-500 dark:text-amber-400"
    return "text-green-500 dark:text-green-400"
  }

  // Formata o tempo de resposta
  useEffect(() => {
    if (!responseTimeMs) {
      setFormattedTime("")
      return
    }

    if (responseTimeMs < 1000) {
      setFormattedTime(`${responseTimeMs}ms`)
    } else {
      const seconds = (responseTimeMs / 1000).toFixed(1)
      setFormattedTime(`${seconds}s`)
    }
  }, [responseTimeMs])

  return (
    <TooltipProvider>
      <div className={`flex flex-wrap items-center gap-2 text-xs ${className}`}>
        {/* Modelo utilizado */}
        <Tooltip>
          <TooltipTrigger asChild>
            <Badge variant="outline" className="flex items-center gap-1 px-2 py-0.5">
              <Cpu className="h-3 w-3" />
              <span>{model}</span>
            </Badge>
          </TooltipTrigger>
          <TooltipContent>
            <p>Modelo de IA utilizado</p>
          </TooltipContent>
        </Tooltip>

        {/* Contagem de tokens */}
        {showTokenCount && (
          <Tooltip>
            <TooltipTrigger asChild>
              <Badge variant="outline" className={`flex items-center gap-1 px-2 py-0.5 ${getTokenColor()}`}>
                <Hash className="h-3 w-3" />
                <span>
                  {tokenCount} / {tokenLimit}
                </span>
              </Badge>
            </TooltipTrigger>
            <TooltipContent>
              <p>Tokens utilizados: {tokenPercentage}% do limite</p>
            </TooltipContent>
          </Tooltip>
        )}

        {/* Tempo de resposta */}
        {showResponseTime && responseTimeMs && (
          <Tooltip>
            <TooltipTrigger asChild>
              <Badge variant="outline" className="flex items-center gap-1 px-2 py-0.5">
                <Clock className="h-3 w-3" />
                <span>{formattedTime}</span>
              </Badge>
            </TooltipTrigger>
            <TooltipContent>
              <p>Tempo de resposta</p>
            </TooltipContent>
          </Tooltip>
        )}

        {/* Alerta de limite */}
        {showLimitAlerts && tokenPercentage >= 90 && (
          <Tooltip>
            <TooltipTrigger asChild>
              <Badge
                variant="outline"
                className="flex items-center gap-1 px-2 py-0.5 bg-red-50 text-red-700 dark:bg-red-900/20 dark:text-red-400 border-red-200 dark:border-red-800/30"
              >
                <AlertCircle className="h-3 w-3" />
                <span>Limite próximo</span>
              </Badge>
            </TooltipTrigger>
            <TooltipContent>
              <p>Você está próximo do limite de tokens. Considere iniciar uma nova conversa.</p>
            </TooltipContent>
          </Tooltip>
        )}
      </div>
    </TooltipProvider>
  )
}
