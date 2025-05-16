"use client"

import { Check, Palette } from "lucide-react"
import { Button } from "@/components/ui/button"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { useTheme } from "@/contexts/theme-context"
import { useMemo } from "react"

/**
 * ThemeSelector Component
 *
 * Dropdown menu for selecting and changing the application theme.
 * Displays a preview of each theme's colors and indicates the currently selected theme.
 */
export function ThemeSelector() {
  const { currentTheme, setTheme, availableThemes } = useTheme()

  // Memoize the theme options to prevent unnecessary re-renders
  const themeOptions = useMemo(
    () =>
      availableThemes.map((theme) => (
        <DropdownMenuItem
          key={theme.name}
          onClick={() => setTheme(theme.name)}
          className="flex items-center justify-between"
        >
          <div className="flex items-center gap-2">
            <div className="flex gap-1">
              {Object.keys(theme.nodeColors)
                .slice(0, 4)
                .map((category) => (
                  <div
                    key={category}
                    className={`h-3 w-3 rounded-full ${theme.nodeColors[category].background} ${theme.nodeColors[category].border}`}
                    aria-hidden="true"
                  />
                ))}
            </div>
            <span>{theme.label}</span>
          </div>
          {currentTheme.name === theme.name && <Check className="h-4 w-4" aria-hidden="true" />}
        </DropdownMenuItem>
      )),
    [availableThemes, currentTheme.name, setTheme],
  )

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" size="sm" className="h-8 gap-1">
          <Palette className="h-4 w-4" aria-hidden="true" />
          <span>Tema: {currentTheme.label}</span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">{themeOptions}</DropdownMenuContent>
    </DropdownMenu>
  )
}
