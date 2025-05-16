/**
 * Componente de Seletor de Presets
 * 
 * Este componente permite ao usuário selecionar entre diferentes presets
 * que combinam modelo, ferramenta e personalidade para uso rápido.
 */
"use client"

import { useState, useCallback } from "react"
import { Check, ChevronDown, Star, Plus, Save } from "lucide-react"
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
import { ChatPreset } from "@/types/chat"

// Presets disponíveis
const AVAILABLE_PRESETS: ChatPreset[] = [
  {
    id: "default",
    name: "Padrão",
    description: "Configuração padrão equilibrada",
    model: "gpt-4o",
    tool: "none",
    personality: "default",
    createdAt: Date.now(),
    isFavorite: true,
  },
  {
    id: "creative-assistant",
    name: "Assistente Criativo",
    description: "Ideal para brainstorming e ideias criativas",
    model: "claude-3-opus",
    tool: "none",
    personality: "creative",
    createdAt: Date.now(),
    isFavorite: false,
  },
  {
    id: "code-helper",
    name: "Ajudante de Código",
    description: "Especializado em programação e desenvolvimento",
    model: "gpt-4o",
    tool: "none",
    personality: "programmer",
    createdAt: Date.now(),
    isFavorite: true,
  },
  {
    id: "research-assistant",
    name: "Assistente de Pesquisa",
    description: "Configurado para pesquisa e análise de informações",
    model: "claude-3-opus",
    tool: "search",
    personality: "academic",
    createdAt: Date.now(),
    isFavorite: false,
  },
]

interface PresetSelectorProps {
  selectedPresetId?: string
  onSelectPreset?: (preset: ChatPreset) => void
  onSavePreset?: () => void
}

/**
 * Componente de seletor de presets
 */
export default function PresetSelector({
  selectedPresetId = "default",
  onSelectPreset,
  onSavePreset,
}: PresetSelectorProps) {
  // Estado local para o preset selecionado
  const [currentPresetId, setCurrentPresetId] = useState(selectedPresetId)

  // Encontra o preset atual com base no ID
  const currentPreset = AVAILABLE_PRESETS.find((preset) => preset.id === currentPresetId) || AVAILABLE_PRESETS[0]

  /**
   * Manipula a seleção de um preset
   */
  const handleSelectPreset = useCallback(
    (preset: ChatPreset) => {
      setCurrentPresetId(preset.id)
      if (onSelectPreset) {
        onSelectPreset(preset)
      }
    },
    [onSelectPreset]
  )

  /**
   * Manipula o salvamento de um novo preset
   */
  const handleSavePreset = useCallback(() => {
    if (onSavePreset) {
      onSavePreset()
    }
  }, [onSavePreset])

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" className="flex items-center justify-between w-full gap-2">
          <div className="flex items-center gap-2 truncate">
            {currentPreset.isFavorite ? <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" /> : <div className="w-4 h-4" />}
            <span className="truncate">{currentPreset.name}</span>
          </div>
          <ChevronDown className="h-4 w-4 opacity-50" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="start" className="w-[220px]">
        <DropdownMenuLabel>Presets</DropdownMenuLabel>
        <DropdownMenuSeparator />
        <DropdownMenuGroup>
          {AVAILABLE_PRESETS.map((preset) => (
            <DropdownMenuItem
              key={preset.id}
              onClick={() => handleSelectPreset(preset)}
              className="flex items-center justify-between"
            >
              <div className="flex items-center gap-2 truncate">
                {preset.isFavorite && <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />}
                {!preset.isFavorite && <div className="w-4 h-4" />}
                <span className="truncate">{preset.name}</span>
              </div>
              {preset.id === currentPresetId && <Check className="h-4 w-4" />}
            </DropdownMenuItem>
          ))}
        </DropdownMenuGroup>
        <DropdownMenuSeparator />
        <DropdownMenuItem onClick={handleSavePreset}>
          <Save className="mr-2 h-4 w-4" />
          <span>Salvar configuração atual</span>
        </DropdownMenuItem>
        <DropdownMenuItem asChild>
          <a href="/presets" className="flex items-center">
            <Plus className="mr-2 h-4 w-4" />
            <span>Gerenciar presets</span>
          </a>
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
