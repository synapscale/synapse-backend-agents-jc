/**
 * Theme types for the application
 * 
 * Defines the structure of themes used throughout the application,
 * particularly for styling nodes in the canvas and other UI elements.
 */

export type ThemeName = "default" | "colorful" | "minimal" | "dark" | "pastel"

/**
 * Node theme colors configuration for each category
 */
export type NodeThemeColors = {
  [key: string]: {
    background: string
    border: string
    text: string
    headerBg: string
  }
}

/**
 * Complete theme definition
 */
export interface Theme {
  name: ThemeName
  label: string
  nodeColors: NodeThemeColors
  canvasBg: string
  nodeStyle: {
    borderRadius: string
    shadowSize: string
  }
}

/**
 * Theme context type definition
 */
export type ThemeContextType = {
  currentTheme: Theme
  setTheme: (theme: ThemeName) => void
  availableThemes: Theme[]
}
