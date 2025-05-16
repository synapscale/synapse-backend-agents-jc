"use client"

import { useState, useCallback, useMemo } from "react"

/**
 * Interface que define as opções de configuração para o hook usePagination
 * @interface UsePaginationOptions
 */
export interface UsePaginationOptions {
  /**
   * Número total de itens a serem paginados
   * @required
   */
  totalItems: number

  /**
   * Número de itens por página
   * @default 10
   */
  itemsPerPage?: number

  /**
   * Página inicial
   * @default 1
   */
  initialPage?: number

  /**
   * Número máximo de botões de página a serem exibidos
   * @default 5
   */
  maxPageButtons?: number

  /**
   * Opções de itens por página disponíveis para seleção
   * @default [10, 25, 50, 100]
   */
  itemsPerPageOptions?: number[]

  /**
   * Função chamada quando a página atual muda
   * @param page - Nova página
   */
  onPageChange?: (page: number) => void

  /**
   * Função chamada quando o número de itens por página muda
   * @param itemsPerPage - Novo número de itens por página
   */
  onItemsPerPageChange?: (itemsPerPage: number) => void
}

/**
 * Interface que define o retorno do hook usePagination
 * @interface UsePaginationReturn
 */
export interface UsePaginationReturn {
  /**
   * Página atual
   */
  currentPage: number

  /**
   * Número de itens por página
   */
  itemsPerPage: number

  /**
   * Número total de páginas
   */
  totalPages: number

  /**
   * Índice do primeiro item na página atual
   */
  startIndex: number

  /**
   * Índice do último item na página atual
   */
  endIndex: number

  /**
   * Função para ir para a próxima página
   * @returns true se a operação foi bem-sucedida, false caso contrário
   */
  nextPage: () => boolean

  /**
   * Função para ir para a página anterior
   * @returns true se a operação foi bem-sucedida, false caso contrário
   */
  prevPage: () => boolean

  /**
   * Função para ir para uma página específica
   * @param page - Número da página
   * @returns true se a operação foi bem-sucedida, false caso contrário
   */
  goToPage: (page: number) => boolean

  /**
   * Função para alterar o número de itens por página
   * @param newItemsPerPage - Novo número de itens por página
   */
  setItemsPerPage: (newItemsPerPage: number) => void

  /**
   * Determina se há uma página anterior
   */
  hasPrevPage: boolean

  /**
   * Determina se há uma próxima página
   */
  hasNextPage: boolean

  /**
   * Array de números de página a serem exibidos na interface
   */
  pageNumbers: number[]

  /**
   * Opções de itens por página disponíveis para seleção
   */
  itemsPerPageOptions: number[]

  /**
   * Função para ir para a primeira página
   * @returns true se a operação foi bem-sucedida, false caso contrário
   */
  firstPage: () => boolean

  /**
   * Função para ir para a última página
   * @returns true se a operação foi bem-sucedida, false caso contrário
   */
  lastPage: () => boolean

  /**
   * Determina se a página atual é a primeira
   */
  isFirstPage: boolean

  /**
   * Determina se a página atual é a última
   */
  isLastPage: boolean

  /**
   * Número total de itens
   */
  totalItems: number

  /**
   * Texto descritivo do estado atual da paginação (ex: "Exibindo 1-10 de 100 itens")
   */
  paginationSummary: string
}

/**
 * Hook usePagination - Gerencia o estado e a lógica de paginação
 *
 * @example
 * // Uso básico
 * const pagination = usePagination({ totalItems: 100 });
 *
 * @example
 * // Com configurações personalizadas
 * const pagination = usePagination({
 *   totalItems: 250,
 *   itemsPerPage: 25,
 *   initialPage: 2,
 *   maxPageButtons: 7,
 *   onPageChange: (page) => console.log(`Página alterada para ${page}`)
 * });
 *
 * @param options - Opções de configuração para a paginação
 * @returns Objeto com estado e funções para controlar a paginação
 */
