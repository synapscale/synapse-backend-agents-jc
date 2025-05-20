"use client"

import type React from "react"
import { useRef, useEffect, useState } from "react"
import { cn } from "@/lib/utils"
import { FormField } from "@/components/form/form-field"
import type { PromptEditorProps } from "@/types/component-params"

/**
 * A specialized editor for AI prompts with syntax highlighting and tools
 *
 * This component provides a textarea with enhanced features for editing AI prompts,
 * including auto-resizing, tab handling, and template selection.
 *
 * @example
 * ```tsx
 * <PromptEditor
 *   value={prompt}
 *   onChange={setPrompt}
 *   onBlur={validatePrompt}
 *   error={errors.prompt}
 *   label="Agent Prompt"
 *   required
 *   onSelectTemplate={() => openTemplatesModal()}
 * />
 * ```
 *
 * @param props - Component properties
 * @returns React component
 */
export function PromptEditor({
  // Required props
  value,
  onChange,

  // Optional props with defaults
  onSelectTemplate,
  error,
  className,
  minHeight = "200px",
  label,
  required = false,
  onBlur,
  placeholder = "# Título do Prompt\n\nVocê é um assistente especializado em...\n\n## Capacidades:\n- Capacidade 1\n- Capacidade 2",
  readOnly = false,
  maxLength,
  showCharCount = true,
  autoFocus = false,
  showTemplateButton = true,

  // Accessibility props
  id,
  testId,
  ariaLabel,
}: PromptEditorProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const [isFocused, setIsFocused] = useState(false)
  const showCharacterCount = maxLength && showCharCount

  // Auto-resize textarea
  useEffect(() => {
    const textarea = textareaRef.current
    if (!textarea) return

    const adjustHeight = () => {
      textarea.style.height = "auto"
      textarea.style.height = `${Math.max(textarea.scrollHeight, Number.parseInt(minHeight))}px`
    }

    adjustHeight()
    window.addEventListener("resize", adjustHeight)

    return () => {
      window.removeEventListener("resize", adjustHeight)
    }
  }, [value, minHeight])

  // Tab key handling for indentation
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Tab") {
      e.preventDefault()
      const start = e.currentTarget.selectionStart
      const end = e.currentTarget.selectionEnd

      // Insert tab at cursor position
      const newValue = value.substring(0, start) + "  " + value.substring(end)
      onChange(newValue)

      // Move cursor after the inserted tab
      setTimeout(() => {
        if (textareaRef.current) {
          textareaRef.current.selectionStart = textareaRef.current.selectionEnd = start + 2
        }
      }, 0)
    }
  }

  const inputId = id || "prompt-editor"

  return (
    <FormField
      label={label}
      error={error}
      required={required}
      id={inputId}
      headerRight={
        onSelectTemplate && showTemplateButton ? (
          <button
            type="button"
            onClick={onSelectTemplate}
            className="text-sm text-purple-600 hover:text-purple-800 font-medium"
            aria-label="Usar template de prompt"
          >
            Usar template
          </button>
        ) : null
      }
      testId={testId}
    >
      <div
        className={cn(
          "relative rounded-md border transition-colors",
          isFocused ? "border-purple-500 ring-1 ring-purple-500" : "border-input",
          error && "border-red-300 ring-1 ring-red-500",
          className,
        )}
      >
        <textarea
          ref={textareaRef}
          id={inputId}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onFocus={() => setIsFocused(true)}
          onBlur={() => {
            setIsFocused(false)
            onBlur?.()
          }}
          onKeyDown={handleKeyDown}
          className={cn(
            "flex w-full rounded-md border-0 bg-transparent px-3 py-2 text-sm shadow-none focus-visible:outline-none focus-visible:ring-0 disabled:cursor-not-allowed disabled:opacity-50 font-mono",
          )}
          style={{ minHeight, resize: "vertical" }}
          placeholder={placeholder}
          required={required}
          aria-invalid={!!error}
          aria-describedby={error ? `${inputId}-error` : undefined}
          aria-label={ariaLabel || label || "Prompt editor"}
          spellCheck="false"
          data-gramm="false"
          readOnly={readOnly}
          maxLength={maxLength}
          autoFocus={autoFocus}
          data-testid={`${inputId}-textarea`}
        />
        {showCharacterCount && (
          <div
            className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-muted-foreground pointer-events-none"
            aria-live="polite"
            aria-atomic="true"
          >
            {value.length}/{maxLength}
          </div>
        )}
      </div>
    </FormField>
  )
}
