"use client"
import { MoreHorizontal, Check, Edit, Copy, Trash2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { cn } from "@/lib/utils"
import type { PromptTemplate } from "@/components/templates-modal"

interface TemplateCardProps {
  template: PromptTemplate
  isSelected: boolean
  onSelect: (template: PromptTemplate) => void
  onEdit: (template: PromptTemplate) => void
  onDelete: (id: string) => void
  onCopy: (content: string) => void
  onUse: (template: PromptTemplate) => void
}

export function TemplateCard({ template, isSelected, onSelect, onEdit, onDelete, onCopy, onUse }: TemplateCardProps) {
  return (
    <div
      className={cn(
        "p-2.5 sm:p-3 border rounded-lg hover:border-purple-200 transition-colors cursor-pointer",
        isSelected && "border-purple-300 bg-purple-50",
      )}
      onClick={() => onSelect(template)}
      role="button"
      tabIndex={0}
      aria-label={`Template: ${template.name}`}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") {
          onSelect(template)
        }
      }}
    >
      <div className="flex justify-between items-start">
        <div className="mr-2">
          <h4 className="font-medium text-xs sm:text-sm">{template.name}</h4>
          <p className="text-xs text-gray-500 mt-0.5 sm:mt-1 line-clamp-1">{template.description}</p>
        </div>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button
              variant="ghost"
              size="icon"
              className="h-6 w-6 sm:h-7 sm:w-7"
              onClick={(e) => e.stopPropagation()}
              aria-label="Opções do template"
            >
              <MoreHorizontal className="h-3.5 w-3.5 sm:h-4 sm:w-4" aria-hidden="true" />
              <span className="sr-only">Ações</span>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-[180px]">
            <DropdownMenuItem
              onClick={(e) => {
                e.stopPropagation()
                onUse(template)
              }}
              className="text-xs sm:text-sm py-1.5"
            >
              <Check className="mr-2 h-3.5 w-3.5 sm:h-4 sm:w-4" aria-hidden="true" />
              Usar Template
            </DropdownMenuItem>
            <DropdownMenuItem
              onClick={(e) => {
                e.stopPropagation()
                onEdit(template)
              }}
              className="text-xs sm:text-sm py-1.5"
            >
              <Edit className="mr-2 h-3.5 w-3.5 sm:h-4 sm:w-4" aria-hidden="true" />
              Editar
            </DropdownMenuItem>
            <DropdownMenuItem
              onClick={(e) => {
                e.stopPropagation()
                onCopy(template.content)
              }}
              className="text-xs sm:text-sm py-1.5"
            >
              <Copy className="mr-2 h-3.5 w-3.5 sm:h-4 sm:w-4" aria-hidden="true" />
              Copiar Conteúdo
            </DropdownMenuItem>
            <DropdownMenuItem
              className="text-red-600 text-xs sm:text-sm py-1.5"
              onClick={(e) => {
                e.stopPropagation()
                onDelete(template.id)
              }}
            >
              <Trash2 className="mr-2 h-3.5 w-3.5 sm:h-4 sm:w-4" aria-hidden="true" />
              Excluir
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
      <div className="flex flex-wrap items-center gap-1.5 sm:gap-2 mt-1.5 sm:mt-2">
        {template.categories.map((category) => (
          <Badge
            key={category}
            variant="outline"
            className="bg-muted/30 px-1.5 sm:px-2 py-0 sm:py-0.5 text-[10px] sm:text-xs"
          >
            {category}
          </Badge>
        ))}
        <span className="text-[10px] sm:text-xs text-gray-400">
          {new Date(template.createdAt).toLocaleDateString()}
        </span>
      </div>
    </div>
  )
}
