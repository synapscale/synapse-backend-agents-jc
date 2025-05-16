"use client"

import { useMemo } from "react"

import { useState, useEffect } from "react"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { TemplateList } from "@/components/templates/template-list"
import { TemplatePreview } from "@/components/templates/template-preview"
import { TemplateForm } from "@/components/templates/template-form"
import { CategorySelector } from "@/components/templates/category-selector" // This component needs to be integrated or path adjusted
import { CategoryManager } from "@/components/templates/category-manager" // This component needs to be integrated or path adjusted
import { useLocalStorage } from "@/hooks/use-local-storage"

// Template interface
export interface PromptTemplate {
  id: string
  name: string
  description: string
  content: string
  categories: string[]
  createdAt: string
  updatedAt: string
}

// Default templates
const DEFAULT_TEMPLATES: PromptTemplate[] = [
  {
    id: "1",
    name: "Assistente de Suporte Técnico",
    description: "Template para um assistente especializado em suporte técnico",
    content: `# Assistente de Suporte Técnico\n\nVocê é um assistente especializado em fornecer suporte técnico para produtos de tecnologia. Seu objetivo é ajudar os usuários a resolver problemas técnicos de forma clara e eficiente.\n\n## Capacidades:\n- Diagnosticar problemas técnicos com base nas descrições dos usuários\n- Fornecer instruções passo a passo para resolução de problemas\n- Explicar conceitos técnicos em linguagem simples\n- Recomendar recursos adicionais quando necessário\n\n## Comportamento:\n- Seja paciente e compreensivo com usuários de todos os níveis de conhecimento técnico\n- Faça perguntas para esclarecer o problema quando a descrição for vaga\n- Priorize soluções mais simples antes de sugerir procedimentos complexos\n- Confirme se o problema foi resolvido após fornecer uma solução`,
    categories: ["Suporte", "Geral"],
    createdAt: "2023-01-01T00:00:00.000Z",
    updatedAt: "2023-01-01T00:00:00.000Z",
  },
  {
    id: "2",
    name: "Assistente de Redação",
    description: "Template para um assistente especializado em redação e revisão de textos",
    content: `# Assistente de Redação e Revisão\n\nVocê é um assistente especializado em redação e revisão de textos. Seu objetivo é ajudar os usuários a melhorar a qualidade de seus textos, corrigindo erros e sugerindo melhorias.\n\n## Capacidades:\n- Revisar textos para corrigir erros gramaticais e ortográficos\n- Sugerir melhorias de clareza, coesão e coerência\n- Ajudar a adaptar o tom e estilo para diferentes públicos e contextos\n- Fornecer feedback construtivo sobre a estrutura do texto\n\n## Comportamento:\n- Seja detalhista na identificação de problemas no texto\n- Explique o motivo das correções e sugestões\n- Respeite o estilo e a voz do autor\n- Priorize a clareza e a precisão na comunicação`,
    categories: ["Redação", "Geral"],
    createdAt: "2023-01-02T00:00:00.000Z",
    updatedAt: "2023-01-02T00:00:00.000Z",
  },
  {
    id: "3",
    name: "Assistente de Pesquisa",
    description: "Template para um assistente especializado em pesquisa e análise de informações",
    content: `# Assistente de Pesquisa e Análise\n\nVocê é um assistente especializado em pesquisa e análise de informações. Seu objetivo é ajudar os usuários a encontrar, organizar e compreender informações sobre diversos tópicos.\n\n## Capacidades:\n- Sintetizar informações complexas em resumos claros e concisos\n- Organizar informações em estruturas lógicas e compreensíveis\n- Identificar padrões e tendências em conjuntos de dados\n- Formular perguntas relevantes para aprofundar a pesquisa\n\n## Comportamento:\n- Seja metódico e sistemático na abordagem de pesquisa\n- Cite fontes e referências quando disponíveis\n- Diferencie claramente entre fatos, opiniões e especulações\n- Reconheça limitações e incertezas nas informações disponíveis`,
    categories: ["Pesquisa", "Geral"],
    createdAt: "2023-01-03T00:00:00.000Z",
    updatedAt: "2023-01-03T00:00:00.000Z",
  },
]

