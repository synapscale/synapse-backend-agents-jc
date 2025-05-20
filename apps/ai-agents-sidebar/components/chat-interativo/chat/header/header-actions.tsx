"use client"

import { Menu, PlusCircle, Moon, Sun, Code, Maximize2, Minimize2, Settings } from "lucide-react"
import { HeaderButton } from "./header-button"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { useApp } from "@/contexts/app-context"

interface HeaderActionsProps {
  onNewChat: () => void
  onToggleSidebar: () => void
  showComponentSelector?: boolean
  onToggleComponentSelector?: () => void
  isMobile?: boolean
}

export function HeaderActions({
  onNewChat,
  onToggleSidebar,
  showComponentSelector,
  onToggleComponentSelector,
  isMobile = false,
}: HeaderActionsProps) {
  const { theme, setTheme, showConfig, setShowConfig, focusMode, setFocusMode } = useApp()

  const toggleTheme = () => setTheme(theme === "light" ? "dark" : "light")

  return (
    <div className="flex items-center">
      {isMobile && (
        <>
          <HeaderButton
            icon={<Menu className="h-5 w-5 text-gray-600 dark:text-gray-300" />}
            onClick={onToggleSidebar}
            tooltip="Toggle sidebar"
            className="md:hidden mr-2"
          />
          <HeaderButton
            icon={<PlusCircle className="h-5 w-5 text-gray-600 dark:text-gray-300" />}
            onClick={onNewChat}
            tooltip="New conversation"
            className="md:hidden"
          />
        </>
      )}

      <HeaderButton
        icon={
          theme === "light" ? (
            <Moon className="h-5 w-5 text-gray-600 dark:text-gray-300" />
          ) : (
            <Sun className="h-5 w-5 text-gray-600 dark:text-gray-300" />
          )
        }
        onClick={toggleTheme}
        tooltip={theme === "light" ? "Dark mode" : "Light mode"}
        className="mr-1"
      />

      <HeaderButton
        icon={
          focusMode ? (
            <Maximize2 className="h-5 w-5 text-gray-600 dark:text-gray-300" />
          ) : (
            <Minimize2 className="h-5 w-5 text-gray-600 dark:text-gray-300" />
          )
        }
        onClick={() => setFocusMode(!focusMode)}
        tooltip={focusMode ? "Exit focus mode" : "Enter focus mode"}
        className="mr-1"
      />

      {onToggleComponentSelector && (
        <HeaderButton
          icon={<Code className="h-5 w-5 text-gray-600 dark:text-gray-300" />}
          onClick={onToggleComponentSelector}
          tooltip={showComponentSelector ? "Hide component selector" : "Show component selector"}
          active={showComponentSelector}
          className="mr-1"
        />
      )}

      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <HeaderButton
            icon={<Settings className="h-5 w-5 text-gray-600 dark:text-gray-300" />}
            tooltip="Settings"
            className="mr-2"
          />
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" className="w-56">
          <DropdownMenuItem onClick={() => setShowConfig(!showConfig)}>
            {showConfig ? "Hide" : "Show"} chat settings
          </DropdownMenuItem>
          <DropdownMenuItem onClick={toggleTheme}>{theme === "light" ? "Dark mode" : "Light mode"}</DropdownMenuItem>
          <DropdownMenuItem onClick={() => setFocusMode(!focusMode)}>
            {focusMode ? "Exit focus mode" : "Enter focus mode"}
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  )
}
