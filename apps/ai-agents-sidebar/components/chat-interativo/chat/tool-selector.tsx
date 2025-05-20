/**
 * ToolSelector Component
 *
 * A component for selecting tools to use with the AI assistant.
 * Displays available tools in categories and allows searching and selecting from recent tools.
 */
"use client"

import type React from "react"

import { useState, useMemo, useCallback } from "react"
import {
  ChevronDown,
  Search,
  Globe,
  ImageIcon,
  FileText,
  BarChart2,
  Twitter,
  BookOpen,
  MessageCircle,
  MessageSquare,
  Newspaper,
  Briefcase,
  Instagram,
  Facebook,
  Clock,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Input } from "@/components/ui/input"
import { useApp } from "@/contexts/app-context"
import type { BaseComponentProps } from "@/types/component-types"
import type { Tool } from "@/types/chat"

/**
 * Tool category types
 */
export type ToolCategory = "main" | "social" | "productivity" | "development" | "other"

/**
 * Props for the ToolSelector component
 */
export interface ToolSelectorProps extends BaseComponentProps {
  /**
   * List of available tools to display
   * If not provided, default tools will be used
   */
  tools?: Tool[]

  /**
   * Callback fired when a tool is selected
   * @param tool The selected tool
   */
  onToolSelect?: (tool: Tool) => void

  /**
   * Size of the selector button
   * @default "sm"
   */
  size?: "sm" | "md" | "lg"

  /**
   * Width of the popover content
   * @default "64"
   */
  contentWidth?: string

  /**
   * Maximum height of the scroll area
   * @default "80"
   */
  maxHeight?: string

  /**
   * Whether to show the search input
   * @default true
   */
  showSearch?: boolean

  /**
   * Whether to show the tabs for all/recent tools
   * @default true
   */
  showTabs?: boolean

  /**
   * Whether to show tool descriptions
   * @default true
   */
  showDescriptions?: boolean

  /**
   * Whether to show tool badges (new, paid, etc.)
   * @default true
   */
  showBadges?: boolean

  /**
   * Whether to group tools by category
   * @default true
   */
  groupByCategory?: boolean

  /**
   * Default tab to show
   * @default "all"
   */
  defaultTab?: "all" | "recent"

  /**
   * Placeholder text for the search input
   * @default "Search tools..."
   */
  searchPlaceholder?: string

  /**
   * Text to display when no tools are found
   * @default "No tools found"
   */
  emptyStateText?: string

  /**
   * Text to display when no recent tools are found
   * @default "No recent tools"
   */
  noRecentToolsText?: string

  /**
   * Custom icon for the selector button
   * If not provided, the selected tool's icon will be used
   */
  buttonIcon?: React.ReactNode

  /**
   * Custom label for the selector button
   * If not provided, the selected tool's name will be used
   */
  buttonLabel?: string
}

/**
 * Default tools available in the selector
 */
