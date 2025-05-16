"use client"
import { Check } from "lucide-react"
import { Button } from "@/components/ui/button"
import type { PromptTemplate } from "@/components/templates/templates-modal" // Adjusted path for type

interface TemplatePreviewProps {
  template: PromptTemplate
  onUse: (template: PromptTemplate) => void
}

export function TemplatePreview({ template, onUse }: TemplatePreviewProps) {
  return (
    <div className="mt-3 sm:mt-4 border-t pt-3 sm:pt-4">
      <div className="flex justify-between items-center mb-1.5 sm:mb-2">
        <h4 className="font-medium text-xs sm:text-sm">Prévia do Template</h4>
        <Button
          variant="default"
          size="sm"
          className="h-7 sm:h-8 text-xs bg-purple-600 hover:bg-purple-700"
          onClick={() => onUse(template)}
          aria-label={`Usar template ${template.name}`}
        >
          <Check className="mr-1 h-3 w-3 sm:h-3.5 sm:w-3.5" aria-hidden="true" />
          Usar Este Template
        </Button>
      </div>
      <div
        className="bg-gray-50 p-2 sm:p-3 rounded-md border text-[10px] sm:text-xs font-mono h-[120px] sm:h-[150px] overflow-auto"
        aria-label="Prévia do conteúdo do template"
      >
        {template.content.split("\n").map((line, i) => (
          <div key={i} className="whitespace-pre-wrap">
            {line || "\u00A0"} {/* Render non-breaking space for empty lines to maintain height */}
          </div>
        ))}
      </div>
    </div>
  )
}

