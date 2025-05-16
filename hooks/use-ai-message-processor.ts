"use client"

/**
 * @fileoverview
 * Hook para processamento de mensagens com IA.
 * Este hook facilita o processamento de mensagens por modelos de IA,
 * com funções para formatação, análise e manipulação de mensagens.
 */

import { useState, useCallback } from "react"
import {
  formatMessageForAI,
  extractReferencedComponents,
  estimateTokenCount,
  extractCodeFromResponse,
} from "@/lib/ai-utils"
import { TOKEN_LIMITS } from "@/lib/ai-constants"
import type { AIProcessableMessage, AIDetectableComponent, AIModelConfig } from "@/types/ai-helpers"
import type { Message } from "@/types/chat"

/**
 * Interface para o estado do processador de mensagens
 */
interface AIMessageProcessorState {
  /** Mensagens processadas */
  processedMessages: AIProcessableMessage[]

  /** Indica se está processando */
  isProcessing: boolean

  /** Erro de processamento, se houver */
  error: Error | null

  /** Contagem estimada de tokens */
  tokenCount: number

  /** Componentes referenciados nas mensagens */
  referencedComponents: AIDetectableComponent[]
}

/**
 * Hook para processamento de mensagens com IA
 *
 * @param modelConfig - Configuração do modelo de IA
 * @returns Estado e funções para processamento de mensagens
 */
export function useAIMessageProcessor(modelConfig: AIModelConfig) {
  // Estado do processador
  const [state, setState] = useState<AIMessageProcessorState>({
    processedMessages: [],
    isProcessing: false,
    error: null,
    tokenCount: 0,
    referencedComponents: [],
  })

  /**
   * Processa uma lista de mensagens para uso com IA
   */
  const processMessages = useCallback(async (messages: Message[]) => {
    setState((prev) => ({ ...prev, isProcessing: true, error: null }))

    try {
      // Converte mensagens para o formato processável por IA
      const processedMessages: AIProcessableMessage[] = messages.map((msg) => ({
        id: msg.id,
        role: msg.role as "user" | "assistant" | "system",
        content: msg.content,
        model: msg.model,
        timestamp: msg.timestamp || Date.now(),
        metadata: msg.metadata || {},
      }))

      // Extrai componentes referenciados
      const referencedComponents: AIDetectableComponent[] = []

      for (const msg of processedMessages) {
        if (msg.role === "user") {
          const components = extractReferencedComponents(msg.content)
          referencedComponents.push(...components)

          // Adiciona os componentes à mensagem
          msg.referencedComponents = components
        }
      }

      // Calcula a contagem total de tokens
      let totalTokens = 0
      for (const msg of processedMessages) {
        totalTokens += estimateTokenCount(msg.content)
      }

      // Atualiza o estado
      setState({
        processedMessages,
        isProcessing: false,
        error: null,
        tokenCount: totalTokens,
        referencedComponents,
      })

      return processedMessages
    } catch (error) {
      setState((prev) => ({
        ...prev,
        isProcessing: false,
        error: error instanceof Error ? error : new Error(String(error)),
      }))
      throw error
    }
  }, [])

  /**
   * Verifica se a contagem de tokens excede o limite do modelo
   */
  const exceedsTokenLimit = useCallback(() => {
    const modelLimit = TOKEN_LIMITS[modelConfig.id as keyof typeof TOKEN_LIMITS] || 4096
    return state.tokenCount > modelLimit
  }, [state.tokenCount, modelConfig.id])

  /**
   * Extrai blocos de código de uma resposta
   */
  const extractCodeBlocks = useCallback((response: string) => {
    return extractCodeFromResponse(response)
  }, [])

  /**
   * Adiciona uma mensagem ao estado processado
   */
  const addMessage = useCallback((message: Partial<AIProcessableMessage>) => {
    const formattedMessage = formatMessageForAI(message)

    setState((prev) => {
      const newMessages = [...prev.processedMessages, formattedMessage]
      const newTokenCount = prev.tokenCount + estimateTokenCount(formattedMessage.content)

      // Extrai componentes referenciados se for mensagem do usuário
      let newReferencedComponents = [...prev.referencedComponents]
      if (message.role === "user") {
        const components = extractReferencedComponents(message.content || "")
        formattedMessage.referencedComponents = components
        newReferencedComponents = [...newReferencedComponents, ...components]
      }

      return {
        ...prev,
        processedMessages: newMessages,
        tokenCount: newTokenCount,
        referencedComponents: newReferencedComponents,
      }
    })

    return formattedMessage
  }, [])

  return {
    ...state,
    processMessages,
    exceedsTokenLimit,
    extractCodeBlocks,
    addMessage,
  }
}