export function usePagination({
  totalItems,
  itemsPerPage: initialItemsPerPage = 10,
  initialPage = 1,
  maxPageButtons = 5,
  itemsPerPageOptions = [10, 25, 50, 100],
  onPageChange,
  onItemsPerPageChange,
}: UsePaginationOptions): UsePaginationReturn {
  // Estado para a página atual e itens por página
  const [currentPage, setCurrentPage] = useState<number>(initialPage > 0 ? initialPage : 1)
  const [itemsPerPage, setItemsPerPage] = useState<number>(initialItemsPerPage)

  // Calcula o número total de páginas
  const totalPages = useMemo(() => {
    return Math.max(1, Math.ceil(totalItems / itemsPerPage))
  }, [totalItems, itemsPerPage])

  // Garante que a página atual está dentro dos limites válidos
  const normalizedCurrentPage = useMemo(() => {
    return Math.min(Math.max(1, currentPage), totalPages)
  }, [currentPage, totalPages])

  // Se a página normalizada for diferente da página atual, atualiza o estado
  if (normalizedCurrentPage !== currentPage) {
    setCurrentPage(normalizedCurrentPage)
  }

  // Calcula os índices de início e fim para a página atual
  const startIndex = useMemo(() => {
    return (normalizedCurrentPage - 1) * itemsPerPage
  }, [normalizedCurrentPage, itemsPerPage])

  const endIndex = useMemo(() => {
    return Math.min(startIndex + itemsPerPage - 1, totalItems - 1)
  }, [startIndex, itemsPerPage, totalItems])

  // Determina se há páginas anteriores ou próximas
  const hasPrevPage = normalizedCurrentPage > 1
  const hasNextPage = normalizedCurrentPage < totalPages
  const isFirstPage = normalizedCurrentPage === 1
  const isLastPage = normalizedCurrentPage === totalPages

  // Gera os números de página a serem exibidos na interface
  const pageNumbers = useMemo(() => {
    // Se o número total de páginas for menor ou igual ao número máximo de botões,
    // exibe todos os números de página
    if (totalPages <= maxPageButtons) {
      return Array.from({ length: totalPages }, (_, i) => i + 1)
    }

    // Caso contrário, calcula quais números de página exibir
    const halfMaxButtons = Math.floor(maxPageButtons / 2)
    let startPage = Math.max(normalizedCurrentPage - halfMaxButtons, 1)
    let endPage = startPage + maxPageButtons - 1

    // Ajusta se o endPage ultrapassar o totalPages
    if (endPage > totalPages) {
      endPage = totalPages
      startPage = Math.max(endPage - maxPageButtons + 1, 1)
    }

    return Array.from({ length: endPage - startPage + 1 }, (_, i) => startPage + i)
  }, [normalizedCurrentPage, totalPages, maxPageButtons])

  // Funções para navegar entre as páginas
  const goToPage = useCallback(
    (page: number): boolean => {
      const targetPage = Math.min(Math.max(1, page), totalPages)
      if (targetPage !== normalizedCurrentPage) {
        setCurrentPage(targetPage)
        onPageChange?.(targetPage)
        return true
      }
      return false
    },
    [normalizedCurrentPage, totalPages, onPageChange],
  )

  const nextPage = useCallback((): boolean => {
    return hasNextPage ? goToPage(normalizedCurrentPage + 1) : false
  }, [hasNextPage, goToPage, normalizedCurrentPage])

  const prevPage = useCallback((): boolean => {
    return hasPrevPage ? goToPage(normalizedCurrentPage - 1) : false
  }, [hasPrevPage, goToPage, normalizedCurrentPage])

  const firstPage = useCallback((): boolean => {
    return goToPage(1)
  }, [goToPage])

  const lastPage = useCallback((): boolean => {
    return goToPage(totalPages)
  }, [goToPage, totalPages])

  // Função para alterar o número de itens por página
  const changeItemsPerPage = useCallback(
    (newItemsPerPage: number) => {
      if (newItemsPerPage !== itemsPerPage && newItemsPerPage > 0) {
        // Calcula a nova página para manter aproximadamente a mesma posição de visualização
        const firstItemIndex = (normalizedCurrentPage - 1) * itemsPerPage
        const newPage = Math.floor(firstItemIndex / newItemsPerPage) + 1

        setItemsPerPage(newItemsPerPage)
        setCurrentPage(newPage)

        onItemsPerPageChange?.(newItemsPerPage)
        onPageChange?.(newPage)
      }
    },
    [itemsPerPage, normalizedCurrentPage, onItemsPerPageChange, onPageChange],
  )

  // Texto descritivo do estado atual da paginação
  const paginationSummary = useMemo(() => {
    const start = totalItems === 0 ? 0 : startIndex + 1
    const end = Math.min(startIndex + itemsPerPage, totalItems)
    return `Exibindo ${start}-${end} de ${totalItems} ${totalItems === 1 ? "item" : "itens"}`
  }, [startIndex, itemsPerPage, totalItems])

  return {
    currentPage: normalizedCurrentPage,
    itemsPerPage,
    totalPages,
    startIndex,
    endIndex,
    nextPage,
    prevPage,
    goToPage,
    setItemsPerPage: changeItemsPerPage,
    hasPrevPage,
    hasNextPage,
    pageNumbers,
    itemsPerPageOptions,
    firstPage,
    lastPage,
    isFirstPage,
    isLastPage,
    totalItems,
    paginationSummary,
  }
}
