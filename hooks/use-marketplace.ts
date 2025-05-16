"use client"

import { useState, useCallback } from "react"
import { useRouter } from "next/navigation"
import { useToast } from "@/components/ui/use-toast"
import { MarketplaceService } from "@/services/marketplace-service"
import type { MarketplaceItem } from "@/types/marketplace-types"

export function useMarketplace() {
  const router = useRouter()
  const { toast } = useToast()
  const [isImporting, setIsImporting] = useState(false)
  const [isAddingToCollection, setIsAddingToCollection] = useState(false)

  // Import an item
  const importItem = useCallback(
    async (item: MarketplaceItem) => {
      setIsImporting(true)
      try {
        await MarketplaceService.importItem(item.id)
        toast({
          title: "Sucesso",
          description: `${item.type === "skill" ? "Skill" : "Node"} importado com sucesso!`,
        })
        return true
      } catch (error) {
        console.error("Erro ao importar item:", error)
        toast({
          title: "Erro",
          description: `Não foi possível importar o ${item.type === "skill" ? "skill" : "node"}.`,
          variant: "destructive",
        })
        return false
      } finally {
        setIsImporting(false)
      }
    },
    [toast],
  )

  // Import from file
  const importFromFile = useCallback(
    async (file: File) => {
      setIsImporting(true)
      try {
        const fileContent = await file.text()
        await MarketplaceService.importFromFile(fileContent)
        toast({
          title: "Sucesso",
          description: "Item importado com sucesso!",
        })
        return true
      } catch (error) {
        console.error("Erro ao importar arquivo:", error)
        toast({
          title: "Erro",
          description: `Não foi possível importar o arquivo: ${error.message}`,
          variant: "destructive",
        })
        return false
      } finally {
        setIsImporting(false)
      }
    },
    [toast],
  )

  // Add item to collection
  const addItemToCollection = useCallback(
    async (collectionId: string, item: MarketplaceItem) => {
      setIsAddingToCollection(true)
      try {
        await MarketplaceService.addItemToCollection(collectionId, item.id, item.type)
        toast({
          title: "Sucesso",
          description: "Item adicionado à coleção com sucesso!",
        })
        return true
      } catch (error) {
        console.error("Erro ao adicionar item à coleção:", error)
        toast({
          title: "Erro",
          description: "Não foi possível adicionar o item à coleção.",
          variant: "destructive",
        })
        return false
      } finally {
        setIsAddingToCollection(false)
      }
    },
    [toast],
  )

  // Remove item from collection
  const removeItemFromCollection = useCallback(
    async (collectionId: string, itemId: string) => {
      try {
        const success = await MarketplaceService.removeItemFromCollection(collectionId, itemId)
        if (success) {
          toast({
            title: "Sucesso",
            description: "Item removido da coleção com sucesso!",
          })
        }
        return success
      } catch (error) {
        console.error("Erro ao remover item da coleção:", error)
        toast({
          title: "Erro",
          description: "Não foi possível remover o item da coleção.",
          variant: "destructive",
        })
        return false
      }
    },
    [toast],
  )

  // Delete collection
  const deleteCollection = useCallback(
    async (collectionId: string) => {
      try {
        const success = await MarketplaceService.deleteCollection(collectionId)
        if (success) {
          toast({
            title: "Sucesso",
            description: "Coleção excluída com sucesso!",
          })
        }
        return success
      } catch (error) {
        console.error("Erro ao excluir coleção:", error)
        toast({
          title: "Erro",
          description: "Não foi possível excluir a coleção.",
          variant: "destructive",
        })
        return false
      }
    },
    [toast],
  )

  return {
    isImporting,
    isAddingToCollection,
    importItem,
    importFromFile,
    addItemToCollection,
    removeItemFromCollection,
    deleteCollection,
  }
}
