"use client"
import { Filter, Plus, Search, Tag } from "lucide-react"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { TemplateCard } from "@/components/templates/template-card" // Adjusted path
import { TemplatePreview } from "@/components/templates/template-preview" // Adjusted path
import type { PromptTemplate } from "@/components/templates/templates-modal" // Adjusted path for type

interface TemplateListProps {
  templates: PromptTemplate[]
  categories: string[]
  selectedTemplate: PromptTemplate | null
  filterCategory: string
  searchQuery: string
  onSelectTemplate: (template: PromptTemplate) => void
  onEditTemplate: (template: PromptTemplate) => void
  onDeleteTemplate: (id: string) => void
  onCopyContent: (content: string) => void
  onUseTemplate: (template: PromptTemplate) => void
  onCreateTemplate: () => void
  onManageCategories: () => void
  onFilterCategoryChange: (category: string) => void
  onSearchQueryChange: (query: string) => void
}

export function TemplateList({
  templates,
  categories,
  selectedTemplate,
  filterCategory,
  searchQuery,
  onSelectTemplate,
  onEditTemplate,
  onDeleteTemplate,
  onCopyContent,
  onUseTemplate,
  onCreateTemplate,
  onManageCategories,
  onFilterCategoryChange,
  onSearchQueryChange,
}: TemplateListProps) {
  return (
    <div className="py-3 sm:py-4">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 sm:gap-4 mb-3 sm:mb-4">
        <div className="flex gap-2 w-full sm:w-auto">
          <Button
            variant="outline"
            size="sm"
            className="text-xs h-8 flex-1 sm:flex-initial"
            onClick={onCreateTemplate}
            aria-label="Criar novo template"
          >
            <Plus className="mr-1 h-3.5 w-3.5" aria-hidden="true" />
            Novo Template
          </Button>
          <Button
            variant="outline"
            size="sm"
            className="text-xs h-8 flex-1 sm:flex-initial"
            onClick={onManageCategories}
            aria-label="Gerenciar categorias"
          >
            <Tag className="mr-1 h-3.5 w-3.5" aria-hidden="true" />
            Categorias
          </Button>
        </div>
        <div className="flex flex-col sm:flex-row items-start sm:items-center gap-2 w-full sm:w-auto">
          <div className="relative w-full sm:w-auto">
            <Search
              className="absolute left-2 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-muted-foreground"
              aria-hidden="true"
            />
            <Input
              placeholder="Buscar templates..."
              value={searchQuery}
              onChange={(e) => onSearchQueryChange(e.target.value)}
              className="pl-8 h-8 text-xs w-full sm:w-[200px]"
              aria-label="Buscar templates"
            />
          </div>
          <div className="flex items-center gap-2 w-full sm:w-auto">
            <Filter className="h-3.5 w-3.5 text-muted-foreground" aria-hidden="true" />
            <select
              id="filter-category"
              className="h-8 rounded-md border border-input bg-background px-2 py-1 text-xs w-full sm:w-auto"
              value={filterCategory}
              onChange={(e) => onFilterCategoryChange(e.target.value)}
              aria-label="Filtrar por categoria"
            >
              <option value="todos">Todas as categorias</option>
              {categories.map((category) => (
                <option key={category} value={category}>
                  {category.charAt(0).toUpperCase() + category.slice(1)}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {templates.length === 0 ? (
        <div className="text-center py-6 sm:py-8">
          <div className="text-muted-foreground mb-2 text-sm">Nenhum template encontrado</div>
          <p className="text-xs sm:text-sm text-muted-foreground">
            {searchQuery ? "Tente ajustar sua busca ou filtros" : "Crie um novo template para começar"}
          </p>
        </div>
      ) : (
        <ScrollArea className="h-[300px] sm:h-[400px] pr-3 sm:pr-4">
          <div className="space-y-2 sm:space-y-3">
            {templates.map((template) => (
              <TemplateCard
                key={template.id}
                template={template}
                isSelected={selectedTemplate?.id === template.id}
                onSelect={onSelectTemplate}
                onEdit={onEditTemplate}
                onDelete={onDeleteTemplate}
                onCopy={onCopyContent}
                onUse={onUseTemplate}
              />
            ))}
          </div>
        </ScrollArea>
      )}

      {selectedTemplate && <TemplatePreview template={selectedTemplate} onUse={onUseTemplate} />}
    </div>
  )
}