export const DEFAULT_TOOLS: Tool[] = [
  // Main tools
  {
    id: "no-tools",
    name: "No Tools",
    description: "Basic interaction without external tools",
    icon: <ChevronDown className="h-4 w-4" />,
    type: "custom",
    category: "main",
  },
  {
    id: "gpt-search",
    name: "GPT Search",
    description: "Search the web using GPT",
    icon: <Search className="h-4 w-4" />,
    type: "search",
    category: "main",
  },
  {
    id: "internet",
    name: "Internet",
    description: "Access to real-time web searches",
    icon: <Globe className="h-4 w-4" />,
    type: "search",
    category: "main",
  },
  {
    id: "image-generation",
    name: "Image Generation",
    description: "Generate images from text descriptions",
    icon: <ImageIcon className="h-4 w-4" />,
    type: "custom",
    isNew: true,
    isPaid: true,
    category: "main",
  },
  {
    id: "manage-files",
    name: "Manage Files",
    description: "Upload and analyze files",
    icon: <FileText className="h-4 w-4" />,
    type: "file",
    isNew: true,
    category: "main",
  },
  {
    id: "deep-analysis",
    name: "Deep Analysis",
    description: "In-depth analysis of data and text",
    icon: <BarChart2 className="h-4 w-4" />,
    type: "custom",
    isTrial: true,
    category: "main",
  },

  // Social media and websites
  {
    id: "twitter",
    name: "Twitter",
    description: "Access Twitter/X data",
    icon: <Twitter className="h-4 w-4" />,
    type: "api",
    category: "social",
  },
  {
    id: "wikipedia",
    name: "Wikipedia",
    description: "Search and query Wikipedia",
    icon: <BookOpen className="h-4 w-4" />,
    type: "api",
    category: "social",
  },
  {
    id: "quora",
    name: "Quora",
    description: "Access Quora questions and answers",
    icon: <MessageCircle className="h-4 w-4" />,
    type: "api",
    category: "social",
  },
  {
    id: "reddit",
    name: "Reddit",
    description: "Access Reddit content and discussions",
    icon: <MessageSquare className="h-4 w-4" />,
    type: "api",
    category: "social",
  },
  {
    id: "medium",
    name: "Medium",
    description: "Access Medium articles",
    icon: <Newspaper className="h-4 w-4" />,
    type: "api",
    category: "social",
  },
  {
    id: "linkedin",
    name: "LinkedIn",
    description: "Access LinkedIn data",
    icon: <Briefcase className="h-4 w-4" />,
    type: "api",
    category: "social",
  },
  {
    id: "instagram",
    name: "Instagram",
    description: "Access Instagram content",
    icon: <Instagram className="h-4 w-4" />,
    type: "api",
    category: "social",
  },
  {
    id: "facebook",
    name: "Facebook",
    description: "Access Facebook data",
    icon: <Facebook className="h-4 w-4" />,
    type: "api",
    category: "social",
  },
]

/**
 * Category display names
 */
export const CATEGORY_NAMES: Record<string, string> = {
  main: "Main Tools",
  social: "Social Media",
  productivity: "Productivity",
  development: "Development",
  other: "Other Tools",
}

/**
 * ToolSelector component
 */
