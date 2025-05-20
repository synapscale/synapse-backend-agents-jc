"use client"

import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"
import type { BaseComponentProps, CategoryProps } from "@/types/component-interfaces"

interface CategoryFilterProps extends BaseComponentProps, CategoryProps {
  allCategoriesText?: string
  showAllCategories?: boolean
  buttonVariant?: "default" | "outline" | "secondary"
  selectedButtonVariant?: "default" | "outline" | "secondary"
}

export function CategoryFilter({
  categories,
  selectedCategory,
  onSelectCategory,
  allCategoriesText = "Todas as categorias",
  showAllCategories = true,
  buttonVariant = "outline",
  selectedButtonVariant = "secondary",
  className,
  testId,
}: CategoryFilterProps) {
  return (
    <div className={cn("flex flex-wrap gap-2", className)} data-testid={testId}>
      {showAllCategories && (
        <Button
          variant={selectedCategory === null ? selectedButtonVariant : buttonVariant}
          size="sm"
          onClick={() => onSelectCategory(null)}
        >
          {allCategoriesText}
        </Button>
      )}
      {categories.map((category) => (
        <Button
          key={category.id}
          variant={selectedCategory === category.id ? selectedButtonVariant : buttonVariant}
          size="sm"
          onClick={() => onSelectCategory(category.id)}
        >
          {category.name}
        </Button>
      ))}
    </div>
  )
}
