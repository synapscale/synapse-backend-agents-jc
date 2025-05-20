"use client"

import type React from "react"

import { forwardRef, useState } from "react"
import { FormField } from "./form-field"
import { Input } from "@/components/ui/input"
import { cn } from "@/lib/utils"

interface InputFieldProps {
  id?: string
  name?: string
  label?: string
  value?: string
  onChange?: (value: string) => void
  placeholder?: string
  type?: string
  required?: boolean
  error?: string
  helperText?: string
  className?: string
  disabled?: boolean
  maxLength?: number
  autoComplete?: string
  autoFocus?: boolean
}

export const InputField = forwardRef<HTMLInputElement, InputFieldProps>(
  (
    {
      id,
      name,
      label,
      value = "",
      onChange,
      placeholder,
      type = "text",
      required = false,
      error,
      helperText,
      className,
      disabled = false,
      maxLength,
      autoComplete,
      autoFocus = false,
      ...props
    },
    ref,
  ) => {
    const inputId = id || name
    const [isFocused, setIsFocused] = useState(false)
    const showCharCount = maxLength && type === "text"

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      onChange?.(e.target.value)
    }

    return (
      <FormField label={label} name={name} error={error} required={required} helperText={helperText} id={inputId}>
        <div className="relative">
          <Input
            ref={ref}
            id={inputId}
            name={name}
            type={type}
            value={value}
            onChange={handleChange}
            onFocus={() => setIsFocused(true)}
            onBlur={() => setIsFocused(false)}
            placeholder={placeholder}
            disabled={disabled}
            maxLength={maxLength}
            autoComplete={autoComplete}
            autoFocus={autoFocus}
            className={cn(
              isFocused && "border-purple-500 ring-1 ring-purple-500",
              error && "border-red-300 focus-visible:ring-red-500",
              showCharCount && "pr-16",
              className,
            )}
            aria-invalid={!!error}
            aria-describedby={error ? `${inputId}-error` : helperText ? `${inputId}-helper` : undefined}
            required={required}
            {...props}
          />
          {showCharCount && (
            <div className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-muted-foreground pointer-events-none">
              {value.length}/{maxLength}
            </div>
          )}
        </div>
      </FormField>
    )
  },
)

InputField.displayName = "InputField"
