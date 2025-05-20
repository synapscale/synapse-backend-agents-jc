"use client"

import { useState, useEffect } from "react"

export interface CustomAttribute {
  id: string
  name: string
  description: string
  selector: string
  priority: number
  extractName?: boolean
  extractPath?: boolean
  namePrefix?: string
  nameSuffix?: string
  findParentComponent?: boolean
  parentSelector?: string
}

export function useCustomAttributes() {
  const [customAttributes, setCustomAttributes] = useState<CustomAttribute[]>([])
  const [isLoaded, setIsLoaded] = useState(false)

  // Carregar atributos personalizados do localStorage
  useEffect(() => {
    try {
      const savedAttributes = localStorage.getItem("component-selector-custom-attributes")
      if (savedAttributes) {
        setCustomAttributes(JSON.parse(savedAttributes))
      } else {
        // Atributos padrão se não houver nenhum salvo
        setCustomAttributes([
          {
            id: "data-component",
            name: "data-component",
            description: "Atributo padrão para identificar componentes",
            selector: "[data-component]",
            priority: 100,
            extractName: true,
          },
          {
            id: "data-component-path",
            name: "data-component-path",
            description: "Atributo padrão para o caminho do componente",
            selector: "[data-component-path]",
            priority: 90,
            extractPath: true,
          },
          {
            id: "model-selector",
            name: "model-selector",
            description: "Seletor de modelos de IA",
            selector: "button[aria-haspopup='dialog']",
            priority: 95,
            findParentComponent: true,
            parentSelector: ".model-selector, [data-component='ModelSelector']",
          },
        ])
      }
      setIsLoaded(true)
    } catch (error) {
      console.error("Erro ao carregar atributos personalizados:", error)
      setIsLoaded(true)
    }
  }, [])

  // Salvar atributos personalizados no localStorage
  useEffect(() => {
    if (isLoaded) {
      localStorage.setItem("component-selector-custom-attributes", JSON.stringify(customAttributes))
    }
  }, [customAttributes, isLoaded])

  // Adicionar um novo atributo personalizado
  const addCustomAttribute = (attribute: Omit<CustomAttribute, "id">) => {
    const newAttribute = {
      ...attribute,
      id: `custom-attr-${Date.now()}`,
    }
    setCustomAttributes((prev) => [...prev, newAttribute])
    return newAttribute.id
  }

  // Atualizar um atributo personalizado existente
  const updateCustomAttribute = (id: string, updates: Partial<CustomAttribute>) => {
    setCustomAttributes((prev) => prev.map((attr) => (attr.id === id ? { ...attr, ...updates } : attr)))
  }

  // Remover um atributo personalizado
  const removeCustomAttribute = (id: string) => {
    setCustomAttributes((prev) => prev.filter((attr) => attr.id !== id))
  }

  // Obter atributos ordenados por prioridade
  const getOrderedAttributes = () => {
    return [...customAttributes].sort((a, b) => b.priority - a.priority)
  }

  return {
    customAttributes,
    addCustomAttribute,
    updateCustomAttribute,
    removeCustomAttribute,
    getOrderedAttributes,
    isLoaded,
  }
}