// Default categories
const DEFAULT_CATEGORIES = ["Suporte", "Redação", "Pesquisa", "Marketing", "Desenvolvimento", "Geral"]

interface TemplatesModalProps {
  isOpen: boolean
  onClose: () => void
  onSelectTemplate: (template: PromptTemplate) => void
  currentPrompt?: string
}

export function TemplatesModal({ isOpen, onClose, onSelectTemplate, currentPrompt = "" }: TemplatesModalProps) {
  // Estados
  const [templates, setTemplates] = useLocalStorage<PromptTemplate[]>("prompt-templates", DEFAULT_TEMPLATES)
  const [categories, setCategories] = useLocalStorage<string[]>("template-categories", DEFAULT_CATEGORIES)
  const [selectedCategory, setSelectedCategory] = useState<string>("todos")
  const [selectedTemplate, setSelectedTemplate] = useState<PromptTemplate | null>(null)
  const [isCreating, setIsCreating] = useState(false)
  const [isManagingCategories, setIsManagingCategories] = useState(false)
  const [searchQuery, setSearchQuery] = useState("")

  // Resetar seleção quando o modal é aberto
  useEffect(() => {
    if (isOpen) {
      setSelectedTemplate(null)
      setIsCreating(false)
      setIsManagingCategories(false)
      setSelectedCategory("todos")
      setSearchQuery("")
    }
  }, [isOpen])

  // Filtrar templates por categoria e pesquisa
  const filteredTemplates = useMemo(() => {
    let filtered = templates

    if (selectedCategory !== "todos") {
      filtered = filtered.filter((template) => template.categories.includes(selectedCategory))
    }

    if (searchQuery) {
      filtered = filtered.filter(
        (template) =>
          template.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
          (template.description && template.description.toLowerCase().includes(searchQuery.toLowerCase())),
      )
    }

    return filtered
  }, [templates, selectedCategory, searchQuery])

  // Manipuladores
  const handleSelectTemplate = (template: PromptTemplate) => {
    setSelectedTemplate(template)
    setIsCreating(false)
  }

  const handleCreateTemplate = () => {
    setSelectedTemplate(null)
    setIsCreating(true)
  }

  const handleSaveTemplate = (template: PromptTemplate) => {
    if (template.id) {
      // Atualizar template existente
      setTemplates(templates.map((t) => (t.id === template.id ? { ...template, updatedAt: new Date().toISOString() } : t)))
    } else {
      // Criar novo template
      const newTemplate = {
        ...template,
        id: Date.now().toString(),
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      }
      setTemplates([...templates, newTemplate])
    }
    setIsCreating(false)
    setSelectedTemplate(null)
  }

  const handleDeleteTemplate = (id: string) => {
    setTemplates(templates.filter((t) => t.id !== id))
    setSelectedTemplate(null)
  }

  const handleUseTemplate = (template: PromptTemplate) => {
    onSelectTemplate(template)
    onClose()
  }

  const handleAddCategory = (category: string) => {
    if (!categories.includes(category)) {
      setCategories([...categories, category])
    }
  }

  const handleUpdateCategory = (oldCategory: string, newCategory: string) => {
    setCategories(categories.map((c) => (c === oldCategory ? newCategory : c)))
    setTemplates(
      templates.map((t) => ({
        ...t,
        categories: t.categories.map((cat) => (cat === oldCategory ? newCategory : cat)),
      })),
    )
    if (selectedCategory === oldCategory) {
      setSelectedCategory(newCategory)
    }
  }

  const handleDeleteCategory = (category: string) => {
    setCategories(categories.filter((c) => c !== category))
    // Atualizar templates que usam esta categoria
    setTemplates(
      templates.map((t) => ({
        ...t,
        categories: t.categories.filter((c) => c !== category),
      })),
    )
    if (selectedCategory === category) {
      setSelectedCategory("todos")
    }
  }

  const getTemplateCountsByCategory = () => {
    return templates.reduce((acc: Record<string, number>, template) => {
      template.categories.forEach((category) => {
        acc[category] = (acc[category] || 0) + 1
      })
      return acc
    }, {} as Record<string, number>)
  }

  const templateCounts = getTemplateCountsByCategory()

  const isValidTemplate = (template: Partial<PromptTemplate>) => {
    return !!template.name && !!template.content && !!template.categories && template.categories.length > 0
  }

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="sm:max-w-4xl max-h-[90vh] flex flex-col">
        <DialogHeader>
          <DialogTitle>
            {isManagingCategories
              ? "Gerenciar Categorias"
              : isCreating
                ? selectedTemplate?.id ? "Editar Template" : "Criar Novo Template"
                : selectedTemplate
                  ? "Detalhes do Template"
                  : "Biblioteca de Templates"}
          </DialogTitle>
        </DialogHeader>

        <div className="flex-1 overflow-hidden flex flex-col md:flex-row gap-4 pt-2">
          {isManagingCategories ? (
            <CategoryManager
              categories={categories}
              onAddCategory={handleAddCategory}
              onUpdateCategory={handleUpdateCategory}
              onDeleteCategory={handleDeleteCategory}
              onBack={() => setIsManagingCategories(false)}
              templateCounts={templateCounts}
            />
          ) : isCreating || (selectedTemplate && isCreating === false && selectedTemplate.id && templates.find(t => t.id === selectedTemplate.id)) ? (
            // Condition for showing TemplateForm for new or existing template editing
            <TemplateForm
              template={selectedTemplate || { categories: ["Geral"], content: currentPrompt }}
              onChange={(field, value) => {
                setSelectedTemplate((prev) => ({ ...(prev || {}), [field]: value } as PromptTemplate))
              }}
              onSubmit={() => {
                if (selectedTemplate && isValidTemplate(selectedTemplate)) {
                  handleSaveTemplate(selectedTemplate as PromptTemplate)
                }
              }}
              onCancel={() => {
                setIsCreating(false)
                setSelectedTemplate(null) // Clear selection on cancel
              }}
              categories={categories}
              onManageCategories={() => setIsManagingCategories(true)}
              isValid={selectedTemplate ? isValidTemplate(selectedTemplate) : false}
              isEdit={!!selectedTemplate?.id}
            />
          ) : (
            // Main view: Category list and Template list/preview
            <>
              <div className="md:w-1/3 flex flex-col border-r pr-4">
                <TemplateList
                  templates={filteredTemplates}
                  categories={categories} // Pass all categories for filter dropdown
                  selectedTemplate={selectedTemplate}
                  filterCategory={selectedCategory}
                  searchQuery={searchQuery}
                  onSelectTemplate={handleSelectTemplate}
                  onEditTemplate={(template) => {
                    setSelectedTemplate(template)
                    setIsCreating(true) // Set isCreating to true to show TemplateForm for editing
                  }}
                  onDeleteTemplate={handleDeleteTemplate}
                  onCopyContent={(content) => navigator.clipboard.writeText(content)}
                  onUseTemplate={handleUseTemplate}
                  onCreateTemplate={handleCreateTemplate}
                  onManageCategories={() => setIsManagingCategories(true)}
                  onFilterCategoryChange={(category) => setSelectedCategory(category)}
                  onSearchQueryChange={(query) => setSearchQuery(query)}
                />
              </div>
              <div className="md:w-2/3 flex flex-col overflow-hidden pl-4">
                {selectedTemplate && !isCreating ? (
                  <TemplatePreview template={selectedTemplate} onUse={handleUseTemplate} />
                ) : (
                  <div className="flex-1 flex items-center justify-center text-muted-foreground">
                    Selecione um template para ver a prévia ou crie um novo.
                  </div>
                )}
              </div>
            </>
          )}
        </div>
      </DialogContent>
    </Dialog>
  )
}

