"use client"

import type React from "react"

import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { Heart, MoreHorizontal, Eye, Edit, Share, Trash, Users, Download, Folder } from "lucide-react"
import { useRouter } from "next/navigation"
import { cn } from "@/lib/utils"
import type { CollectionCardProps } from "@/types/core/marketplace-types"

/**
 * CollectionCard Component
 *
 * Displays a card for a collection with details, tags, and actions.
 * Supports various customization options and actions like viewing, editing,
 * sharing, and deleting collections.
 *
 * @example
 * ```tsx
 * <CollectionCard
 *   collection={collectionData}
 *   isOwner={true}
 *   onEdit={handleEditCollection}
 *   onDelete={handleDeleteCollection}
 *   onShare={handleShareCollection}
 *   isFavorited={favoriteCollections.includes(collectionData.id)}
 *   onFavorite={handleToggleFavorite}
 * />
 * ```
 */
export function CollectionCard({
  // Required props
  collection,

  // State props
  isOwner = false,
  isFavorited = false,
  disabled = false,

  // Action handlers
  onView,
  onEdit,
  onDelete,
  onShare,
  onFavorite,
  onClick,

  // Display options
  maxVisibleTags = 3,
  hoverEffect = true,
  clickableCard = false,
  showFolderIcon = false,
  showItemCount = true,
  showVisibility = true,
  showFavorites = true,
  showDownloads = true,
  truncateDescription = true,

  // Available actions
  availableActions,

  // Accessibility and testing
  className,
  testId,

  // Other props
  ...otherProps
}: CollectionCardProps) {
  const router = useRouter()

  // Determine default actions based on ownership
  const defaultActions = isOwner ? ["view", "edit", "share", "delete"] : ["view", "share"]

  // Use provided actions or default ones
  const actions = availableActions || defaultActions

  // Handle view collection
  const handleView = () => {
    if (disabled) return

    if (onView) {
      onView(collection.id)
    } else {
      router.push(`/marketplace/collections/${collection.id}`)
    }
  }

  // Handle card click
  const handleCardClick = (e: React.MouseEvent) => {
    if (disabled) return

    if (clickableCard) {
      handleView()
    }

    onClick?.(e)
  }

  // Handle favorite toggle
  const handleFavoriteToggle = (e: React.MouseEvent) => {
    e.stopPropagation()
    onFavorite?.(collection, !isFavorited)
  }

  return (
    <Card
      className={cn(
        "overflow-hidden",
        hoverEffect && "transition-shadow hover:shadow-md",
        clickableCard && "cursor-pointer",
        disabled && "opacity-60 cursor-not-allowed",
        className,
      )}
      onClick={handleCardClick}
      data-testid={testId}
      data-collection-id={collection.id}
      aria-disabled={disabled}
      {...otherProps}
    >
      <CardHeader className="p-4">
        <div className="flex justify-between items-start">
          <div>
            <CardTitle className="text-base flex items-center gap-1.5">
              {showFolderIcon && <Folder className="w-4 h-4 text-muted-foreground" />}
              {collection.name}
            </CardTitle>
            <CardDescription className="flex items-center gap-1 mt-1">
              {collection.userId === "current-user" ? "Você" : collection.userId}
              {showItemCount && (
                <>
                  <span className="mx-1">•</span>
                  <span>{collection.items.length} itens</span>
                </>
              )}
            </CardDescription>
          </div>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                variant="ghost"
                size="sm"
                className="h-8 w-8 p-0"
                onClick={(e) => e.stopPropagation()}
                aria-label="Opções da coleção"
                disabled={disabled}
              >
                <MoreHorizontal className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              {actions.includes("view") && (
                <DropdownMenuItem
                  onClick={(e) => {
                    e.stopPropagation()
                    handleView()
                  }}
                  disabled={disabled}
                >
                  <Eye className="w-4 h-4 mr-2" />
                  Ver detalhes
                </DropdownMenuItem>
              )}
              {isOwner && actions.includes("edit") && onEdit && (
                <DropdownMenuItem
                  onClick={(e) => {
                    e.stopPropagation()
                    onEdit(collection)
                  }}
                  disabled={disabled}
                >
                  <Edit className="w-4 h-4 mr-2" />
                  Editar
                </DropdownMenuItem>
              )}
              {actions.includes("share") && onShare && (
                <DropdownMenuItem
                  onClick={(e) => {
                    e.stopPropagation()
                    onShare(collection)
                  }}
                  disabled={disabled}
                >
                  <Share className="w-4 h-4 mr-2" />
                  Compartilhar
                </DropdownMenuItem>
              )}
              {isOwner && actions.includes("delete") && onDelete && (
                <DropdownMenuItem
                  className="text-red-600"
                  onClick={(e) => {
                    e.stopPropagation()
                    onDelete(collection)
                  }}
                  disabled={disabled}
                >
                  <Trash className="w-4 h-4 mr-2" />
                  Excluir
                </DropdownMenuItem>
              )}
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </CardHeader>
      <CardContent className="p-4 pt-0">
        <p className={cn("text-sm", truncateDescription && "line-clamp-2")}>{collection.description}</p>
        <div className="flex flex-wrap gap-1 mt-3">
          {collection.tags?.slice(0, maxVisibleTags).map((tag) => (
            <Badge key={tag} variant="secondary" className="text-xs">
              {tag}
            </Badge>
          ))}
          {collection.tags && collection.tags.length > maxVisibleTags && (
            <Badge variant="outline" className="text-xs">
              +{collection.tags.length - maxVisibleTags}
            </Badge>
          )}
        </div>
      </CardContent>
      <CardFooter className="p-4 pt-0 flex justify-between items-center text-xs text-muted-foreground">
        <div className="flex items-center gap-3">
          {showFavorites && (
            <div
              className={cn("flex items-center", onFavorite && !disabled && "cursor-pointer hover:text-foreground")}
              onClick={onFavorite && !disabled ? handleFavoriteToggle : undefined}
            >
              <Heart className={cn("w-3.5 h-3.5 mr-1", isFavorited ? "fill-red-500 text-red-500" : "text-red-500")} />
              <span>{collection.stats.favorites}</span>
            </div>
          )}
          {showDownloads && (
            <div className="flex items-center">
              <Download className="w-3.5 h-3.5 mr-1" />
              <span>{collection.stats.downloads}</span>
            </div>
          )}
          {showVisibility && (
            <div className="flex items-center">
              <Users className="w-3.5 h-3.5 mr-1" />
              <span>{collection.isPublic ? "Pública" : "Privada"}</span>
            </div>
          )}
        </div>
      </CardFooter>
    </Card>
  )
}
