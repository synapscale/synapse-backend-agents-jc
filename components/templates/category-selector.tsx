"use client"
import { Check, Plus, Tag, X } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { FormField } from "@/components/form/form-field"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { Command, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList } from "@/components/ui/command"
import { useDisclosure } from "@/hooks/use-disclosure"

interface CategorySelectorProps {
  selectedCategories: string[]
  availableCategories: string[]
  onAddCategory: (category: string) => void
  onRemoveCategory: (category: string) => void
  onManageCategories: () => void
}

export function CategorySelector({
  selectedCategories,
  availableCategories,
  onAddCategory,
  onRemoveCategory,
  onManageCategories,
}: CategorySelectorProps) {
  const popover = useDisclosure()

  return (
    <FormField
      label="Categorias"
      headerRight={
        <Button variant="ghost" size="sm" className="h-7 sm:h-8 px-2 text-xs" onClick={onManageCategories}>
          <Tag className="h-3 w-3 sm:h-3.5 sm:w-3.5 mr-1" aria-hidden="true" />
          Gerenciar Categorias
        </Button>
      }
    >
      <div className="flex flex-col gap-2">
        <div className="flex flex-wrap gap-1.5 sm:gap-2 mb-2" role="group" aria-label="Categorias selecionadas">
          {selectedCategories.map((category) => (
            <Badge key={category} variant="secondary" className="px-1.5 sm:px-2 py-0.5 sm:py-1 text-xs">
              {category}
              <button
                className="ml-1 text-muted-foreground hover:text-foreground p-0.5"
                onClick={() => onRemoveCategory(category)}
                aria-label={`Remover categoria ${category}`}
                disabled={selectedCategories.length <= 1}
              >
                <X className="h-2.5 w-2.5 sm:h-3 sm:w-3" aria-hidden="true" />
              </button>
            </Badge>
          ))}
        </div>

        <Popover open={popover.isOpen} onOpenChange={popover.toggle}>
          <PopoverTrigger asChild>
            <Button
              variant="outline"
              size="sm"
              className="w-full justify-start h-8 sm:h-9 text-xs sm:text-sm"
              aria-label="Adicionar categoria"
            >
              <Plus className="mr-1.5 h-3.5 w-3.5 sm:h-4 sm:w-4" aria-hidden="true" />
              Adicionar categoria
            </Button>
          </PopoverTrigger>
          <PopoverContent className="p-0" align="start" side="bottom">
            <Command>
              <CommandInput placeholder="Buscar categoria..." className="h-9" />
              <CommandList className="max-h-[200px] sm:max-h-[250px]">
                <CommandEmpty>Nenhuma categoria encontrada.</CommandEmpty>
                <CommandGroup>
                  {availableCategories.map((category) => (
                    <CommandItem
                      key={category}
                      onSelect={() => {
                        onAddCategory(category)
                        popover.close()
                      }}
                      disabled={selectedCategories.includes(category)}
                      className="py-1.5 sm:py-2"
                    >
                      <Check
                        className={`mr-1.5 h-3.5 w-3.5 sm:h-4 sm:w-4 ${
                          selectedCategories.includes(category) ? "opacity-100" : "opacity-0"
                        }`}
                        aria-hidden="true"
                      />
                      {category}
                    </CommandItem>
                  ))}
                </CommandGroup>
              </CommandList>
            </Command>
          </PopoverContent>
        </Popover>
      </div>
    </FormField>
  )
}

