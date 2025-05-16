"use client"

import { ChevronDown } from "lucide-react"
import { Button } from "@/components/ui/button"
import ModelSelectorSidebar from "./model-selector-sidebar"
import ToolSelector from "./tool-selector"
import PersonalitySelector from "./personality-selector"
import PresetSelector from "./preset-selector"

interface ChatConfigProps {
  showConfig: boolean
  onToggleConfig: () => void
}

export function ChatConfig({ showConfig, onToggleConfig }: ChatConfigProps) {
  return (
    <>
      {/* Seletores de modelo, ferramentas e personalidade */}
      {showConfig && (
        <div className="flex flex-wrap items-center gap-2 mt-3 px-2 animate-in">
          <ModelSelectorSidebar />
          <ToolSelector />
          <PersonalitySelector />
          <PresetSelector />
        </div>
      )}

      {/* Toggle de configurações */}
      <div className="flex justify-center mt-2">
        <Button
          variant="ghost"
          size="sm"
          className="text-xs text-gray-500 dark:text-gray-400 flex items-center gap-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-full px-3"
          onClick={onToggleConfig}
        >
          {showConfig ? "Ocultar" : "Mostrar"} Configurações
          <ChevronDown className={`h-3 w-3 transition-transform duration-200 ${showConfig ? "rotate-180" : ""}`} />
        </Button>
        <div className="ml-auto">
          <Button
            variant="ghost"
            size="sm"
            className="text-xs text-primary flex items-center gap-1 hover:bg-primary/5 dark:hover:bg-primary/10 rounded-full px-3"
          >
            Tutorial
          </Button>
        </div>
      </div>
    </>
  )
}