export default function ToolSelector({
  className = "",
  style,
  id,
  disabled = false,
  dataAttributes,
  tools = DEFAULT_TOOLS,
  onToolSelect,
  size = "sm",
  contentWidth = "64",
  maxHeight = "80",
  showSearch = true,
  showTabs = true,
  showDescriptions = true,
  showBadges = true,
  groupByCategory = true,
  defaultTab = "all",
  searchPlaceholder = "Search tools...",
  emptyStateText = "No tools found",
  noRecentToolsText = "No recent tools",
  buttonIcon,
  buttonLabel,
}: ToolSelectorProps) {
  // SECTION: Local state
  const [isOpen, setIsOpen] = useState(false)
  const [searchQuery, setSearchQuery] = useState("")
  const [activeTab, setActiveTab] = useState<"all" | "recent">(defaultTab)

  // SECTION: Application context
  const { selectedTool, setSelectedTool, userPreferences } = useApp()

  // SECTION: Derived data

  /**
   * Find the currently selected tool object
   */
  const selectedToolObj = useMemo(() => {
    return tools.find((tool) => tool.name === selectedTool) || tools[0]
  }, [tools, selectedTool])

  /**
   * Filter tools based on search query
   */
  const filteredTools = useMemo(() => {
    if (!searchQuery.trim()) return tools

    const query = searchQuery.toLowerCase()
    return tools.filter(
      (tool) =>
        tool.name.toLowerCase().includes(query) ||
        (tool.description && tool.description.toLowerCase().includes(query)) ||
        (tool.category && tool.category.toLowerCase().includes(query)),
    )
  }, [tools, searchQuery])

  /**
   * Group tools by category
   */
  const toolsByCategory = useMemo(() => {
    if (!groupByCategory) {
      return { all: filteredTools }
    }

    return filteredTools.reduce(
      (acc, tool) => {
        const category = tool.category || "other"
        if (!acc[category]) {
          acc[category] = []
        }
        acc[category].push(tool)
        return acc
      },
      {} as Record<string, Tool[]>,
    )
  }, [filteredTools, groupByCategory])

  /**
   * Check if there are recent tools
   */
  const hasRecentTools = userPreferences?.recentTools && userPreferences.recentTools.length > 0

  /**
   * Get recent tools
   */
  const recentTools = useMemo(() => {
    if (!hasRecentTools) return []

    return userPreferences.recentTools
      .map((toolName) => tools.find((t) => t.name === toolName))
      .filter((tool): tool is Tool => !!tool)
  }, [tools, userPreferences.recentTools, hasRecentTools])

  // SECTION: Event handlers

  /**
   * Handle tool selection
   */
  const handleSelectTool = useCallback(
    (tool: Tool) => {
      setSelectedTool(tool.name)
      onToolSelect?.(tool)
      setIsOpen(false)
    },
    [setSelectedTool, onToolSelect],
  )

  /**
   * Handle tab change
   */
  const handleTabChange = useCallback((value: string) => {
    setActiveTab(value as "all" | "recent")
    setSearchQuery("")
  }, [])

  // Prepare data attributes
  const allDataAttributes = {
    "data-component": "ToolSelector",
    "data-component-path": "@/components/chat/tool-selector",
    ...(dataAttributes || {}),
  }

  // SECTION: Render
  return (
    <Popover open={isOpen} onOpenChange={setIsOpen}>
      {/* Trigger button */}
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          size={size}
          className={`text-xs flex items-center gap-1 ${
            size === "sm" ? "h-8" : size === "md" ? "h-9" : "h-10"
          } bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700 hover:border-primary/30 hover:bg-primary/5 dark:hover:bg-primary/10 transition-colors duration-200 rounded-full ${className}`}
          style={style}
          id={id}
          disabled={disabled}
          {...allDataAttributes}
        >
          {buttonIcon || (selectedToolObj.icon && <span className="mr-1">{selectedToolObj.icon}</span>)}
          {buttonLabel || selectedTool}
          <ChevronDown className="h-3 w-3 ml-1 text-gray-500 dark:text-gray-400" />
        </Button>
      </PopoverTrigger>

      {/* Popover content */}
      <PopoverContent
        className={`w-${contentWidth} p-0 border border-gray-100 dark:border-gray-700 shadow-lg rounded-xl bg-white dark:bg-gray-800 transition-colors duration-200`}
        align="start"
        sideOffset={4}
      >
        {showTabs ? (
          <Tabs defaultValue={defaultTab} value={activeTab} onValueChange={handleTabChange}>
            {/* Header with search and tabs */}
            <div className="border-b border-gray-100 dark:border-gray-700 px-3 py-2">
              {/* Search input */}
              {showSearch && (
                <div className="relative mb-2">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400 dark:text-gray-500" />
                  <Input
                    placeholder={searchPlaceholder}
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-9 h-9 text-sm rounded-full bg-gray-50 dark:bg-gray-700 border-gray-100 dark:border-gray-600 focus:border-primary/30 focus:ring-primary/20"
                  />
                </div>
              )}

              {/* Tabs */}
              <TabsList className="w-full grid grid-cols-2 h-9 rounded-full bg-gray-100 dark:bg-gray-700 p-1">
                <TabsTrigger
                  value="all"
                  className="rounded-full data-[state=active]:bg-white dark:data-[state=active]:bg-gray-600 data-[state=active]:text-primary data-[state=active]:shadow-sm"
                >
                  All
                </TabsTrigger>
                <TabsTrigger
                  value="recent"
                  className="rounded-full data-[state=active]:bg-white dark:data-[state=active]:bg-gray-600 data-[state=active]:text-primary data-[state=active]:shadow-sm"
                >
                  Recent
                </TabsTrigger>
              </TabsList>
            </div>

            {/* "All" tab content */}
            <TabsContent value="all" className="mt-0">
              <ScrollArea className={`h-${maxHeight} scrollbar-thin`}>
                {Object.keys(toolsByCategory).length === 0 ? (
                  <div className="p-4 text-center text-gray-500 dark:text-gray-400">{emptyStateText}</div>
                ) : (
                  Object.keys(toolsByCategory).map((category) => (
                    <div key={category} className="py-2">
                      {/* Category title */}
                      {groupByCategory && (
                        <div className="px-3 py-1 text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                          {CATEGORY_NAMES[category] || category}
                        </div>
                      )}

                      {/* Tools in this category */}
                      <div className="space-y-0.5">
                        {toolsByCategory[category].map((tool) => (
                          <button
                            key={tool.id}
                            className={`w-full px-3 py-2 text-left hover:bg-gray-50 dark:hover:bg-gray-700 flex items-center justify-between transition-colors duration-200 ${
                              tool.name === selectedTool ? "bg-primary/5 dark:bg-primary/10" : ""
                            }`}
                            onClick={() => handleSelectTool(tool)}
                            disabled={disabled}
                          >
                            {/* Tool info */}
                            <div className="flex items-center">
                              <span className="w-6 h-6 flex items-center justify-center bg-gray-100 dark:bg-gray-700 rounded-md text-gray-600 dark:text-gray-300 mr-2">
                                {tool.icon}
                              </span>
                              <div>
                                <span className="text-sm text-gray-800 dark:text-gray-200 block">{tool.name}</span>
                                {showDescriptions && tool.description && (
                                  <span className="text-xs text-gray-500 dark:text-gray-400 block truncate max-w-[180px]">
                                    {tool.description}
                                  </span>
                                )}
                              </div>
                            </div>

                            {/* Badges */}
                            {showBadges && (
                              <div className="flex items-center space-x-1">
                                {tool.isNew && (
                                  <span className="text-xs bg-green-50 dark:bg-green-900/30 text-green-600 dark:text-green-400 px-1.5 py-0.5 rounded-full">
                                    New
                                  </span>
                                )}
                                {tool.isPaid && (
                                  <span className="text-xs bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 px-1.5 py-0.5 rounded-full">
                                    $
                                  </span>
                                )}
                                {tool.isTrial && (
                                  <span className="text-xs bg-purple-50 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400 px-1.5 py-0.5 rounded-full">
                                    Trial
                                  </span>
                                )}
                              </div>
                            )}
                          </button>
                        ))}
                      </div>
                    </div>
                  ))
                )}
              </ScrollArea>
            </TabsContent>

            {/* "Recent" tab content */}
            <TabsContent value="recent" className="mt-0">
              <ScrollArea className={`h-${maxHeight} scrollbar-thin`}>
                {!hasRecentTools ? (
                  <div className="text-center text-gray-500 dark:text-gray-400 py-12 flex flex-col items-center">
                    <Clock className="h-12 w-12 text-gray-300 dark:text-gray-600 mb-3" />
                    <p>{noRecentToolsText}</p>
                    <p className="text-xs mt-1 max-w-[250px]">Tools you use will appear here for quick access</p>
                  </div>
                ) : (
                  <div className="py-2 space-y-0.5">
                    {recentTools.map((tool) => (
                      <button
                        key={tool.id}
                        className={`w-full px-3 py-2 text-left hover:bg-gray-50 dark:hover:bg-gray-700 flex items-center justify-between transition-colors duration-200 ${
                          tool.name === selectedTool ? "bg-primary/5 dark:bg-primary/10" : ""
                        }`}
                        onClick={() => handleSelectTool(tool)}
                        disabled={disabled}
                      >
                        {/* Tool info */}
                        <div className="flex items-center">
                          <span className="w-6 h-6 flex items-center justify-center bg-gray-100 dark:bg-gray-700 rounded-md text-gray-600 dark:text-gray-300 mr-2">
                            {tool.icon}
                          </span>
                          <div>
                            <span className="text-sm text-gray-800 dark:text-gray-200 block">{tool.name}</span>
                            {showDescriptions && tool.description && (
                              <span className="text-xs text-gray-500 dark:text-gray-400 block truncate max-w-[180px]">
                                {tool.description}
                              </span>
                            )}
                          </div>
                        </div>

                        {/* Badges */}
                        {showBadges && (
                          <div className="flex items-center space-x-1">
                            {tool.isNew && (
                              <span className="text-xs bg-green-50 dark:bg-green-900/30 text-green-600 dark:text-green-400 px-1.5 py-0.5 rounded-full">
                                New
                              </span>
                            )}
                            {tool.isPaid && (
                              <span className="text-xs bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 px-1.5 py-0.5 rounded-full">
                                $
                              </span>
                            )}
                            {tool.isTrial && (
                              <span className="text-xs bg-purple-50 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400 px-1.5 py-0.5 rounded-full">
                                Trial
                              </span>
                            )}
                          </div>
                        )}
                      </button>
                    ))}
                  </div>
                )}
              </ScrollArea>
            </TabsContent>
          </Tabs>
        ) : (
          // Simple view without tabs
          <div>
            {/* Search input */}
            {showSearch && (
              <div className="relative px-3 py-2 border-b border-gray-100 dark:border-gray-700">
                <Search className="absolute left-6 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400 dark:text-gray-500" />
                <Input
                  placeholder={searchPlaceholder}
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-9 h-9 text-sm rounded-full bg-gray-50 dark:bg-gray-700 border-gray-100 dark:border-gray-600 focus:border-primary/30 focus:ring-primary/20"
                />
              </div>
            )}

            {/* Tools list */}
            <ScrollArea className={`h-${maxHeight} scrollbar-thin`}>
              {Object.keys(toolsByCategory).length === 0 ? (
                <div className="p-4 text-center text-gray-500 dark:text-gray-400">{emptyStateText}</div>
              ) : (
                Object.keys(toolsByCategory).map((category) => (
                  <div key={category} className="py-2">
                    {/* Category title */}
                    {groupByCategory && (
                      <div className="px-3 py-1 text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">
                        {CATEGORY_NAMES[category] || category}
                      </div>
                    )}

                    {/* Tools in this category */}
                    <div className="space-y-0.5">
                      {toolsByCategory[category].map((tool) => (
                        <button
                          key={tool.id}
                          className={`w-full px-3 py-2 text-left hover:bg-gray-50 dark:hover:bg-gray-700 flex items-center justify-between transition-colors duration-200 ${
                            tool.name === selectedTool ? "bg-primary/5 dark:bg-primary/10" : ""
                          }`}
                          onClick={() => handleSelectTool(tool)}
                          disabled={disabled}
                        >
                          {/* Tool info */}
                          <div className="flex items-center">
                            <span className="w-6 h-6 flex items-center justify-center bg-gray-100 dark:bg-gray-700 rounded-md text-gray-600 dark:text-gray-300 mr-2">
                              {tool.icon}
                            </span>
                            <div>
                              <span className="text-sm text-gray-800 dark:text-gray-200 block">{tool.name}</span>
                              {showDescriptions && tool.description && (
                                <span className="text-xs text-gray-500 dark:text-gray-400 block truncate max-w-[180px]">
                                  {tool.description}
                                </span>
                              )}
                            </div>
                          </div>

                          {/* Badges */}
                          {showBadges && (
                            <div className="flex items-center space-x-1">
                              {tool.isNew && (
                                <span className="text-xs bg-green-50 dark:bg-green-900/30 text-green-600 dark:text-green-400 px-1.5 py-0.5 rounded-full">
                                  New
                                </span>
                              )}
                              {tool.isPaid && (
                                <span className="text-xs bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 px-1.5 py-0.5 rounded-full">
                                  $
                                </span>
                              )}
                              {tool.isTrial && (
                                <span className="text-xs bg-purple-50 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400 px-1.5 py-0.5 rounded-full">
                                  Trial
                                </span>
                              )}
                            </div>
                          )}
                        </button>
                      ))}
                    </div>
                  </div>
                ))
              )}
            </ScrollArea>
          </div>
        )}
      </PopoverContent>
    </Popover>
  )
}
