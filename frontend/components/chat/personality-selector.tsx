/**
 * Componente de Seletor de Personalidade
 * 
 * Este componente permite ao usuário selecionar entre diferentes personalidades
 * que podem ser aplicadas ao assistente durante a conversa.
 */
"use client"

import { useState, useCallback } from "react"
import { Check, ChevronDown, User, Brain, Lightbulb, Code, Briefcase, GraduationCap } from "lucide-react"
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
import { Personality } from "@/types/chat"

// Personalidades disponíveis
const AVAILABLE_PERSONALITIES: Personality[] = [
  {
    id: "default",
    name: "Padrão",
    description: "Assistente equilibrado e versátil",
    icon: <User className="h-4 w-4" />,
    systemPrompt: "Você é um assistente útil, respeitoso e honesto. Responda de forma concisa e clara.",
  },
  {
    id: "creative",
    name: "Criativo",
    description: "Assistente com foco em ideias criativas e inovadoras",
    icon: <Lightbulb className="h-4 w-4" />,
    systemPrompt: "Você é um assistente criativo e inovador. Pense fora da caixa e ofereça ideias originais.",
    isNew: true,
  },
  {
    id: "analytical",
    name: "Analítico",
    description: "Assistente com foco em análise detalhada e lógica",
    icon: <Brain className="h-4 w-4" />,
    systemPrompt: "Você é um assistente analítico e lógico. Forneça análises detalhadas e baseadas em fatos.",
  },
  {
    id: "programmer",
    name: "Programador",
    description: "Assistente especializado em programação e desenvolvimento",
    icon: <Code className="h-4 w-4" />,
    systemPrompt: "Você é um assistente especializado em programação. Forneça código limpo, bem documentado e eficiente.",
  },
  {
    id: "business",
    name: "Negócios",
    description: "Assistente com foco em estratégias de negócios",
    icon: <Briefcase className="h-4 w-4" />,
    systemPrompt: "Você é um assistente especializado em negócios. Forneça insights estratégicos e práticos.",
  },
  {
    id: "academic",
    name: "Acadêmico",
    description: "Assistente com foco em pesquisa e rigor acadêmico",
    icon: <GraduationCap className="h-4 w-4" />,
    systemPrompt: "Você é um assistente acadêmico. Forneça informações precisas, citando fontes quando possível.",
  },
]

interface PersonalitySelectorProps {
  selectedPersonalityId?: string
  onSelectPersonality?: (personalityId: string) => void
}

/**
 * Componente de seletor de personalidade
 */
export default function PersonalitySelector({
  selectedPersonalityId = "default",
  onSelectPersonality,
}: PersonalitySelectorProps) {
  // Estado local para a personalidade selecionada
  const [currentPersonalityId, setCurrentPersonalityId] = useState(selectedPersonalityId)

  // Encontra a personalidade atual com base no ID
  const currentPersonality = AVAILABLE_PERSONALITIES.find((personality) => personality.id === currentPersonalityId) || AVAILABLE_PERSONALITIES[0]

  /**
   * Manipula a seleção de uma personalidade
   */
  const handleSelectPersonality = useCallback(
    (personalityId: string) => {
      setCurrentPersonalityId(personalityId)
      if (onSelectPersonality) {
        onSelectPersonality(personalityId)
      }
    },
    [onSelectPersonality]
  )

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" className="flex items-center justify-between w-full gap-2">
          <div className="flex items-center gap-2 truncate">
            {currentPersonality.icon}
            <span className="truncate">{currentPersonality.name}</span>
            {currentPersonality.isNew && (
              <Badge variant="outline" className="ml-1 text-xs bg-primary/10 text-primary">
                Novo
              </Badge>
            )}
          </div>
          <ChevronDown className="h-4 w-4 opacity-50" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="start" className="w-[220px]">
        <DropdownMenuLabel>Selecione uma personalidade</DropdownMenuLabel>
        <DropdownMenuSeparator />
        <DropdownMenuGroup>
          {AVAILABLE_PERSONALITIES.map((personality) => (
            <DropdownMenuItem
              key={personality.id}
              onClick={() => handleSelectPersonality(personality.id)}
              className="flex items-center justify-between"
            >
              <div className="flex items-center gap-2 truncate">
                {personality.icon}
                <span className="truncate">{personality.name}</span>
                {personality.isNew && (
                  <Badge variant="outline" className="ml-1 text-xs bg-primary/10 text-primary">
                    Novo
                  </Badge>
                )}
              </div>
              {personality.id === currentPersonalityId && <Check className="h-4 w-4" />}
            </DropdownMenuItem>
          ))}
        </DropdownMenuGroup>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
