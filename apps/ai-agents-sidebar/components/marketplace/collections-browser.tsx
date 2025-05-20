"use client"

import type React from "react"
import { useEffect, useState } from "react"
import { MarketplaceService } from "@/services/marketplace-service"
import type { Collection, SearchFilters } from "@/types/marketplace-types"
import { CollectionCard } from "./collection-card"
import { SearchBar } from "../ui/search-bar"
import { PaginationControls } from "../ui/pagination-controls"
import { CardSkeleton } from "../ui/skeletons/card-skeleton"
import { useSearchFilters } from "@/hooks/use-search-filters"
import { usePagination } from "@/hooks/use-pagination"

/**
 * CollectionType - Enum for collection types that can be displayed
 *
 * @enum {string}
 * @property {string} ALL - Show all collections
 * @property {string} FEATURED - Show only featured collections
 * @property {string} PERSONAL - Show only user's personal collections
 * @property {string} PUBLIC - Show only public collections
 */
export enum CollectionType {
  ALL = "all",
  FEATURED = "featured",
  PERSONAL = "personal",
  PUBLIC = "public",
}

/**
 * CollectionsBrowserProps - Interface for the CollectionsBrowser component props
 *
 * @property {string} [title] - Optional custom title for the collections browser
 * @property {string} [description] - Optional custom description for the collections browser
 * @property {CollectionType} [collectionType=CollectionType.ALL] - Type of collections to display
 * @property {SearchFilters} [initialFilters] - Optional initial search filters to apply
 * @property {boolean} [showSearchBar=true] - Whether to show the search bar
 * @property {boolean} [showPagination=true] - Whether to show pagination controls
 * @property {number} [itemsPerPage=12] - Number of collections to display per page
 * @property {number} [skeletonCount=12] - Number of skeleton items to show during loading
 * @property {(collection: Collection) => void} [onCollectionClick] - Optional callback when a collection is clicked
 * @property {React.ReactNode} [emptyStateContent] - Optional custom content to display when no collections are found
 * @property {string} [className] - Optional additional CSS classes
 * @property {boolean} [showCreateButton=false] - Whether to show the create collection button
 * @property {() => void} [onCreateCollection] - Callback when the create collection button is clicked
 */
interface CollectionsBrowserProps {
  title?: string
  description?: string
  collectionType?: CollectionType
  initialFilters?: SearchFilters
  showSearchBar?: boolean
  showPagination?: boolean
  itemsPerPage?: number
  skeletonCount?: number
  onCollectionClick?: (collection: Collection) => void
  emptyStateContent?: React.ReactNode
  className?: string
  showCreateButton?: boolean
  onCreateCollection?: () => void
}

/**
 * CollectionsBrowser - A component for browsing and searching collections
 *
 * This component provides a complete interface for browsing collections with
 * search and pagination capabilities. It handles loading states and
 * empty states automatically.
 *
 * @example
 * // Basic usage
 * <CollectionsBrowser />
 *
 * @example
 * // Show only featured collections
 * <CollectionsBrowser
 *   collectionType={CollectionType.FEATURED}
 *   title="Featured Collections"
 * />
 *
 * @example
 * // With create button for personal collections
 * <CollectionsBrowser
 *   collectionType={CollectionType.PERSONAL}
 *   showCreateButton={true}
 *   onCreateCollection={() => openCreateCollectionModal()}
 * />
 */
