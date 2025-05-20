"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { MarketplaceService } from "@/services/marketplace-service"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Folder } from "lucide-react"
import { MarketplaceItemCard } from "@/components/marketplace/marketplace-item-card"
import { CardSkeleton } from "@/components/ui/skeletons/card-skeleton"
import type { MarketplaceItem, SkillCollection } from "@/types/marketplace-types"
import type { BaseComponentProps } from "@/types/component-interfaces"

interface SimplifiedMarketplaceBrowserProps extends BaseComponentProps {
  className?: string
}

export function MarketplaceBrowser({ className }: SimplifiedMarketplaceBrowserProps) {
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(true)
  const [items, setItems] = useState<MarketplaceItem[]>([])
  const [featuredCollections, setFeaturedCollections] = useState<SkillCollection[]>([])

  // Load data on mount only
  useEffect(() => {
    async function loadData() {
      setIsLoading(true)
      try {
        // Load items with minimal filters
        const itemsResponse = await MarketplaceService.searchItems({
          type: "all",
          sortBy: "relevance",
          page: 1,
          pageSize: 12,
        })
        setItems(itemsResponse.items)

        // Load featured collections
        const collections = await MarketplaceService.getFeaturedCollections(3)
        setFeaturedCollections(collections)
      } catch (error) {
        console.error("Error loading marketplace data:", error)
      } finally {
        setIsLoading(false)
      }
    }

    loadData()
  }, [])

  return (
    <div className={className}>
      <div className="border-b px-4 py-3">
        <div className="flex justify-between items-center">
          <h2 className="text-xl font-bold">Marketplace</h2>
          <Button variant="outline" size="sm" onClick={() => router.push("/marketplace/collections")}>
            <Folder className="w-4 h-4 mr-2" />
            Coleções
          </Button>
        </div>
      </div>

      <div className="flex-1 p-4 overflow-auto">
        {/* Featured Collections */}
        {featuredCollections.length > 0 && (
          <div className="mb-6">
            <div className="flex justify-between items-center mb-3">
              <h3 className="text-lg font-semibold">Coleções em Destaque</h3>
              <Button variant="link" size="sm" onClick={() => router.push("/marketplace/collections")}>
                Ver todas
              </Button>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {featuredCollections.map((collection) => (
                <Card key={collection.id} className="overflow-hidden">
                  <CardHeader className="p-4">
                    <div className="flex justify-between items-start">
                      <div>
                        <CardTitle className="text-base flex items-center">
                          <Folder className="w-4 h-4 mr-2" />
                          {collection.name}
                        </CardTitle>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent className="p-4 pt-0">
                    <p className="text-sm line-clamp-2">{collection.description}</p>
                  </CardContent>
                  <CardFooter className="p-4 pt-0 flex justify-between">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => router.push(`/marketplace/collections/${collection.id}`)}
                    >
                      Ver coleção
                    </Button>
                  </CardFooter>
                </Card>
              ))}
            </div>
          </div>
        )}

        <div className="mb-4">
          <p className="text-sm text-muted-foreground">{!isLoading && `Mostrando ${items.length} resultados`}</p>
        </div>

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
            <p className="text-muted-foreground mb-2">Nenhum resultado encontrado</p>
          </div>
        )}
      </div>
    </div>
  )
}
