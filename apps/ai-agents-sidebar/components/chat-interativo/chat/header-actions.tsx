/**
 * HeaderActions Component
 *
 * Displays action buttons in the chat header for creating new chats,
 * accessing settings, and other global actions.
 */
"use client"
import { useCallback } from "react"
import { PlusCircle, Settings, HelpCircle, Moon, Sun, Menu } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { useApp } from "@/contexts/app-context"
import type { BaseComponentProps } from "@/types/component-types"

/**
 * Props for the HeaderActions component
 */
export interface HeaderActionsProps extends BaseComponentProps {
  /**
   * Callback fired when the new chat button is clicked
   */
  onNewChat?: () => void

  /**
   * Callback fired when the settings button is clicked
   */
  onOpenSettings?: () => void

  /**
   * Callback fired when the help button is clicked
   */
  onOpenHelp?: () => void

  /**
   * Callback fired when the sidebar toggle button is clicked
   */
  onToggleSidebar?: () => void

  /**
   * Whether to show the new chat button
   * @default true
   */
  showNewChatButton?: boolean

  /**
   * Whether to show the settings button
   * @default true
   */
  showSettingsButton?: boolean

  /**
   * Whether to show the help button
   * @default true
   */
  showHelpButton?: boolean

  /**
   * Whether to show the theme toggle button
   * @default true
   */
  showThemeToggle?: boolean

  /**
   * Whether to show the sidebar toggle button
   * @default true
   */
  showSidebarToggle?: boolean

  /**
   * Size of the buttons
   * @default "sm"
   */
  size?: "sm" | "md" | "lg"

  /**
   * Variant of the new chat button
   * @default "default"
   */
  newChatButtonVariant?: "default" | "outline" | "ghost"

  /**
   * Text to display on the new chat button
   * @default "New Chat"
   */
  newChatButtonText?: string

  /**
   * Whether to show tooltips
   * @default true
   */
  showTooltips?: boolean
}

/**
 * HeaderActions component
 */