export function CollectionsBrowser({
  title = "Collections",
  description = "Browse and discover curated collections of skills",
  collectionType = CollectionType.ALL,
  initialFilters = {},
  showSearchBar = true,
  showPagination = true,
  itemsPerPage = 12,
  skeletonCount = 12,
  onCollectionClick,
  emptyStateContent,
  className = "",
  showCreateButton = false,
  onCreateCollection,
}: CollectionsBrowserProps) {
  // State for collections and loading status
  const [collections, setCollections] = useState<Collection[]>([])
  const [isLoading, setIsLoading] = useState<boolean>(true)
  const [totalItems, setTotalItems] = useState<number>(0)

  // State for current page - added to fix the setCurrentPage issue
  const [currentPage, setCurrentPage] = useState<number>(1)
  const [totalPages, setTotalPages] = useState<number>(1)

  // Use custom hooks for search filters and pagination
  const { filters, setFilters, handleSearchChange } = useSearchFilters(initialFilters)

  // Use the usePagination hook for pagination logic
  const pagination = usePagination({
    totalItems,
    itemsPerPage,
    initialPage: 1,
  })

  // Handle page change
  const handlePageChange = (page: number) => {
    setCurrentPage(page)
  }

  // Fetch collections based on current filters, type, and pagination
  useEffect(() => {
    const fetchCollections = async () => {
      setIsLoading(true)
      try {
        // Calculate pagination parameters
        const offset = (currentPage - 1) * itemsPerPage
        const limit = itemsPerPage

        let response

        // Fetch collections based on the collection type
        switch (collectionType) {
          case CollectionType.FEATURED:
            response = await MarketplaceService.getFeaturedCollections({
              ...filters,
              offset,
              limit,
            })
            break
          case CollectionType.PERSONAL:
            response = await MarketplaceService.getUserCollections({
              ...filters,
              offset,
              limit,
            })
            break
          case CollectionType.PUBLIC:
            response = await MarketplaceService.getPublicCollections({
              ...filters,
              offset,
              limit,
            })
            break
          default:
            response = await MarketplaceService.getAllCollections({
              ...filters,
              offset,
              limit,
            })
        }

        // Update state with fetched data
        setCollections(response.collections)
        setTotalItems(response.totalCount)
        setTotalPages(Math.ceil(response.totalCount / itemsPerPage))
      } catch (error) {
        console.error("Error fetching collections:", error)
        setCollections([])
        setTotalItems(0)
        setTotalPages(1)
      } finally {
        setIsLoading(false)
      }
    }

    fetchCollections()
  }, [filters, collectionType, currentPage, itemsPerPage])

  // Reset to first page when filters change
  useEffect(() => {
    setCurrentPage(1)
  }, [filters, collectionType])

  // Handle collection click with optional callback
  const handleCollectionClick = (collection: Collection) => {
    if (onCollectionClick) {
      onCollectionClick(collection)
    }
  }

  // Render loading skeletons
  const renderSkeletons = () => {
    return Array(skeletonCount)
      .fill(0)
      .map((_, index) => (
        <CardSkeleton key={`skeleton-${index}`} className="h-[280px]" imageHeight={140} lines={3} showFooter />
      ))
  }

  // Render empty state
  const renderEmptyState = () => {
    if (emptyStateContent) {
      return emptyStateContent
    }

    let message = "No collections found"
    let description = "Try adjusting your search to find what you're looking for."

    if (collectionType === CollectionType.PERSONAL && !filters.searchTerm) {
      message = "You don't have any collections yet"
      description = "Create your first collection to organize your skills."
    }

    return (
      <div className="flex flex-col items-center justify-center p-8 text-center">
        <h3 className="text-xl font-semibold mb-2">{message}</h3>
        <p className="text-gray-500 mb-4">{description}</p>
        {collectionType === CollectionType.PERSONAL ? (
          <button
            className="px-4 py-2 bg-primary text-white rounded-md hover:bg-primary/90 transition-colors"
            onClick={onCreateCollection}
          >
            Create Collection
          </button>
        ) : (
          <button
            className="px-4 py-2 bg-primary text-white rounded-md hover:bg-primary/90 transition-colors"
            onClick={() => setFilters({})}
          >
            Clear all filters
          </button>
        )}
      </div>
    )
  }

  return (
    <div className={`w-full ${className}`}>
      {/* Header section */}
      <div className="mb-8 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold mb-2">{title}</h1>
          <p className="text-gray-500">{description}</p>
        </div>

        {showCreateButton && (
          <button
            className="px-4 py-2 bg-primary text-white rounded-md hover:bg-primary/90 transition-colors"
            onClick={onCreateCollection}
            aria-label="Create new collection"
          >
            Create Collection
          </button>
        )}
      </div>

      {/* Search bar */}
      {showSearchBar && (
        <div className="mb-6">
          <SearchBar
            placeholder="Search collections..."
            value={filters.searchTerm || ""}
            onChange={handleSearchChange}
            onClear={() => handleSearchChange("")}
            className="w-full max-w-xl"
            debounceMs={300}
            aria-label="Search collections"
          />
        </div>
      )}

      {/* Collections grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 mb-8">
        {isLoading ? (
          renderSkeletons()
        ) : collections.length > 0 ? (
          collections.map((collection) => (
            <CollectionCard
              key={collection.id}
              collection={collection}
              onClick={() => handleCollectionClick(collection)}
              aria-label={`View collection: ${collection.name}`}
            />
          ))
        ) : (
          <div className="col-span-full">{renderEmptyState()}</div>
        )}
      </div>

      {/* Pagination controls */}
      {showPagination && !isLoading && collections.length > 0 && (
        <PaginationControls
          currentPage={currentPage}
          totalPages={totalPages}
          onPageChange={handlePageChange}
          className="flex justify-center"
          aria-label="Collections pagination"
        />
      )}
    </div>
  )
}
