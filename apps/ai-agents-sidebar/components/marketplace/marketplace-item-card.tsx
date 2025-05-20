"use client"

import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { Clock, Download, Eye, FolderPlus, MoreHorizontal, Star } from "lucide-react"
import { cn } from "@/lib/utils"
import type { MarketplaceItem } from "@/types/marketplace-types"

interface SimplifiedMarketplaceItemCardProps {
  item: MarketplaceItem
  onViewDetails: (item: MarketplaceItem) => void
  onImport: (item: MarketplaceItem) => void
  onAddToCollection: (item: MarketplaceItem) => void
  className?: string
}

export function MarketplaceItemCard({
  item,
  onViewDetails,
  onImport,
  onAddToCollection,
  className,
}: SimplifiedMarketplaceItemCardProps) {
  // Simplified version with minimal functionality
  return (
    <Card className={cn("overflow-hidden", className)}>
      <CardHeader className="p-4">
        <div className="flex justify-between items-start">
          <div>
            <CardTitle className="text-base">{item.name}</CardTitle>
            <CardDescription className="flex items-center gap-1 mt-1">
              <span>por {item.author.displayName}</span>
            </CardDescription>
          </div>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                variant="ghost"
                size="sm"
                className="h-8 w-8 p-0"
                onClick={(e) => e.stopPropagation()}
                aria-label="Opções do item"
              >
                <MoreHorizontal className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem
                onClick={(e) => {
                  e.stopPropagation()
                  onViewDetails(item)
                }}
              >
                <Eye className="w-4 h-4 mr-2" />
                Ver detalhes
              </DropdownMenuItem>
              <DropdownMenuItem
                onClick={(e) => {
                  e.stopPropagation()
                  onImport(item)
                }}
              >
                <Download className="w-4 h-4 mr-2" />
                Importar
              </DropdownMenuItem>
              <DropdownMenuItem
                onClick={(e) => {
                  e.stopPropagation()
                  onAddToCollection(item)
                }}
              >
                <FolderPlus className="w-4 h-4 mr-2" />
                Adicionar à coleção
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </CardHeader>
      <CardContent className="p-4 pt-0">
        <p className="text-sm line-clamp-2">{item.description}</p>
        <div className="flex flex-wrap gap-1 mt-3">
          {item.tags.slice(0, 3).map((tag) => (
            <Badge key={tag} variant="secondary" className="text-xs">
              {tag}
            </Badge>
          ))}
          {item.tags.length > 3 && (
            <Badge variant="outline" className="text-xs">
              +{item.tags.length - 3}
            </Badge>
          )}
        </div>
      </CardContent>
      <CardFooter className="p-4 pt-0 flex justify-between items-center text-xs text-muted-foreground">
        <div className="flex items-center gap-3">
          <div className="flex items-center">
            <Star className="w-3.5 h-3.5 mr-1 text-yellow-500" />
            <span>{item.rating.toFixed(1)}</span>
          </div>
          <div className="flex items-center">
            <Download className="w-3.5 h-3.5 mr-1" />
            <span>{item.downloads}</span>
          </div>
        </div>
        <div className="flex items-center">
          <Clock className="w-3.5 h-3.5 mr-1" />
          <span>{new Date(item.publishedAt).toLocaleDateString()}</span>
        </div>
      </CardFooter>
    </Card>
  )
}
