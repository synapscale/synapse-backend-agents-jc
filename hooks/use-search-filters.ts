"use client"

import { useState, useCallback, useMemo, useEffect } from "react"

/**
 * Tipo que define os operadores de comparação disponíveis
 */
export type FilterOperator =
  | "equals" // Igual a
  | "notEquals" // Diferente de
  | "contains" // Contém
  | "notContains" // Não contém
  | "startsWith" // Começa com
  | "endsWith" // Termina com
  | "greaterThan" // Maior que
  | "lessThan" // Menor que
  | "greaterOrEqual" // Maior ou igual a
  | "lessOrEqual" // Menor ou igual a
  | "between" // Entre dois valores
  | "in" // Em uma lista de valores
  | "notIn" // Não está em uma lista de valores

/**
 * Interface que define um filtro individual
 * @interface Filter
 */
export interface Filter<T = any> {
  /**
   * Campo a ser filtrado
   */
  field: keyof T

  /**
   * Operador de comparação
   * @default "equals"
   */
  operator?: FilterOperator

  /**
   * Valor para comparação
   */
  value: any

  /**
   * Segundo valor para comparação (usado com o operador 'between')
   */
  value2?: any
}

/**
 * Interface que define as opções de ordenação
 * @interface SortOption
 */
export interface SortOption<T = any> {
  /**
   * Campo a ser ordenado
   */
  field: keyof T

  /**
   * Direção da ordenação
   * @default "asc"
   */
  direction: "asc" | "desc"
}

/**
 * Interface que define as opções de configuração para o hook useSearchFilters
 * @interface UseSearchFiltersOptions
 */
export interface UseSearchFiltersOptions<T = any> {
  /**
   * Filtros iniciais
   * @default []
   */
  initialFilters?: Filter<T>[]

  /**
   * Opção de ordenação inicial
   */
  initialSort?: SortOption<T>

  /**
   * Termo de busca inicial
   * @default ""
   */
  initialSearchTerm?: string

  /**
   * Campos a serem considerados na busca por texto
   * @default []
   */
  searchFields?: (keyof T)[]

  /**
   * Função chamada quando os filtros são alterados
   * @param filters - Novos filtros
   */
  onFiltersChange?: (filters: Filter<T>[]) => void

  /**
   * Função chamada quando a ordenação é alterada
   * @param sort - Nova opção de ordenação
   */
  onSortChange?: (sort: SortOption<T> | null) => void

  /**
   * Função chamada quando o termo de busca é alterado
   * @param searchTerm - Novo termo de busca
   */
  onSearchTermChange?: (searchTerm: string) => void

  /**
   * Atraso em milissegundos para debounce do termo de busca
   * @default 300
   */
  searchDebounce?: number
}

/**
 * Interface que define o retorno do hook useSearchFilters
 * @interface UseSearchFiltersReturn
 */
export interface UseSearchFiltersReturn<T = any> {
  /**
   * Filtros ativos
   */
  filters: Filter<T>[]

  /**
   * Opção de ordenação ativa
   */
  sort: SortOption<T> | null

  /**
   * Termo de busca atual
   */
  searchTerm: string

  /**
   * Termo de busca com debounce aplicado
   */
  debouncedSearchTerm: string

  /**
   * Função para adicionar um novo filtro
   * @param filter - Filtro a ser adicionado
   */
  addFilter: (filter: Filter<T>) => void

  /**
   * Função para remover um filtro pelo índice
   * @param index - Índice do filtro a ser removido
   */
  removeFilter: (index: number) => void

  /**
   * Função para atualizar um filtro existente
   * @param index - Índice do filtro a ser atualizado
   * @param filter - Novo filtro
   */
  updateFilter: (index: number, filter: Filter<T>) => void

  /**
   * Função para limpar todos os filtros
   */
  clearFilters: () => void

  /**
   * Função para definir a opção de ordenação
   * @param sort - Nova opção de ordenação
   */
  setSort: (sort: SortOption<T> | null) => void

  /**
   * Função para alternar a direção da ordenação atual
   */
  toggleSortDirection: () => void

  /**
   * Função para definir o termo de busca
   * @param term - Novo termo de busca
   */
  setSearchTerm: (term: string) => void

  /**
   * Função para limpar o termo de busca
   */
  clearSearchTerm: () => void

  /**
   * Função para aplicar os filtros a uma lista de itens
   * @param items - Lista de itens a ser filtrada
   * @returns Lista filtrada e ordenada
   */
  applyFilters: (items: T[]) => T[]

  /**
   * Função para resetar todos os filtros, ordenação e termo de busca
   */
  resetAll: () => void