export default function HeaderActions({
  className = "",
  style,
  id,
  disabled = false,
  dataAttributes,
  onNewChat,
  onOpenSettings,
  onOpenHelp,
  onToggleSidebar,
  showNewChatButton = true,
  showSettingsButton = true,
  showHelpButton = true,
  showThemeToggle = true,
  showSidebarToggle = true,
  size = "sm",
  newChatButtonVariant = "default",
  newChatButtonText = "New Chat",
  showTooltips = true,
}: HeaderActionsProps) {
  // SECTION: Application context
  const { theme, setTheme, isSidebarOpen, setIsSidebarOpen } = useApp()

  // SECTION: Event handlers

  /**
   * Toggle between light and dark themes
   */
  const toggleTheme = useCallback(() => {
    setTheme(theme === "light" ? "dark" : "light")
  }, [theme, setTheme])

  /**
   * Toggle sidebar visibility
   */
  const toggleSidebar = useCallback(() => {
    setIsSidebarOpen(!isSidebarOpen)
    onToggleSidebar?.()
  }, [isSidebarOpen, setIsSidebarOpen, onToggleSidebar])

  // SECTION: Size mappings
  const sizeClasses = {
    sm: "h-8",
    md: "h-9",
    lg: "h-10",
  }

  const iconSizes = {
    sm: "h-4 w-4",
    md: "h-5 w-5",
    lg: "h-6 w-6",
  }

  // Prepare data attributes
  const allDataAttributes = {
    "data-component": "HeaderActions",
    "data-component-path": "@/components/chat/header-actions",
    ...(dataAttributes || {}),
  }

  // SECTION: Render
  return (
    <div className={`flex items-center space-x-2 ${className}`} style={style} id={id} {...allDataAttributes}>
      {/* New Chat Button */}
      {showNewChatButton &&
        (showTooltips ? (
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  variant={newChatButtonVariant}
                  size={size}
                  className={`${sizeClasses[size]} ${newChatButtonVariant === "default" ? "bg-primary hover:bg-primary/90" : ""}`}
                  onClick={onNewChat}
                  disabled={disabled}
                >
                  <PlusCircle className={`${iconSizes[size]} ${newChatButtonText ? "mr-2" : ""}`} />
                  {newChatButtonText}
                </Button>
              </TooltipTrigger>
              <TooltipContent>Start a new chat</TooltipContent>
            </Tooltip>
          </TooltipProvider>
        ) : (
          <Button
            variant={newChatButtonVariant}
            size={size}
            className={`${sizeClasses[size]} ${newChatButtonVariant === "default" ? "bg-primary hover:bg-primary/90" : ""}`}
            onClick={onNewChat}
            disabled={disabled}
          >
            <PlusCircle className={`${iconSizes[size]} ${newChatButtonText ? "mr-2" : ""}`} />
            {newChatButtonText}
          </Button>
        ))}

      {/* Theme Toggle Button */}
      {showThemeToggle &&
        (showTooltips ? (
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  variant="ghost"
                  size="icon"
                  className={`${sizeClasses[size]} rounded-full hover:bg-gray-100 dark:hover:bg-gray-700`}
                  onClick={toggleTheme}
                  disabled={disabled}
                >
                  {theme === "light" ? <Moon className={iconSizes[size]} /> : <Sun className={iconSizes[size]} />}
                </Button>
              </TooltipTrigger>
              <TooltipContent>{theme === "light" ? "Dark mode" : "Light mode"}</TooltipContent>
            </Tooltip>
          </TooltipProvider>
        ) : (
          <Button
            variant="ghost"
            size="icon"
            className={`${sizeClasses[size]} rounded-full hover:bg-gray-100 dark:hover:bg-gray-700`}
            onClick={toggleTheme}
            disabled={disabled}
          >
            {theme === "light" ? <Moon className={iconSizes[size]} /> : <Sun className={iconSizes[size]} />}
          </Button>
        ))}

      {/* Help Button */}
      {showHelpButton &&
        (showTooltips ? (
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  variant="ghost"
                  size="icon"
                  className={`${sizeClasses[size]} rounded-full hover:bg-gray-100 dark:hover:bg-gray-700`}
                  onClick={onOpenHelp}
                  disabled={disabled}
                >
                  <HelpCircle className={iconSizes[size]} />
                </Button>
              </TooltipTrigger>
              <TooltipContent>Help</TooltipContent>
            </Tooltip>
          </TooltipProvider>
        ) : (
          <Button
            variant="ghost"
            size="icon"
            className={`${sizeClasses[size]} rounded-full hover:bg-gray-100 dark:hover:bg-gray-700`}
            onClick={onOpenHelp}
            disabled={disabled}
          >
            <HelpCircle className={iconSizes[size]} />
          </Button>
        ))}

      {/* Settings Button */}
      {showSettingsButton && (
        <DropdownMenu>
          {showTooltips ? (
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <DropdownMenuTrigger asChild>
                    <Button
                      variant="ghost"
                      size="icon"
                      className={`${sizeClasses[size]} rounded-full hover:bg-gray-100 dark:hover:bg-gray-700`}
                      disabled={disabled}
                    >
                      <Settings className={iconSizes[size]} />
                    </Button>
                  </DropdownMenuTrigger>
                </TooltipTrigger>
                <TooltipContent>Settings</TooltipContent>
              </Tooltip>
            </TooltipProvider>
          ) : (
            <DropdownMenuTrigger asChild>
              <Button
                variant="ghost"
                size="icon"
                className={`${sizeClasses[size]} rounded-full hover:bg-gray-100 dark:hover:bg-gray-700`}
                disabled={disabled}
              >
                <Settings className={iconSizes[size]} />
              </Button>
            </DropdownMenuTrigger>
          )}

          <DropdownMenuContent align="end" className="w-48">
            <DropdownMenuItem onClick={onOpenSettings} disabled={disabled}>
              <Settings className="h-4 w-4 mr-2" />
              Settings
            </DropdownMenuItem>
            <DropdownMenuItem onClick={toggleTheme} disabled={disabled}>
              {theme === "light" ? (
                <>
                  <Moon className="h-4 w-4 mr-2" />
                  Dark mode
                </>
              ) : (
                <>
                  <Sun className="h-4 w-4 mr-2" />
                  Light mode
                </>
              )}
            </DropdownMenuItem>
            <DropdownMenuItem onClick={onOpenHelp} disabled={disabled}>
              <HelpCircle className="h-4 w-4 mr-2" />
              Help & FAQ
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      )}

      {/* Sidebar Toggle Button (Mobile) */}
      {showSidebarToggle &&
        (showTooltips ? (
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  variant="ghost"
                  size="icon"
                  className={`${sizeClasses[size]} rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 md:hidden`}
                  onClick={toggleSidebar}
                  disabled={disabled}
                >
                  <Menu className={iconSizes[size]} />
                </Button>
              </TooltipTrigger>
              <TooltipContent>Toggle sidebar</TooltipContent>
            </Tooltip>
          </TooltipProvider>
        ) : (
          <Button
            variant="ghost"
            size="icon"
            className={`${sizeClasses[size]} rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 md:hidden`}
            onClick={toggleSidebar}
            disabled={disabled}
          >
            <Menu className={iconSizes[size]} />
          </Button>
        ))}
    </div>
  )
}
