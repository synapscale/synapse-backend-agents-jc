"use client"
import { Save } from "lucide-react"
import { Button } from "@/components/ui/button"
import { InputField } from "@/components/form/input-field"
import { Textarea } from "@/components/ui/textarea"
import { FormField } from "@/components/form/form-field"
import { CategorySelector } from "@/components/templates/category-selector"
import type { PromptTemplate } from "@/components/templates-modal"

interface TemplateFormProps {
  template: Partial<PromptTemplate>
  onChange: (field: keyof PromptTemplate, value: any) => void
  onSubmit: () => void
  onCancel: () => void
  onManageCategories: () => void
  categories: string[]
  isValid: boolean
  isEdit?: boolean
}

export function TemplateForm({
  template,
  onChange,
  onSubmit,
  onCancel,
  onManageCategories,
  categories,
  isValid,
  isEdit = false,
}: TemplateFormProps) {
  return (
    <div className="grid gap-3 sm:gap-4 py-3 sm:py-4">
      <InputField
        id="template-name"
        label="Nome do Template"
        value={template.name || ""}
        onChange={(value) => onChange("name", value)}
        placeholder="Ex: Assistente de Vendas"
        required
      />

      <InputField
        id="template-description"
        label="Descrição"
        value={template.description || ""}
        onChange={(value) => onChange("description", value)}
        placeholder="Descreva o propósito deste template"
      />

      <CategorySelector
        selectedCategories={template.categories || []}
        availableCategories={categories}
        onAddCategory={(category) => {
          const currentCategories = template.categories || []
          if (!currentCategories.includes(category)) {
            onChange("categories", [...currentCategories, category])
          }
        }}
        onRemoveCategory={(category) => {
          const currentCategories = template.categories || []
          if (currentCategories.length > 1) {
            onChange(
              "categories",
              currentCategories.filter((c) => c !== category),
            )
          }
        }}
        onManageCategories={onManageCategories}
      />

      <FormField label="Conteúdo do Template" htmlFor="template-content" required>
        <Textarea
          id="template-content"
          value={template.content || ""}
          onChange={(e) => onChange("content", e.target.value)}
          placeholder="# Título do Prompt&#10;&#10;Você é um assistente especializado em...&#10;&#10;## Capacidades:&#10;- Capacidade 1&#10;- Capacidade 2"
          className="min-h-[150px] sm:min-h-[200px] font-mono text-xs sm:text-sm"
        />
      </FormField>

      <div className="flex flex-col sm:flex-row justify-end gap-2 sm:gap-3 mt-2">
        <Button variant="outline" size="sm" className="w-full sm:w-auto h-9" onClick={onCancel}>
          Cancelar
        </Button>
        <Button size="sm" className="w-full sm:w-auto h-9" onClick={onSubmit} disabled={!isValid}>
          <Save className="mr-1.5 h-3.5 w-3.5 sm:h-4 sm:w-4" aria-hidden="true" />
          {isEdit ? "Atualizar Template" : "Salvar Template"}
        </Button>
      </div>
    </div>
  )
}
