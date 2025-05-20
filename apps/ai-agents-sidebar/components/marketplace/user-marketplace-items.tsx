"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { MarketplaceService } from "@/services/marketplace-service"
import type { PublishRequest, ImportHistory, MarketplaceItem } from "@types"
import { Card, CardContent, CardFooter, CardHeader } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { useToast } from "../ui/use-toast"
import { Clock, FileDown, CheckCircle, XCircle } from "lucide-react"
import { CardSkeleton } from "@/components/ui/skeletons/card-skeleton"
import { MarketplaceItemCard } from "@/components/marketplace/marketplace-item-card"
import type { BaseComponentProps } from "@types/component-interfaces"

interface UserMarketplaceItemsProps extends BaseComponentProps {
  className?: string
}

export function UserMarketplaceItems({ className }: UserMarketplaceItemsProps) {
  const router = useRouter()
  const { toast } = useToast()
  const [activeTab, setActiveTab] = useState("published")
  const [isLoading, setIsLoading] = useState(true)
  const [publishHistory, setPublishHistory] = useState<PublishRequest[]>([])
  const [importHistory, setImportHistory] = useState<ImportHistory[]>([])
  const [items, setItems] = useState<MarketplaceItem[]>([])

  // Carregar histórico de publicações e importações
  useEffect(() => {
    loadHistory()
  }, [])

  const loadHistory = async () => {
    setIsLoading(true)
    try {
      const [publishData, importData] = await Promise.all([
        MarketplaceService.getUserPublishHistory(),
        MarketplaceService.getUserImportHistory(),
      ])
      setPublishHistory(publishData)
      setImportHistory(importData)
    } catch (error) {
      console.error("Erro ao carregar histórico:", error)
      toast({
        title: "Erro",
        description: "Não foi possível carregar o histórico.",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  // Exportar um item
  const handleExportItem = async (itemType: "skill" | "node", itemId: string) => {
    try {
      const jsonData = await MarketplaceService.exportItem(itemType, itemId)

      // Criar um blob e um link para download
      const blob = new Blob([jsonData], { type: "application/json" })
      const url = URL.createObjectURL(blob)
      const a = document.createElement("a")
      a.href = url
      a.download = `${itemType}-${itemId}.json`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)

      toast({
        title: "Sucesso",
        description: "Item exportado com sucesso!",
      })
    } catch (error) {
      console.error("Erro ao exportar item:", error)
      toast({
        title: "Erro",
        description: "Não foi possível exportar o item.",
        variant: "destructive",
      })
    }
  }

  // Renderizar status de publicação
  const renderPublishStatus = (status: string) => {
    switch (status) {
      case "published":
        return (
          <Badge variant="success" className="flex items-center gap-1">
            <CheckCircle className="w-3 h-3" />
            Publicado
          </Badge>
        )
      case "pending":
        return (
          <Badge variant="outline" className="flex items-center gap-1">
            <Clock className="w-3 h-3" />
            Pendente
          </Badge>
        )
      case "rejected":
        return (
          <Badge variant="destructive" className="flex items-center gap-1">
            <XCircle className="w-3 h-3" />
            Rejeitado
          </Badge>
        )
      case "draft":
        return (
          <Badge variant="secondary" className="flex items-center gap-1">
            <FileDown className="w-3 h-3" />
            Rascunho
          </Badge>
        )
      default:
        return (
          <Badge variant="outline" className="flex items-center gap-1">
            {status}
          </Badge>
        )
    }
  }

  // Renderizar status de importação
  const renderImportStatus = (status: string) => {
    switch (status) {
      case "success":
        return (
          <Badge variant="success" className="flex items-center gap-1">
            <CheckCircle className="w-3 h-3" />
            Sucesso
          </Badge>
        )
      case "failed":
        return (
          <Badge variant="destructive" className="flex items-center gap-1">
            <XCircle className="w-3 h-3" />
            Falha
          </Badge>
        )
      default:
        return (
          <Badge variant="outline" className="flex items-center gap-1">
            {status}
          </Badge>
        )
    }
  }

  // Renderizar esqueletos de carregamento
  const renderSkeletons = () => {
    return Array.from({ length: 3 }).map((_, index) => (
      <Card key={`skeleton-${index}`}>
        <CardHeader className="p-4">
          <Skeleton className="h-5 w-3/4" />
          <Skeleton className="h-4 w-1/2 mt-2" />
        </CardHeader>
        <CardContent className="p-4 pt-0">
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-5/6 mt-1" />
        </CardContent>
        <CardFooter className="p-4 pt-0 flex justify-between">
          <Skeleton className="h-4 w-20" />
          <Skeleton className="h-4 w-20" />
        </CardFooter>
      </Card>
    ))
  }

  // Load data on mount only
  useEffect(() => {
    async function loadUserItems() {
      setIsLoading(true)
      try {
        // This is a placeholder - in a real app, you'd fetch the user's items
        const response = await MarketplaceService.getUserItems()
        setItems(response.items)
      } catch (error) {
        console.error("Error loading user items:", error)
      } finally {
        setIsLoading(false)
      }
    }

    loadUserItems()
  }, [])

  return (
    <div className={className}>
      <div className="border-b px-4 py-3">
        <h2 className="text-xl font-bold">Meus Itens</h2>
      </div>

      <div className="flex-1 p-4 overflow-auto">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {isLoading
            ? Array.from({ length: 6 }).map((_, index) => <CardSkeleton key={`skeleton-${index}`} />)
            : items.map((item) => (
                <MarketplaceItemCard
                  key={item.id}
                  item={item}
                  onViewDetails={() => {}}
                  onImport={() => {}}
                  onAddToCollection={() => {}}
                />
              ))}
        </div>

        {!isLoading && items.length === 0 && (
          <div className="text-center py-12">
            <p className="text-muted-foreground mb-2">Você ainda não tem itens no marketplace</p>
          </div>
        )}
      </div>
    </div>
  )
}
