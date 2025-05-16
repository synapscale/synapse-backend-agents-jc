/**
 * Componente de Seletor de Modelo
 * 
 * Este componente permite ao usuário selecionar entre diferentes modelos de IA
 * disponíveis para uso no chat.
 */
"use client"

import { useState, useCallback } from "react"
import { Check, ChevronDown, Info } from "lucide-react"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"
import { Badge } from "@/components/ui/badge"
import { AIModel } from "@/types/chat"

// Modelos de exemplo
const AVAILABLE_MODELS: AIModel[] = [
  {
    id: "gpt-4o",
    name: "GPT-4o",
    description: "Modelo mais avançado da OpenAI com capacidades multimodais",
    provider: "openai",
    category: "multimodal",
    capabilities: {
      images: true,
      audio: true,
      tools: true,
      code: true,
      maxContextLength: 128000,
    },
    isNew: true,
    iconUrl: "/icons/openai.svg",
  },
  {
    id: "claude-3-opus",
    name: "Claude 3 Opus",
    description: "Modelo mais poderoso da Anthropic para tarefas complexas",
    provider: "anthropic",
    category: "multimodal",
    capabilities: {
      images: true,
      tools: true,
      code: true,
      maxContextLength: 200000,
    },
    iconUrl: "/icons/anthropic.svg",
  },
  {
    id: "gemini-pro",
    name: "Gemini Pro",
    description: "Modelo avançado do Google com capacidades multimodais",
    provider: "google",
    category: "multimodal",
    capabilities: {
      images: true,
      code: true,
      maxContextLength: 32000,
    },
    iconUrl: "/icons/google.svg",
  },
  {
    id: "mistral-large",
    name: "Mistral Large",
    description: "Modelo de alta performance da Mistral AI",
    provider: "mistral",
    category: "text",
    capabilities: {
      code: true,
      maxContextLength: 32000,
    },
    iconUrl: "/icons/mistral.svg",
  },
]

interface ModelSelectorProps {
  selectedModelId?: string
  onSelectModel?: (modelId: string) => void
}

/**
 * Componente de seletor de modelo
 */
export default function ModelSelector({
  selectedModelId = "gpt-4o",
  onSelectModel,
}: ModelSelectorProps) {
  // Estado local para o modelo selecionado
  const [currentModelId, setCurrentModelId] = useState(selectedModelId)

  // Encontra o modelo atual com base no ID
  const currentModel = AVAILABLE_MODELS.find((model) => model.id === currentModelId) || AVAILABLE_MODELS[0]

  /**
   * Manipula a seleção de um modelo
   */
  const handleSelectModel = useCallback(
    (modelId: string) => {
      setCurrentModelId(modelId)
      if (onSelectModel) {
        onSelectModel(modelId)
      }
    },
    [onSelectModel]
  )

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" className="flex items-center justify-between w-full gap-2">
          <div className="flex items-center gap-2 truncate">
            {currentModel.iconUrl && (
              <img
                src={currentModel.iconUrl}
                alt={`${currentModel.provider} logo`}
                className="h-4 w-4"
              />
            )}
            <span className="truncate">{currentModel.name}</span>
            {currentModel.isNew && (
              <Badge variant="outline" className="ml-1 text-xs bg-primary/10 text-primary">
                Novo
              </Badge>
            )}
          </div>
          <ChevronDown className="h-4 w-4 opacity-50" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="start" className="w-[220px]">
        <DropdownMenuLabel>Selecione um modelo</DropdownMenuLabel>
        <DropdownMenuSeparator />
        <DropdownMenuGroup>
          {AVAILABLE_MODELS.map((model) => (
            <DropdownMenuItem
              key={model.id}
              onClick={() => handleSelectModel(model.id)}
              className="flex items-center justify-between"
            >
              <div className="flex items-center gap-2 truncate">
                {model.iconUrl && (
                  <img
                    src={model.iconUrl}
                    alt={`${model.provider} logo`}
                    className="h-4 w-4"
                  />
                )}
                <span className="truncate">{model.name}</span>
                {model.isNew && (
                  <Badge variant="outline" className="ml-1 text-xs bg-primary/10 text-primary">
                    Novo
                  </Badge>
                )}
              </div>
              {model.id === currentModelId && <Check className="h-4 w-4" />}
            </DropdownMenuItem>
          ))}
        </DropdownMenuGroup>
        <DropdownMenuSeparator />
        <DropdownMenuItem asChild>
          <a
            href="/docs/models"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center"
          >
            <Info className="mr-2 h-4 w-4" />
            <span>Sobre os modelos</span>
          </a>
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}

/**
 * Componente de barra lateral para seleção de modelo
 */
export function ModelSelectorSidebar() {
  return (
    <div className="flex items-center gap-2">
      <TooltipProvider>
        <Tooltip>
          <TooltipTrigger asChild>
            <div className="w-full max-w-[180px]">
              <ModelSelector />
            </div>
          </TooltipTrigger>
          <TooltipContent side="bottom">
            <p>Selecione o modelo de IA para esta conversa</p>
          </TooltipContent>
        </Tooltip>
      </TooltipProvider>
    </div>
  )
}
