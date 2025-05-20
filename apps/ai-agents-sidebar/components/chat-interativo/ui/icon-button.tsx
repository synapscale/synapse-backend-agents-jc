/**
 * IconButton Component
 *
 * A button with an icon and optional tooltip.
 *
 * @ai-pattern ui-component
 * Reusable button component with icon and tooltip support
 */
"use client"

import type React from "react"
import { forwardRef } from "react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"

/**
 * Props for the IconButton component
 */
export interface IconButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  /**
   * Icon to display in the button
   */
  icon: React.ReactNode

  /**
   * Optional tooltip text
   */
  tooltip?: string

  /**
   * Size of the button
   * @default "md"
   */
  size?: "sm" | "md" | "lg"

  /**
   * Button variant
   * @default "ghost"
   */
  variant?: "default" | "ghost" | "outline" | "secondary" | "destructive" | "link"

  /**
   * Whether the button is active
   * @default false
   */
  active?: boolean

  /**
   * Active class name
   * @default "bg-primary/10 text-primary"
   */
  activeClassName?: string
}

/**
 * IconButton component
 */
export const IconButton = forwardRef<HTMLButtonElement, IconButtonProps>(
  (
    {
      icon,
      tooltip,
      disabled = false,
      className = "",
      size = "md",
      variant = "ghost",
      active = false,
      activeClassName = "bg-primary/10 text-primary",
      onClick,
      ...props
    },
    ref,
  ) => {
    // Size classes for the button
    const sizeClasses = {
      sm: "h-7 w-7",
      md: "h-9 w-9",
      lg: "h-11 w-11",
    }

    // Combine classes
    const buttonClassName = cn(sizeClasses[size], "rounded-full", active && activeClassName, className)

    // Create button content
    const buttonContent = (
      <Button
        ref={ref}
        variant={variant}
        size="icon"
        onClick={onClick}
        disabled={disabled}
        className={buttonClassName}
        aria-pressed={active}
        {...props}
      >
        {icon}
      </Button>
    )

    // Add tooltip if provided
    if (tooltip) {
      return (
        <TooltipProvider>
          <Tooltip delayDuration={300}>
            <TooltipTrigger asChild>{buttonContent}</TooltipTrigger>
            <TooltipContent side="bottom">
              <p className="text-xs">{tooltip}</p>
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>
      )
    }

    return buttonContent
  },
)

IconButton.displayName = "IconButton"
