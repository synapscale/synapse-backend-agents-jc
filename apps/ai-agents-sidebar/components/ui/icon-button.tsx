"use client"

import type React from "react"
import { cn } from "@/lib/utils"

interface IconButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  icon: React.ReactNode
  label: string
  variant?: "default" | "outline" | "ghost" | "link"
  size?: "xs" | "sm" | "md" | "lg" | "xl"
  displayMode?: "icon-only" | "icon-and-label"
  loading?: boolean
  className?: string
}

/**
 * IconButton component
 *
 * A button that displays an icon, optionally with a label.
 *
 * @example
 * ```tsx
 * <IconButton
 *   icon={<PlusIcon />}
 *   label="Add Item"
 *   onClick={handleAdd}
 *   variant="outline"
 * />
 * ```
 */
export function IconButton({
  icon,
  label,
  variant = "default",
  size = "md",
  displayMode = "icon-only",
  loading = false,
  className,
  ...props
}: IconButtonProps) {
  // Size classes
  const sizeClasses = {
    xs: "h-6 w-6 text-xs",
    sm: "h-8 w-8 text-sm",
    md: "h-10 w-10 text-base",
    lg: "h-12 w-12 text-lg",
    xl: "h-14 w-14 text-xl",
  }

  // Variant classes
  const variantClasses = {
    default: "bg-primary text-primary-foreground hover:bg-primary/90",
    outline: "border border-input bg-background hover:bg-accent hover:text-accent-foreground",
    ghost: "hover:bg-accent hover:text-accent-foreground",
    link: "text-primary underline-offset-4 hover:underline",
  }

  // Display mode classes
  const displayModeClasses = {
    "icon-only": "p-0",
    "icon-and-label": "flex items-center justify-center gap-1 px-3",
  }

  return (
    <button
      type="button"
      className={cn(
        "inline-flex items-center justify-center rounded-md font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none",
        displayMode === "icon-only" ? sizeClasses[size] : "",
        variantClasses[variant],
        displayModeClasses[displayMode],
        className,
      )}
      aria-label={label}
      disabled={loading || props.disabled}
      {...props}
    >
      {icon}
      {displayMode === "icon-and-label" && <span>{label}</span>}
      {loading && (
        <span className="absolute inset-0 flex items-center justify-center">
          <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            ></path>
          </svg>
        </span>
      )}
    </button>
  )
}
