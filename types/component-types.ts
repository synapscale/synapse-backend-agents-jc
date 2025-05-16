/**
 * Shared component types
 *
 * This file contains common types and interfaces used across multiple components
 * to ensure consistency and reduce duplication.
 */

import type React from "react"

/**
 * Standard size options for UI components
 */
export type ComponentSize = "xs" | "sm" | "md" | "lg" | "xl"

/**
 * Standard color variant options
 */
export type ColorVariant =
  | "primary"
  | "secondary"
  | "success"
  | "danger"
  | "warning"
  | "info"
  | "light"
  | "dark"
  | "muted"

/**
 * Standard position options
 */
export type Position = "top" | "right" | "bottom" | "left"

/**
 * Standard alignment options
 */
export type Alignment = "start" | "center" | "end"

/**
 * Standard status options
 */
export type Status = "idle" | "loading" | "success" | "error"

/**
 * Base component props that most components should extend
 */
export interface BaseComponentProps {
  /**
   * Optional CSS class name to apply to the component
   */
  className?: string

  /**
   * Optional inline style object
   */
  style?: React.CSSProperties

  /**
   * Optional ID for the component
   */
  id?: string

  /**
   * Whether the component is disabled
   * @default false
   */
  disabled?: boolean

  /**
   * Data attributes to apply to the component
   */
  dataAttributes?: Record<string, string>

  /**
   * ARIA attributes for accessibility
   */
  ariaAttributes?: Record<string, string>
}

/**
 * Props for components that can be clicked
 */
export interface ClickableProps {
  /**
   * Function called when the component is clicked
   * @param event The click event
   */
  onClick?: (event: React.MouseEvent) => void

  /**
   * Function called when the component receives focus
   * @param event The focus event
   */
  onFocus?: (event: React.FocusEvent) => void

  /**
   * Function called when the component loses focus
   * @param event The blur event
   */
  onBlur?: (event: React.FocusEvent) => void
}

/**
 * Props for components that can have a loading state
 */
export interface LoadableProps {
  /**
   * Whether the component is in a loading state
   * @default false
   */
  isLoading?: boolean

  /**
   * Custom loading indicator component
   */
  loadingIndicator?: React.ReactNode
}

/**
 * Props for components that can be animated
 */
export interface AnimatableProps {
  /**
   * Whether to enable animations
   * @default true
   */
  animated?: boolean

  /**
   * Animation duration in milliseconds
   * @default 300
   */
  animationDuration?: number

  /**
   * Animation timing function
   * @default "ease"
   */
  animationEasing?: string
}

/**
 * Props for components that can have tooltips
 */
export interface TooltipProps {
  /**
   * Tooltip content to display
   */
  tooltip?: React.ReactNode

  /**
   * Position of the tooltip relative to the component
   * @default "top"
   */
  tooltipPosition?: Position

  /**
   * Delay before showing the tooltip in milliseconds
   * @default 500
   */
  tooltipDelay?: number
}

/**
 * Props for components that can have badges
 */
export interface BadgeProps {
  /**
   * Badge content to display
   */
  badge?: React.ReactNode

  /**
   * Position of the badge relative to the component
   * @default "top-right"
   */
  badgePosition?: `${Position}-${Position}`

  /**
   * Color variant for the badge
   * @default "primary"
   */
  badgeVariant?: ColorVariant
}
