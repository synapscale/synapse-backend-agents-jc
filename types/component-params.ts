import type React from "react"
/**
 * Base component parameters that all components should implement
 * @template T - The type of the component's ref element
 */
export interface BaseComponentParams<T = HTMLDivElement> {
  /**
   * CSS class name to apply to the component
   * @default ""
   */
  className?: string

  /**
   * Inline styles to apply to the component
   */
  style?: React.CSSProperties

  /**
   * Unique identifier for the component
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
   * Ref object for the component
   */
  ref?: React.Ref<T>

  /**
   * ARIA attributes for accessibility
   */
  ariaAttributes?: Record<string, string>

  /**
   * Whether the component should be rendered with a focus ring when focused
   * @default true
   */
  focusable?: boolean

  /**
   * Tab index for the component
   */
  tabIndex?: number

  /**
   * Whether the component should be rendered with a hover effect
   * @default true
   */
  interactive?: boolean
}

/**
 * Parameters for components that can be in a loading state
 */
export interface LoadingStateParams {
  /**
   * Whether the component is in a loading state
   * @default false
   */
  isLoading?: boolean

  /**
   * Text to display when the component is loading
   * @default "Loading..."
   */
  loadingText?: string

  /**
   * Component to display when the component is loading
   * If provided, loadingText will be ignored
   */
  loadingComponent?: React.ReactNode

  /**
   * Whether to disable the component when it's loading
   * @default true
   */
  disableWhileLoading?: boolean

  /**
   * Animation to use for the loading state
   * @default "pulse"
   */
  loadingAnimation?: "pulse" | "spin" | "bounce" | "none"
}

/**
 * Parameters for components that can have a theme
 */
export interface ThemeableParams {
  /**
   * Theme variant for the component
   * @default "default"
   */
  variant?: "default" | "primary" | "secondary" | "destructive" | "outline" | "ghost" | "link"

  /**
   * Size variant for the component
   * @default "default"
   */
  size?: "sm" | "default" | "lg" | "xl"

  /**
   * Color scheme for the component
   * @default "primary"
   */
  colorScheme?: "primary" | "secondary" | "success" | "warning" | "danger" | "info" | "neutral"

  /**
   * Whether the component should adapt to the current theme
   * @default true
   */
  adaptToTheme?: boolean
}

/**
 * Parameters for components that can have a tooltip
 */
export interface TooltipParams {
  /**
   * Tooltip text to display when hovering over the component
   */
  tooltip?: string

  /**
   * Delay before showing the tooltip in milliseconds
   * @default 700
   */
  tooltipDelay?: number

  /**
   * Position of the tooltip relative to the component
   * @default "top"
   */
  tooltipPosition?: "top" | "right" | "bottom" | "left"

  /**
   * Whether the tooltip should be disabled
   * @default false
   */
  tooltipDisabled?: boolean
}

/**
 * Parameters for components that can have an icon
 */
export interface IconParams {
  /**
   * Icon to display in the component
   */
  icon?: React.ReactNode

  /**
   * Position of the icon relative to the component's content
   * @default "left"
   */
  iconPosition?: "left" | "right"

  /**
   * Size of the icon relative to the component's text
   * @default "default"
   */
  iconSize?: "sm" | "default" | "lg"

  /**
   * Whether the icon should be animated
   * @default false
   */
  animateIcon?: boolean

  /**
   * Type of animation for the icon
   * @default "none"
   */
  iconAnimation?: "spin" | "pulse" | "bounce" | "none"
}

/**
 * Parameters for components that can have a badge
 */
export interface BadgeParams {
  /**
   * Badge text to display on the component
   */
  badge?: string | number

  /**
   * Position of the badge relative to the component
   * @default "top-right"
   */
  badgePosition?: "top-left" | "top-right" | "bottom-left" | "bottom-right"

  /**
   * Color scheme for the badge
   * @default "primary"
   */
  badgeColorScheme?: "primary" | "secondary" | "success" | "warning" | "danger" | "info" | "neutral"

  /**
   * Maximum value to display in the badge
   * If the badge value is a number and exceeds this value, it will be displayed as "{maxBadgeValue}+"
   * @default 99
   */
  maxBadgeValue?: number
}

