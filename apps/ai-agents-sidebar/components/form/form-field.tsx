import type * as React from "react"
import { cn } from "@/lib/utils"
import { Label } from "@/components/ui/label"

export interface FormFieldProps extends React.HTMLAttributes<HTMLDivElement> {
  className?: string
  children?: React.ReactNode
  label?: string
  name?: string
  error?: string
  required?: boolean
  helperText?: string
  id?: string
  headerRight?: React.ReactNode
}

/**
 * FormField component
 *
 * A wrapper for form inputs that provides consistent styling and layout,
 * including label, error message, and helper text.
 *
 * @example
 * \`\`\`tsx
 * <FormField
 *   label="Email Address"
 *   name="email"
 *   required
 *   error={errors.email}
 *   helperText="We'll never share your email with anyone else."
 * >
 *   <input type="email" name="email" />
 * </FormField>
 * \`\`\`
 */
export const FormField: React.FC<FormFieldProps> = ({
  className,
  children,
  label,
  name,
  error,
  required = false,
  helperText,
  id,
  headerRight,
  ...props
}) => {
  const inputId = id || name

  return (
    <div className={cn("mb-4", className)} {...props}>
      <div className="flex items-center justify-between">
        {label && (
          <Label htmlFor={inputId} className="mb-1 block text-sm font-medium text-gray-700">
            {label}
            {required && <span className="ml-1 text-red-500">*</span>}
          </Label>
        )}
        {headerRight}
      </div>
      {children}
      {helperText && !error && <p className="mt-1 text-sm text-gray-500">{helperText}</p>}
      {error && (
        <p className="mt-1 text-sm text-red-600" id={`${inputId}-error`}>
          {error}
        </p>
      )}
    </div>
  )
}
