"use client"

import { useState, useCallback } from "react"

/**
 * Interface que define as opções de configuração para o hook useDialog
 * @interface UseDialogOptions
 */
export interface UseDialogOptions {
  /**
   * Estado inicial do diálogo (aberto ou fechado)
   * @default false
   */
  initialOpen?: boolean

  /**
   * Função chamada quando o diálogo é aberto
   */
  onOpen?: () => void

  /**
   * Função chamada quando o diálogo é fechado
   */
  onClose?: () => void

  /**
   * Função chamada antes de abrir o diálogo
   * Se retornar false, o diálogo não será aberto
   * @returns true para permitir a abertura, false para impedir
   */
  beforeOpen?: () => boolean | Promise<boolean>

  /**
   * Função chamada antes de fechar o diálogo
   * Se retornar false, o diálogo não será fechado
   * @returns true para permitir o fechamento, false para impedir
   */
  beforeClose?: () => boolean | Promise<boolean>
}

/**
 * Interface que define o retorno do hook useDialog
 * @interface UseDialogReturn
 */
export interface UseDialogReturn {
  /**
   * Estado atual do diálogo (aberto ou fechado)
   */
  isOpen: boolean

  /**
   * Função para abrir o diálogo
   * @returns Promise que resolve para true se o diálogo foi aberto, false caso contrário
   */
  open: () => Promise<boolean>

  /**
   * Função para fechar o diálogo
   * @returns Promise que resolve para true se o diálogo foi fechado, false caso contrário
   */
  close: () => Promise<boolean>

  /**
   * Função para alternar o estado do diálogo (abrir se fechado, fechar se aberto)
   * @returns Promise que resolve para true se o estado foi alterado, false caso contrário
   */
  toggle: () => Promise<boolean>
}

/**
 * Hook useDialog - Gerencia o estado e a lógica de diálogos/modais
 *
 * @example
 * // Uso básico
 * const { isOpen, open, close, toggle } = useDialog();
 *
 * @example
 * // Com callbacks
 * const dialog = useDialog({
 *   onOpen: () => console.log('Diálogo aberto'),
 *   onClose: () => console.log('Diálogo fechado'),
 *   beforeOpen: () => {
 *     const userConfirmed = window.confirm('Deseja realmente abrir o diálogo?');
 *     return userConfirmed;
 *   }
 * });
 *
 * @param options - Opções de configuração para o diálogo
 * @returns Objeto com estado e funções para controlar o diálogo
 */
export function useDialog({
  initialOpen = false,
  onOpen,
  onClose,
  beforeOpen,
  beforeClose,
}: UseDialogOptions = {}): UseDialogReturn {
  // Estado para controlar se o diálogo está aberto ou fechado
  const [isOpen, setIsOpen] = useState<boolean>(initialOpen)

  /**
   * Função para abrir o diálogo
   * Executa a validação beforeOpen se fornecida
   */
  const open = useCallback(async (): Promise<boolean> => {
    // Se o diálogo já estiver aberto, não faz nada
    if (isOpen) return false

    // Executa a validação beforeOpen se fornecida
    if (beforeOpen) {
      try {
        const canOpen = await beforeOpen()
        if (!canOpen) return false
      } catch (error) {
        console.error("Error in beforeOpen callback:", error)
        return false
      }
    }

    // Abre o diálogo e executa o callback onOpen
    setIsOpen(true)
    onOpen?.()
    return true
  }, [isOpen, beforeOpen, onOpen])

  /**
   * Função para fechar o diálogo
   * Executa a validação beforeClose se fornecida
   */
  const close = useCallback(async (): Promise<boolean> => {
    // Se o diálogo já estiver fechado, não faz nada
    if (!isOpen) return false

    // Executa a validação beforeClose se fornecida
    if (beforeClose) {
      try {
        const canClose = await beforeClose()
        if (!canClose) return false
      } catch (error) {
        console.error("Error in beforeClose callback:", error)
        return false
      }
    }

    // Fecha o diálogo e executa o callback onClose
    setIsOpen(false)
    onClose?.()
    return true
  }, [isOpen, beforeClose, onClose])

  /**
   * Função para alternar o estado do diálogo
   * Abre se estiver fechado, fecha se estiver aberto
   */
  const toggle = useCallback(async (): Promise<boolean> => {
    return isOpen ? await close() : await open()
  }, [isOpen, open, close])

  return {
    isOpen,
    open,
    close,
    toggle,
  }
}
