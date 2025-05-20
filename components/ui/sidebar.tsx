"use client"

import * as React from "react"

interface SidebarContextType {
  isOpen: boolean
  toggleSidebar: () => void
  closeSidebar: () => void
  activeSection: string | null;
  setActiveSection: (section: string | null) => void;
}

const SidebarContext = React.createContext<SidebarContextType | undefined>(undefined)

export function SidebarProvider({ children }: { children: React.ReactNode }) {
  const [isOpen, setIsOpen] = React.useState(false)
  const [activeSection, setActiveSection] = React.useState<string | null>(null)

  const toggleSidebar = React.useCallback(() => {
    setIsOpen((prev) => !prev)
  }, [])

  const closeSidebar = React.useCallback(() => {
    setIsOpen(false)
  }, [])

  return (
    <SidebarContext.Provider value={{ 
      isOpen, 
      toggleSidebar, 
      closeSidebar,
      activeSection,
      setActiveSection
    }}>
      {children}
    </SidebarContext.Provider>
  )
}

export function useSidebar() {
  const context = React.useContext(SidebarContext)
  if (context === undefined) {
    throw new Error("useSidebar must be used within a SidebarProvider")
  }
  return context
}

export default {
  SidebarProvider,
  useSidebar
}
