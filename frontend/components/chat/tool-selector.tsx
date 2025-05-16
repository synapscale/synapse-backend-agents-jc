/**
 * Componente de Seletor de Ferramentas
 * 
 * Este componente permite ao usuário selecionar entre diferentes ferramentas
 * que podem ser utilizadas pelo assistente durante a conversa.
 */
"use client"

import { useState, useCallback } from "react"
import { Check, ChevronDown, Search, Database, FileText, Globe, Calculator } from "lucide-react"
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
import { Tool, ToolType } from "@/types/chat"

// Ferramentas disponíveis
const AVAILABLE_TOOLS: Tool[] = [
  {
    id: "none",
    name: "Nenhuma",
    description: "Sem acesso a ferramentas externas",
    type: "custom",
    icon: <div className="w-4 h-4" />,
  },
  {
    id: "search",
    name: "Pesquisa Web",
    description: "Permite ao assistente pesquisar informações na web",
    type: "search",
    icon: <Search className="h-4 w-4" />,
    isNew: true,
  },
  {
    id: "database",
    name: "Banco de Dados",
    description: "Permite ao assistente consultar e manipular bancos de dados",
    type: "database",
    icon: <Database className="h-4 w-4" />,
  },
  {
    id: "file",
    name: "Arquivos",
    description: "Permite ao assistente ler e analisar arquivos",
    type: "file",
    icon: <FileText className="h-4 w-4" />,
  },
  {
    id: "api",
    name: "APIs",
    description: "Permite ao assistente fazer chamadas para APIs externas",
    type: "api",
    icon: <Globe className="h-4 w-4" />,
  },
  {
    id: "calculator",
    name: "Calculadora",
    description: "Permite ao assistente realizar cálculos complexos",
    type: "calculator",
    icon: <Calculator className="h-4 w-4" />,
  },
]

interface ToolSelectorProps {
  selectedToolId?: string
  onSelectTool?: (toolId: string) => void
}

/**
 * Componente de seletor de ferramentas
 */
export default function ToolSelector({
  selectedToolId = "none",
  onSelectTool,
}: ToolSelectorProps) {
  // Estado local para a ferramenta selecionada
  const [currentToolId, setCurrentToolId] = useState(selectedToolId)

  // Encontra a ferramenta atual com base no ID
  const currentTool = AVAILABLE_TOOLS.find((tool) => tool.id === currentToolId) || AVAILABLE_TOOLS[0]

  /**
   * Manipula a seleção de uma ferramenta
   */
  const handleSelectTool = useCallback(
    (toolId: string) => {
      setCurrentToolId(toolId)
      if (onSelectTool) {
        onSelectTool(toolId)
      }
    },
    [onSelectTool]
  )

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" className="flex items-center justify-between w-full gap-2">
          <div className="flex items-center gap-2 truncate">
            {currentTool.icon}
            <span className="truncate">{currentTool.name}</span>
            {currentTool.isNew && (
              <Badge variant="outline" className="ml-1 text-xs bg-primary/10 text-primary">
                Novo
              </Badge>
            )}
          </div>
          <ChevronDown className="h-4 w-4 opacity-50" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="start" className="w-[220px]">
        <DropdownMenuLabel>Selecione uma ferramenta</DropdownMenuLabel>
        <DropdownMenuSeparator />
        <DropdownMenuGroup>
          {AVAILABLE_TOOLS.map((tool) => (
            <DropdownMenuItem
              key={tool.id}
              onClick={() => handleSelectTool(tool.id)}
              className="flex items-center justify-between"
            >
              <div className="flex items-center gap-2 truncate">
                {tool.icon}
                <span className="truncate">{tool.name}</span>
                {tool.isNew && (
                  <Badge variant="outline" className="ml-1 text-xs bg-primary/10 text-primary">
                    Novo
                  </Badge>
                )}
              </div>
              {tool.id === currentToolId && <Check className="h-4 w-4" />}
            </DropdownMenuItem>
          ))}
        </DropdownMenuGroup>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
