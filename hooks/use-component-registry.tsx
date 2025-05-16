/**
 * Component Registry Hook
 *
 * Provides functionality to register and track React components in the application.
 * This enables component discovery, selection, and inspection.
 */
"use client"

import { useEffect, useRef, useState, useCallback } from "react"

/**
 * Component information interface
 */
export interface ComponentInfo {
  id: string
  name: string
  path: string
  element: HTMLElement | null
  props?: Record<string, any>
  children?: ComponentInfo[]
}

// Global registry to store component information
const componentRegistry = new Map<string, ComponentInfo>()

/**
 * Generate a unique ID for components
 */
function generateId(): string {
  return `comp-${Math.random().toString(36).substring(2, 9)}`
}

/**
 * Hook to register a component in the system
 * @param name - Component name
 * @param path - Component path
 * @returns Component reference and ID
 */
export function useComponentRegistry(name?: string, path?: string) {
  const ref = useRef<HTMLElement>(null)
  const [id] = useState(() => generateId())
  const [isRegistered, setIsRegistered] = useState(false)

  // Register component on mount
  useEffect(() => {
    if (!name || !path) return

    if (ref.current) {
      try {
        // Create component info
        const componentInfo: ComponentInfo = {
          id,
          name,
          path,
          element: ref.current,
        }

        // Register component
        componentRegistry.set(id, componentInfo)

        // Add data attributes for easier detection
        ref.current.setAttribute("data-component", name)
        ref.current.setAttribute("data-component-path", path)
        ref.current.setAttribute("data-component-id", id)

        setIsRegistered(true)

        // Log registration in development
        if (process.env.NODE_ENV === "development") {
          console.log(`Component registered: ${name} (${id})`)
        }
      } catch (error) {
        console.error(`Error registering component ${name}:`, error)
      }
    }

    // Cleanup on unmount
    return () => {
      try {
        componentRegistry.delete(id)
        setIsRegistered(false)

        // Log unregistration in development
        if (process.env.NODE_ENV === "development") {
          console.log(`Component unregistered: ${name} (${id})`)
        }
      } catch (error) {
        console.error(`Error unregistering component ${name}:`, error)
      }
    }
  }, [id, name, path])

  return {
    ref,
    componentId: id,
    isRegistered,
  }
}

/**
 * Get all registered components
 * @returns Array of component information
 */
export function getRegisteredComponents(): ComponentInfo[] {
  return Array.from(componentRegistry.values())
}

/**
 * Find a component by element
 * @param element - DOM element
 * @returns Component information or undefined
 */
export function findComponentByElement(element: HTMLElement): ComponentInfo | undefined {
  try {
    // Check if element has a component ID
    const componentId = element.getAttribute("data-component-id")
    if (componentId && componentRegistry.has(componentId)) {
      return componentRegistry.get(componentId)
    }

    // Check if element is a child of a registered component
    for (const info of componentRegistry.values()) {
      if (info.element && info.element.contains(element)) {
        return info
      }
    }

    return undefined
  } catch (error) {
    console.error("Error finding component by element:", error)
    return undefined
  }
}

/**
 * Register a component manually
 * @param component - Component information
 * @returns Component ID
 */
export function registerComponent(component: ComponentInfo): string {
  try {
    if (!component.id) {
      component.id = generateId()
    }

    componentRegistry.set(component.id, component)

    // Add data attributes if element exists
    if (component.element) {
      component.element.setAttribute("data-component", component.name)
      component.element.setAttribute("data-component-path", component.path)
      component.element.setAttribute("data-component-id", component.id)
    }

    return component.id
  } catch (error) {
    console.error(`Error registering component ${component.name}:`, error)
    throw error
  }
}

/**
 * Unregister a component manually
 * @param id - Component ID
 */
export function unregisterComponent(id: string): void {
  try {
    componentRegistry.delete(id)
  } catch (error) {
    console.error(`Error unregistering component ${id}:`, error)
    throw error
  }
}

/**
 * Hook to access the component registry
 * @returns Component registry state and functions
 */
export function useComponentRegistryManager() {
  const [components, setComponents] = useState<ComponentInfo[]>([])

  // Update components state
  const refreshComponents = useCallback(() => {
    setComponents(Array.from(componentRegistry.values()))
  }, [])

  // Define the register component function directly in the hook
  const registerComponentCallback = useCallback(
    (component: ComponentInfo): string => {
      try {
        if (!component.id) {
          component.id = generateId()
        }

        componentRegistry.set(component.id, component)

        // Add data attributes if element exists
        if (component.element) {
          component.element.setAttribute("data-component", component.name || "UnknownComponent")
          component.element.setAttribute("data-component-path", component.path || "unknown-path")
          component.element.setAttribute("data-component-id", component.id)
        }

        refreshComponents()
        return component.id
      } catch (error) {
        console.error(`Error registering component ${component.name || "unknown"}:`, error)
        return generateId() // Return a fallback ID
      }
    },
    [refreshComponents],
  )

  // Unregister a component manually
  const unregisterComponentCallback = useCallback(
    (id: string) => {
      try {
        unregisterComponent(id)
        refreshComponents()
      } catch (error) {
        console.error(`Error unregistering component ${id}:`, error)
      }
    },
    [refreshComponents],
  )

  // Get a component by ID
  const getComponent = useCallback((id: string): ComponentInfo | undefined => {
    try {
      return componentRegistry.get(id)
    } catch (error) {
      console.error(`Error getting component ${id}:`, error)
      return undefined
    }
  }, [])

  // Update components when the registry changes
  useEffect(() => {
    refreshComponents()

    // Set up a periodic refresh to catch any missed updates
    const intervalId = setInterval(refreshComponents, 2000)

    return () => {
      clearInterval(intervalId)
    }
  }, [refreshComponents])

  return {
    components,
    registerComponent: registerComponentCallback,
    unregisterComponent: unregisterComponentCallback,
    findComponentByElement,
    getComponent,
    refreshComponents,
  }
}
