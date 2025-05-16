"use client"

import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import { z } from "zod"
import { useEffect } from "react"
import { cn } from "@/lib/utils"

import { Button } from "@/components/ui/button"
import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetFooter } from "@/components/ui/sheet"
import type { ComponentBase, Loadable } from "@/types/core/component-base"

/**
 * Form validation schema for node data
 */
const formSchema = z.object({
  /**
   * Node name - must be at least 2 characters
   */
  name: z.string().min(2, {
    message: "O nome deve ter pelo menos 2 caracteres.",
  }),

  /**
   * Node description - must be at least 5 characters
   */
  description: z.string().min(5, {
    message: "A descrição deve ter pelo menos 5 caracteres.",
  }),

  /**
   * Node category - required
   */
  category: z.string({
    required_error: "Selecione uma categoria.",
  }),

  /**
   * Node configuration in JSON format - optional
   */
  config: z.string().optional(),
})

/**
 * Type for form values
 */
export type NodeFormValues = z.infer<typeof formSchema>

/**
 * Props for the NodeForm component
 */
interface NodeFormProps extends ComponentBase, Loadable {
  /**
   * Whether the form sheet is open
   */
  open: boolean

  /**
   * Callback fired when the open state changes
   */
  onOpenChange: (open: boolean) => void

  /**
   * Initial form data
   */
  initialData?: NodeFormValues

  /**
   * Initial category to select
   */
  initialCategory?: string

  /**
   * Callback fired when the form is submitted
   */
  onSubmit?: (data: NodeFormValues) => void

  /**
   * Whether the form is in edit mode
   * @default false
   */
  isEditing?: boolean

  /**
   * Available node categories
   */
  nodeCategories: Array<{ id: string; name: string }>

  /**
   * Title for the form sheet
   * If not provided, will use "Editar Node" or "Criar Novo Node" based on isEditing
   */
  title?: string

  /**
   * Whether to reset the form when closed
   * @default true
   */
  resetOnClose?: boolean

  /**
   * Whether the form is in a readonly state
   * @default false
   */
  readonly?: boolean

  /**
   * Custom submit button text
   * If not provided, will use "Atualizar" or "Salvar" based on isEditing
   */
  submitText?: string

  /**
   * Custom cancel button text
   * @default "Cancelar"
   */
  cancelText?: string

  /**
   * Whether to show the config field
   * @default true
   */
  showConfigField?: boolean

  /**
   * Default JSON config template
   * @default '{"inputs": [], "outputs": []}'
   */
  defaultConfigTemplate?: string
}

/**
 * NodeForm Component
 *
 * A form for creating or editing nodes, displayed in a slide-out sheet.
 * Uses React Hook Form with Zod validation.
 *
 * @example
 * ```tsx
 * <NodeForm
 *   open={isFormOpen}
 *   onOpenChange={setIsFormOpen}
 *   initialData={selectedNode}
 *   isEditing={!!selectedNode}
 *   nodeCategories={categories}
 *   onSubmit={handleSubmitNode}
 * />
 * ```
 */
export function NodeForm({
  // Required props
  open,
  onOpenChange,
  nodeCategories,

  // Optional data props
  initialData,
  initialCategory,

  // State props
  isEditing = false,
  isLoading = false,
  readonly = false,
  resetOnClose = true,

  // Customization props
  title,
  submitText,
  cancelText = "Cancelar",
  loadingText = "Salvando...",
  showConfigField = true,
  defaultConfigTemplate = '{"inputs": [], "outputs": []}',

  // Event handlers
  onSubmit,

  // Accessibility and testing
  className,
  testId,
  id,

  // Other props
  ...otherProps
}: NodeFormProps) {
  // Initialize form with validation
  const form = useForm<NodeFormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: initialData || {
      name: "",
      description: "",
      category: initialCategory || "",
      config: "",
    },
  })

  // Update form when initial data changes
  useEffect(() => {
    if (open && initialData) {
      form.reset(initialData)
    } else if (open && initialCategory && !form.getValues("category")) {
      form.setValue("category", initialCategory)
    }
  }, [open, initialData, initialCategory, form])

  // Reset form when modal is closed
  useEffect(() => {
    if (!open && resetOnClose && !isEditing) {
      form.reset({
        name: "",
        description: "",
        category: initialCategory || "",
        config: "",
      })
    }
  }, [open, form, initialCategory, isEditing, resetOnClose])

  // Handle form submission
  function handleSubmit(values: NodeFormValues) {
    onSubmit?.(values)
    onOpenChange(false)
  }

  // Determine form title
  const formTitle = title || (isEditing ? "Editar Node" : "Criar Novo Node")

  // Determine submit button text
  const submitButtonText = submitText || (isEditing ? "Atualizar" : "Salvar")

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent className={cn("sm:max-w-[500px]", className)} data-testid={testId} id={id} {...otherProps}>
        <SheetHeader>
          <SheetTitle>{formTitle}</SheetTitle>
        </SheetHeader>

        <Form {...form}>
          <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-6 pt-6">
            <FormField
              control={form.control}
              name="name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Nome</FormLabel>
                  <FormControl>
                    <Input
                      placeholder="Nome do node"
                      {...field}
                      disabled={isLoading || readonly}
                      aria-required="true"
                    />
                  </FormControl>
                  <FormDescription>Um nome descritivo para o seu node.</FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="description"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Descrição</FormLabel>
                  <FormControl>
                    <Textarea
                      placeholder="Descreva o que este node faz"
                      className="resize-none"
                      {...field}
                      disabled={isLoading || readonly}
                      aria-required="true"
                    />
                  </FormControl>
                  <FormDescription>Uma breve descrição da funcionalidade do node.</FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="category"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Categoria</FormLabel>
                  <Select onValueChange={field.onChange} value={field.value} disabled={isLoading || readonly}>
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="Selecione uma categoria" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      {nodeCategories.map((category) => (
                        <SelectItem key={category.id} value={category.id}>
                          {category.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <FormDescription>A categoria ajuda a organizar os nodes.</FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />

            {showConfigField && (
              <FormField
                control={form.control}
                name="config"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Configuração (JSON)</FormLabel>
                    <FormControl>
                      <Textarea
                        placeholder={defaultConfigTemplate}
                        className="font-mono h-32"
                        {...field}
                        disabled={isLoading || readonly}
                      />
                    </FormControl>
                    <FormDescription>Configuração avançada do node em formato JSON.</FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />
            )}

            <SheetFooter className="flex justify-end space-x-2">
              <Button variant="outline" type="button" onClick={() => onOpenChange(false)} disabled={isLoading}>
                {cancelText}
              </Button>
              <Button type="submit" disabled={isLoading || readonly}>
                {isLoading ? loadingText : submitButtonText}
              </Button>
            </SheetFooter>
          </form>
        </Form>
      </SheetContent>
    </Sheet>
  )
}
