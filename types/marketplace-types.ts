import type React from "react"
export interface MarketplaceItem {
  id: string
  name: string
  description: string
  type: "skill" | "node"
  category: string
  version: string
  author: {
    id: string
    displayName: string
    isVerified: boolean
  }
  tags: string[]
  rating: number
  downloads: number
  publishedAt: string
  license: string
}

export interface SkillCollection {
  id: string
  name: string
  description: string
  userId: string
  isPublic: boolean
  items: string[] | MarketplaceItem[]
  tags?: string[]
  stats: {
    favorites: number
    downloads: number
  }
}

export interface CollectionCardProps {
  collection: SkillCollection
  isOwner?: boolean
  isFavorited?: boolean
  disabled?: boolean
  onView?: (id: string) => void
  onEdit?: (collection: SkillCollection) => void
  onDelete?: (collection: SkillCollection) => void
  onShare?: (collection: SkillCollection) => void
  onFavorite?: (collection: SkillCollection, isFavorited: boolean) => void
  onClick?: (e: React.MouseEvent) => void
  maxVisibleTags?: number
  hoverEffect?: boolean
  clickableCard?: boolean
  showFolderIcon?: boolean
  showItemCount?: boolean
  showVisibility?: boolean
  showFavorites?: boolean
  showDownloads?: boolean
  truncateDescription?: boolean
  availableActions?: string[]
  className?: string
  testId?: string
}

export interface MarketplaceItemCardProps {
  item: MarketplaceItem
  onViewDetails: (item: MarketplaceItem) => void
  onImport: (item: MarketplaceItem) => void
  onAddToCollection: (item: MarketplaceItem) => void
  onRemoveFromCollection?: (item: MarketplaceItem) => void
  onFavorite?: (item: MarketplaceItem, isFavorited: boolean) => void
  onClick?: (e: React.MouseEvent) => void
  isFavorited?: boolean
  disabled?: boolean
  maxVisibleTags?: number
  showVerifiedBadge?: boolean
  truncateDescription?: boolean
  showRating?: boolean
  showDownloads?: boolean
  showPublishedDate?: boolean
  clickableCard?: boolean
  hoverEffect?: boolean
  dateFormat?: "default" | "relative" | ((date: Date) => string)
  availableActions?: string[]
  className?: string
  testId?: string
}