  /**
   * Determina se há filtros ativos
   */
  hasActiveFilters: boolean
}

/**
 * Hook useSearchFilters - Gerencia filtros, ordenação e busca para listas de dados
 *
 * @example
 * // Uso básico
 * const {
 *   filters,
 *   addFilter,
 *   removeFilter,
 *   searchTerm,
 *   setSearchTerm,
 *   applyFilters
 * } = useSearchFilters<User>({
 *   searchFields: ['name', 'email']
 * });
 *
 * // Aplicar filtros a uma lista
 * const filteredUsers = applyFilters(users);
 *
 * @example
 * // Com filtros iniciais e ordenação
 * const searchFilters = useSearchFilters<Product>({
 *   initialFilters: [{ field: 'category', operator: 'equals', value: 'electronics' }],
 *   initialSort: { field: 'price', direction: 'asc' },
 *   initialSearchTerm: 'smartphone',
 *   searchFields: ['name', 'description']
 * });
 *
 * @param options - Opções de configuração para os filtros de busca
 * @returns Objeto com estado e funções para controlar filtros, ordenação e busca
 */
export function useSearchFilters<T = any>({
  initialFilters = [],
  initialSort,
  initialSearchTerm = "",
  searchFields = [],
  onFiltersChange,
  onSortChange,
  onSearchTermChange,
  searchDebounce = 300,
}: UseSearchFiltersOptions<T> = {}): UseSearchFiltersReturn<T> {
  // Estados para filtros, ordenação e termo de busca
  const [filters, setFilters] = useState<Filter<T>[]>(initialFilters)
  const [sort, setSort] = useState<SortOption<T> | null>(initialSort || null)
  const [searchTerm, setSearchTerm] = useState<string>(initialSearchTerm)
  const [debouncedSearchTerm, setDebouncedSearchTerm] = useState<string>(initialSearchTerm)

  // Aplica debounce ao termo de busca
  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedSearchTerm(searchTerm)
      onSearchTermChange?.(searchTerm)
    }, searchDebounce)

    return () => {
      clearTimeout(handler)
    }
  }, [searchTerm, searchDebounce, onSearchTermChange])

  // Funções para manipular filtros
  const addFilter = useCallback(
    (filter: Filter<T>) => {
      setFilters((prev) => {
        const newFilters = [...prev, filter]
        onFiltersChange?.(newFilters)
        return newFilters
      })
    },
    [onFiltersChange],
  )

  const removeFilter = useCallback(
    (index: number) => {
      setFilters((prev) => {
        const newFilters = prev.filter((_, i) => i !== index)
        onFiltersChange?.(newFilters)
        return newFilters
      })
    },
    [onFiltersChange],
  )

  const updateFilter = useCallback(
    (index: number, filter: Filter<T>) => {
      setFilters((prev) => {
        const newFilters = [...prev]
        newFilters[index] = filter
        onFiltersChange?.(newFilters)
        return newFilters
      })
    },
    [onFiltersChange],
  )

  const clearFilters = useCallback(() => {
    setFilters([])
    onFiltersChange?.([])
  }, [onFiltersChange])

  // Funções para manipular ordenação
  const setSortOption = useCallback(
    (newSort: SortOption<T> | null) => {
      setSort(newSort)
      onSortChange?.(newSort)
    },
    [onSortChange],
  )

  const toggleSortDirection = useCallback(() => {
    if (!sort) return

    const newDirection = sort.direction === "asc" ? "desc" : "asc"
    const newSort = { ...sort, direction: newDirection }

    setSort(newSort)
    onSortChange?.(newSort)
  }, [sort, onSortChange])

  // Funções para manipular termo de busca
  const setSearchTermValue = useCallback((term: string) => {
    setSearchTerm(term)
  }, [])

  const clearSearchTerm = useCallback(() => {
    setSearchTerm("")
    onSearchTermChange?.("")
  }, [onSearchTermChange])

  // Função para resetar todos os filtros
  const resetAll = useCallback(() => {
    clearFilters()
    setSort(null)
    onSortChange?.(null)
    clearSearchTerm()
  }, [clearFilters, onSortChange, clearSearchTerm])

  // Verifica se há filtros ativos
  const hasActiveFilters = useMemo(() => {
    return filters.length > 0 || !!sort || debouncedSearchTerm.trim() !== ""
  }, [filters, sort, debouncedSearchTerm])

  /**
   * Aplica um filtro individual a um item
   * @param item - Item a ser filtrado
   * @param filter - Filtro a ser aplicado
   * @returns true se o item passa no filtro, false caso contrário
   */
  const applyFilter = useCallback((item: T, filter: Filter<T>): boolean => {
    const { field, operator = "equals", value, value2 } = filter
    const itemValue = item[field]

    // Se o valor do item for undefined ou null, retorna false para a maioria dos operadores
    if (itemValue === undefined || itemValue === null) {
      // Exceções: notEquals, notContains, notIn
      if (operator === "notEquals") return value === null || value === undefined
      if (operator === "notContains" || operator === "notIn") return true
      return false
    }

    // Converte para string para comparações de texto
    const stringValue = String(itemValue).toLowerCase()
    const stringFilterValue = value !== null && value !== undefined ? String(value).toLowerCase() : ""

    switch (operator) {
      case "equals":
        return itemValue === value
      case "notEquals":
        return itemValue !== value
      case "contains":
        return stringValue.includes(stringFilterValue)
      case "notContains":
        return !stringValue.includes(stringFilterValue)
      case "startsWith":
        return stringValue.startsWith(stringFilterValue)
      case "endsWith":
        return stringValue.endsWith(stringFilterValue)
      case "greaterThan":
        return itemValue > value
      case "lessThan":
        return itemValue < value
      case "greaterOrEqual":
        return itemValue >= value
      case "lessOrEqual":
        return itemValue <= value
      case "between":
        return itemValue >= value && itemValue <= value2
      case "in":
        return Array.isArray(value) && value.includes(itemValue)
      case "notIn":
        return Array.isArray(value) && !value.includes(itemValue)
      default:
        return true
    }
  }, [])

  /**
   * Aplica o termo de busca a um item
   * @param item - Item a ser filtrado
   * @returns true se o item passa no filtro de busca, false caso contrário
   */
  const applySearch = useCallback(
    (item: T): boolean => {
      if (!debouncedSearchTerm || debouncedSearchTerm.trim() === "") return true
      if (searchFields.length === 0) return true

      const searchTermLower = debouncedSearchTerm.toLowerCase().trim()

      return searchFields.some((field) => {
        const value = item[field]
        if (value === undefined || value === null) return false

        return String(value).toLowerCase().includes(searchTermLower)
      })
    },
    [debouncedSearchTerm, searchFields],
  )

  /**
   * Compara dois itens para ordenação
   * @param a - Primeiro item
   * @param b - Segundo item
   * @returns Número negativo se a < b, positivo se a > b, zero se a === b
   */
  const compareItems = useCallback(
    (a: T, b: T): number => {
      if (!sort) return 0

      const { field, direction } = sort
      const valueA = a[field]
      const valueB = b[field]

      // Tratamento para valores undefined ou null
      if (valueA === undefined || valueA === null) {
        return direction === "asc" ? -1 : 1
      }
      if (valueB === undefined || valueB === null) {
        return direction === "asc" ? 1 : -1
      }

      // Comparação baseada no tipo de dados
      if (typeof valueA === "string" && typeof valueB === "string") {
        return direction === "asc" ? valueA.localeCompare(valueB) : valueB.localeCompare(valueA)
      }

      // Comparação numérica ou de data
      const numA = valueA instanceof Date ? valueA.getTime() : valueA
      const numB = valueB instanceof Date ? valueB.getTime() : valueB

      return direction === "asc" ? numA - numB : numB - numA
    },
    [sort],
  )

  /**
   * Aplica todos os filtros, busca e ordenação a uma lista de itens
   * @param items - Lista de itens a ser filtrada
   * @returns Lista filtrada e ordenada
   */
  const applyFilters = useCallback(
    (items: T[]): T[] => {
      if (!items || !Array.isArray(items)) return []

      // Aplica filtros
      let result = items

      if (filters.length > 0) {
        result = result.filter((item) => filters.every((filter) => applyFilter(item, filter)))
      }

      // Aplica busca por texto
      if (debouncedSearchTerm && debouncedSearchTerm.trim() !== "") {
        result = result.filter(applySearch)
      }

      // Aplica ordenação
      if (sort) {
        result = [...result].sort(compareItems)
      }

      return result
    },
    [filters, debouncedSearchTerm, sort, applyFilter, applySearch, compareItems],
  )

  return {
    filters,
    sort,
    searchTerm,
    debouncedSearchTerm,
    addFilter,
    removeFilter,
    updateFilter,
    clearFilters,
    setSort: setSortOption,
    toggleSortDirection,
    setSearchTerm: setSearchTermValue,
    clearSearchTerm,
    applyFilters,
    resetAll,
    hasActiveFilters,
  }
}
