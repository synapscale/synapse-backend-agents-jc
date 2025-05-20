"use client"
import { Check, Edit, Plus, Trash2, X } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import { useState } from "react"

interface CategoryManagerProps {
  categories: string[]
  onAddCategory: (category: string) => void
  onUpdateCategory: (oldCategory: string, newCategory: string) => void
  onDeleteCategory: (category: string) => void
  onBack: () => void
  templateCounts: Record<string, number>
}

export function CategoryManager({
  categories,
  onAddCategory,
  onUpdateCategory,
  onDeleteCategory,
  onBack,
  templateCounts,
}: CategoryManagerProps) {
  const [newCategory, setNewCategory] = useState("")
  const [editingCategory, setEditingCategory] = useState<{ original: string; new: string } | null>(null)

  const handleAddCategory = () => {
    if (!newCategory.trim()) return
    onAddCategory(newCategory.trim().toLowerCase())
    setNewCategory("")
  }

  const handleUpdateCategory = () => {
    if (!editingCategory || !editingCategory.new.trim()) return
    onUpdateCategory(editingCategory.original, editingCategory.new.trim().toLowerCase())
    setEditingCategory(null)
  }

  return (
    <div className="py-3 sm:py-4">
      <div className="flex items-center gap-2 mb-3 sm:mb-4">
        <Input
          placeholder="Nova categoria..."
          value={newCategory}
          onChange={(e) => setNewCategory(e.target.value)}
          className="flex-1 h-8 sm:h-9 text-sm"
          aria-label="Nome da nova categoria"
        />
        <Button
          onClick={handleAddCategory}
          disabled={!newCategory.trim()}
          size="sm"
          className="h-8 sm:h-9"
          aria-label="Adicionar nova categoria"
        >
          <Plus className="mr-1.5 h-3.5 w-3.5 sm:h-4 sm:w-4" aria-hidden="true" />
          <span className="text-xs sm:text-sm">Adicionar</span>
        </Button>
      </div>

      <div className="border rounded-md">
        <div className="py-2 px-3 sm:px-4 bg-muted/50 border-b text-xs sm:text-sm font-medium">
          Categorias Existentes
        </div>
        <ScrollArea className="h-[250px] sm:h-[300px]">
          <div className="p-3 sm:p-4 space-y-1.5 sm:space-y-2">
            {categories.map((category) => (
              <div key={category} className="flex items-center justify-between p-1.5 sm:p-2 border rounded-md group">
                {editingCategory && editingCategory.original === category ? (
                  <div className="flex items-center gap-1.5 sm:gap-2 flex-1">
                    <Input
                      value={editingCategory.new}
                      onChange={(e) => setEditingCategory({ ...editingCategory, new: e.target.value })}
                      className="h-7 sm:h-8 text-xs sm:text-sm"
                      autoFocus
                      aria-label={`Editar categoria ${category}`}
                    />
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={handleUpdateCategory}
                      className="h-7 w-7 sm:h-8 sm:w-8 p-0"
                      aria-label="Salvar alterações"
                    >
                      <Check className="h-3.5 w-3.5 sm:h-4 sm:w-4" aria-hidden="true" />
                    </Button>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => setEditingCategory(null)}
                      className="h-7 w-7 sm:h-8 sm:w-8 p-0"
                      aria-label="Cancelar edição"
                    >
                      <X className="h-3.5 w-3.5 sm:h-4 sm:w-4" aria-hidden="true" />
                    </Button>
                  </div>
                ) : (
                  <>
                    <div className="flex items-center gap-2">
                      <Badge variant="outline" className="bg-muted/30 text-xs">
                        {category}
                      </Badge>
                      <span className="text-xs text-muted-foreground">{templateCounts[category] || 0} templates</span>
                    </div>
                    <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                      <Button
                        size="sm"
                        variant="ghost"
                        className="h-7 w-7 sm:h-8 sm:w-8 p-0"
                        onClick={() => setEditingCategory({ original: category, new: category })}
                        disabled={category === "geral"} // Não permitir editar a categoria "geral"
                        aria-label={`Editar categoria ${category}`}
                      >
                        <Edit className="h-3.5 w-3.5 sm:h-4 sm:w-4" aria-hidden="true" />
                        <span className="sr-only">Editar</span>
                      </Button>
                      <Button
                        size="sm"
                        variant="ghost"
                        className="h-7 w-7 sm:h-8 sm:w-8 p-0 text-destructive hover:text-destructive"
                        onClick={() => onDeleteCategory(category)}
                        disabled={category === "geral"} // Não permitir excluir a categoria "geral"
                        aria-label={`Excluir categoria ${category}`}
                      >
                        <Trash2 className="h-3.5 w-3.5 sm:h-4 sm:w-4" aria-hidden="true" />
                        <span className="sr-only">Excluir</span>
                      </Button>
                    </div>
                  </>
                )}
              </div>
            ))}
          </div>
        </ScrollArea>
      </div>

      <div className="flex justify-end mt-4">
        <Button variant="outline" size="sm" className="w-full sm:w-auto h-9" onClick={onBack}>
          Voltar
        </Button>
      </div>
    </div>
  )
}
