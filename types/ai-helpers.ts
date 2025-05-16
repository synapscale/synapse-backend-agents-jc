/**
 * @fileoverview
 * Este arquivo contém tipos e interfaces que facilitam a interação com modelos de IA.
 * Esses tipos são projetados para serem explícitos e auto-documentados, facilitando
 * a compreensão e manipulação por ferramentas de IA.
 */

/**
 * Representa um componente que pode ser detectado e manipulado pela IA.
 * @typedef {Object} AIDetectableComponent
 */
export interface AIDetectableComponent {
  /** Identificador único do componente */
  id: string

  /** Nome descritivo do componente para referência em prompts */
  name: string

  /** Caminho do componente na árvore de componentes */
  path: string

  /** Propriedades do componente que podem ser modificadas */
  props?: Record<string, any>

  /** Método usado para detectar o componente (DOM, React, etc.) */
  detectionMethod?: string

  /** Indica se o componente pode ser modificado pela IA */
  modifiable?: boolean

  /** Metadados adicionais que podem ser úteis para a IA */
  metadata?: Record<string, any>
}

/**
 * Representa uma mensagem que pode ser processada por modelos de IA.
 * @typedef {Object} AIProcessableMessage
 */
export interface AIProcessableMessage {
  /** Identificador único da mensagem */
  id: string

  /** Papel do remetente (usuário ou assistente) */
  role: "user" | "assistant" | "system"

  /** Conteúdo da mensagem */
  content: string

  /** Modelo de IA usado para gerar a resposta (se aplicável) */
  model?: string

  /** Timestamp da mensagem */
  timestamp?: number

  /** Metadados adicionais que podem ser úteis para a IA */
  metadata?: Record<string, any>

  /** Componentes referenciados na mensagem */
  referencedComponents?: AIDetectableComponent[]
}

/**
 * Configuração para interação com modelos de IA.
 * @typedef {Object} AIModelConfig
 */
export interface AIModelConfig {
  /** Identificador do modelo */
  id: string

  /** Nome descritivo do modelo */
  name: string

  /** Provedor do modelo (OpenAI, Anthropic, etc.) */
  provider: string

  /** Versão do modelo */
  version?: string

  /** Parâmetros de configuração específicos do modelo */
  parameters?: Record<string, any>

  /** Capacidades do modelo (código, imagens, etc.) */
  capabilities?: string[]

  /** URL do ícone do modelo */
  iconUrl?: string
}

/**
 * Configuração para personalidade do assistente de IA.
 * @typedef {Object} AIPersonalityConfig
 */
export interface AIPersonalityConfig {
  /** Identificador da personalidade */
  id: string

  /** Nome descritivo da personalidade */
  name: string

  /** Descrição da personalidade */
  description: string

  /** Instruções de sistema para configurar a personalidade */
  systemPrompt: string

  /** Exemplos de interações com esta personalidade */
  examples?: AIProcessableMessage[]
}

/**
 * Configuração para ferramentas que podem ser usadas pela IA.
 * @typedef {Object} AIToolConfig
 */
export interface AIToolConfig {
  /** Identificador da ferramenta */
  id: string

  /** Nome descritivo da ferramenta */
  name: string

  /** Descrição da ferramenta */
  description: string

  /** Tipo da ferramenta */
  type: "function" | "retrieval" | "code" | "other"

  /** Parâmetros aceitos pela ferramenta */
  parameters?: Record<string, any>

  /** Indica se a ferramenta está ativa */
  active: boolean
}

/**
 * Configuração para preferências do usuário relacionadas à IA.
 * @typedef {Object} AIUserPreferences
 */
export interface AIUserPreferences {
  /** Modelos recentemente usados */
  recentModels?: string[]

  /** Modelo preferido */
  preferredModel?: string

  /** Personalidade preferida */
  preferredPersonality?: string

  /** Ferramentas preferidas */
  preferredTools?: string[]

  /** Configurações de interface relacionadas à IA */
  interfaceSettings?: {
    /** Mostrar probabilidades de tokens */
    showTokenProbabilities?: boolean

    /** Mostrar uso de tokens */
    showTokenUsage?: boolean

    /** Mostrar tempo de resposta */
    showResponseTime?: boolean
  }
}