/**
 * Parameters for components that can have a label
 */
export interface LabelParams {
  /**
   * Label text to display for the component
   */
  label?: string

  /**
   * Position of the label relative to the component
   * @default "top"
   */
  labelPosition?: "top" | "right" | "bottom" | "left"

  /**
   * Whether the label should be hidden visually but still accessible to screen readers
   * @default false
   */
  hideLabel?: boolean

  /**
   * Whether the label is required
   * @default false
   */
  required?: boolean
}

/**
 * Parameters for components that can have a description
 */
export interface DescriptionParams {
  /**
   * Description text to display for the component
   */
  description?: string

  /**
   * Position of the description relative to the component
   * @default "bottom"
   */
  descriptionPosition?: "top" | "right" | "bottom" | "left"

  /**
   * Whether the description should be hidden visually but still accessible to screen readers
   * @default false
   */
  hideDescription?: boolean
}

/**
 * Parameters for components that can have an error state
 */
export interface ErrorStateParams {
  /**
   * Whether the component is in an error state
   * @default false
   */
  hasError?: boolean

  /**
   * Error message to display when the component is in an error state
   */
  errorMessage?: string

  /**
   * Position of the error message relative to the component
   * @default "bottom"
   */
  errorMessagePosition?: "top" | "right" | "bottom" | "left"
}

/**
 * Parameters for components that can be animated
 */
export interface AnimationParams {
  /**
   * Whether the component should be animated
   * @default true
   */
  animated?: boolean

  /**
   * Animation to use for the component
   * @default "fade"
   */
  animation?: "fade" | "slide" | "scale" | "none"

  /**
   * Duration of the animation in milliseconds
   * @default 300
   */
  animationDuration?: number

  /**
   * Delay before starting the animation in milliseconds
   * @default 0
   */
  animationDelay?: number

  /**
   * Easing function to use for the animation
   * @default "ease"
   */
  animationEasing?: "ease" | "linear" | "ease-in" | "ease-out" | "ease-in-out"
}

/**
 * Parameters for components that can have a responsive behavior
 */
export interface ResponsiveParams {
  /**
   * Whether the component should be hidden on mobile devices
   * @default false
   */
  hideOnMobile?: boolean

  /**
   * Whether the component should be hidden on tablet devices
   * @default false
   */
  hideOnTablet?: boolean

  /**
   * Whether the component should be hidden on desktop devices
   * @default false
   */
  hideOnDesktop?: boolean

  /**
   * Whether the component should adapt its size based on the viewport
   * @default true
   */
  responsive?: boolean
}

/**
 * Parameters for components that can have a hover state
 */
export interface HoverStateParams {
  /**
   * Whether the component should show a hover effect
   * @default true
   */
  showHoverEffect?: boolean

  /**
   * Color to use for the hover effect
   * @default "primary"
   */
  hoverColor?: "primary" | "secondary" | "success" | "warning" | "danger" | "info" | "neutral"

  /**
   * Effect to use for the hover state
   * @default "highlight"
   */
  hoverEffect?: "highlight" | "glow" | "scale" | "none"
}

/**
 * Parameters for components that can have a focus state
 */
export interface FocusStateParams {
  /**
   * Whether the component should show a focus ring when focused
   * @default true
   */
  showFocusRing?: boolean

  /**
   * Color to use for the focus ring
   * @default "primary"
   */
  focusRingColor?: "primary" | "secondary" | "success" | "warning" | "danger" | "info" | "neutral"

  /**
   * Whether the component should be auto-focused when mounted
   * @default false
   */
  autoFocus?: boolean
}

/**
 * Parameters for components that can have a transition
 */
export interface TransitionParams {
  /**
   * Whether the component should have a transition effect
   * @default true
   */
  transition?: boolean

  /**
   * Duration of the transition in milliseconds
   * @default 200
   */
  transitionDuration?: number

  /**
   * Properties that should be transitioned
   * @default ["all"]
   */
  transitionProperties?: string[]

  /**
   * Easing function to use for the transition
   * @default "ease"
   */
  transitionEasing?: "ease" | "linear" | "ease-in" | "ease-out" | "ease-in-out"
}
