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
import { useDialog } from "@/hooks/use-dialog"
import { ConfirmationDialog } from "../ui/confirmation-dialog"

/**
 * CollectionFormData - Interface for collection form data
 *
 * @property {string} name - Collection name
 * @property {string} description - Collection description
 * @property {string[]} tags - Collection tags
 * @property {boolean} isPublic - Whether the collection is public
 * @property {string} [imageUrl] - Optional collection image URL
 */
export interface CollectionFormData {
  name: string
  description: string
  tags: string[]
  isPublic: boolean
  imageUrl?: string
}

/**
 * UserCollectionsProps - Interface for the UserCollections component props
 *
 * @property {string} [title] - Optional custom title for the user collections
 * @property {string} [description] - Optional custom description for the user collections
 * @property {SearchFilters} [initialFilters] - Optional initial search filters to apply
 * @property {boolean} [showSearchBar=true] - Whether to show the search bar
 * @property {boolean} [showPagination=true] - Whether to show pagination controls
 * @property {number} [itemsPerPage=12] - Number of collections to display per page
 * @property {number} [skeletonCount=12] - Number of skeleton items to show during loading
 * @property {(collection: Collection) => void} [onCollectionClick] - Optional callback when a collection is clicked
 * @property {(collection: Collection) => void} [onEditCollection] - Optional callback when edit collection is clicked
 * @property {(collection: Collection) => void} [onDeleteCollection] - Optional callback when delete collection is clicked
 * @property {() => void} [onCreateCollection] - Optional callback when create collection is clicked
 * @property {React.ReactNode} [emptyStateContent] - Optional custom content to display when no collections are found
 * @property {string} [className] - Optional additional CSS classes
 * @property {React.ReactNode} [headerContent] - Optional custom content to display in the header
 * @property {React.ReactNode} [footerContent] - Optional custom content to display in the footer
 * @property {boolean} [showCreateButton=true] - Whether to show the create collection button
 * @property {boolean} [showActionButtons=true] - Whether to show edit and delete buttons on collection cards
 * @property {(formData: CollectionFormData) => Promise<void>} [onSubmitCollectionForm] - Optional callback when collection form is submitted
 */
interface UserCollectionsProps {
  title?: string
  description?: string
  initialFilters?: SearchFilters
  showSearchBar?: boolean
  showPagination?: boolean
  itemsPerPage?: number
  skeletonCount?: number
  onCollectionClick?: (collection: Collection) => void
  onEditCollection?: (collection: Collection) => void
  onDeleteCollection?: (collection: Collection) => void
  onCreateCollection?: () => void
  emptyStateContent?: React.ReactNode
  className?: string
  headerContent?: React.ReactNode
  footerContent?: React.ReactNode
  showCreateButton?: boolean
  showActionButtons?: boolean
  onSubmitCollectionForm?: (formData: CollectionFormData) => Promise<void>
}

/**
 * UserCollections - A component for managing user's collections
 *
 * This component provides a complete interface for viewing and managing a user's
 * collections with search and pagination capabilities. It handles loading states
 * and empty states automatically.
 *
 * @example
 * // Basic usage
 * <UserCollections />
 *
 * @example
 * // With custom callbacks
 * <UserCollections
 *   onCollectionClick={(collection) => router.push(`/collections/${collection.id}`)}
 *   onEditCollection={(collection) => openEditModal(collection)}
 *   onDeleteCollection={(collection) => handleDeleteCollection(collection)}
 * />
 */
export function UserCollections({
  title = "My Collections",
  description = "Manage your personal collections of skills",
  initialFilters = {},
  showSearchBar = true,
  showPagination = true,
  itemsPerPage = 12,
  skeletonCount = 12,
  onCollectionClick,
  onEditCollection,
  onDeleteCollection,
  onCreateCollection,
  emptyStateContent,
  className = "",
  headerContent,
  footerContent,
  showCreateButton = true,
  showActionButtons = true,
  onSubmitCollectionForm,
}: UserCollectionsProps) {
  // State for collections and loading status
  const [collections, setCollections] = useState<Collection[]>([])
  const [isLoading, setIsLoading] = useState<boolean>(true)
  const [totalItems, setTotalItems] = useState<number>(0)
  const [collectionToDelete, setCollectionToDelete] = useState<Collection | null>(null)

  // Use custom hooks for search filters, pagination, and dialog
  const { filters, setFilters, handleSearchChange } = useSearchFilters(initialFilters)

  const { currentPage, setCurrentPage, totalPages, setTotalPages, handlePageChange } = usePagination({
    itemsPerPage,
    totalItems,
    initialPage: 1,
  })

  const { isOpen: isDeleteDialogOpen, open: openDeleteDialog, close: closeDeleteDialog } = useDialog()

  // Fetch user collections based on current filters and pagination
  useEffect(() => {
    const fetchUserCollections = async () => {
      setIsLoading(true)
      try {
        // Calculate pagination parameters
        const offset = (currentPage - 1) * itemsPerPage
        const limit = itemsPerPage

        // Fetch collections from the marketplace service
        const response = await MarketplaceService.getUserCollections({
          ...filters,
          offset,
          limit,
        })

        // Update state with fetched data
        setCollections(response.collections)
        setTotalItems(response.totalCount)
        setTotalPages(Math.ceil(response.totalCount / itemsPerPage))
      } catch (error) {
        console.error("Error fetching user collections:", error)
        setCollections([])
        setTotalItems(0)
        setTotalPages(1)
      } finally {
        setIsLoading(false)
      }
    }

    fetchUserCollections()
  }, [filters, currentPage, itemsPerPage])

  // Reset to first page when filters change
  useEffect(() => {
    setCurrentPage(1)
  }, [filters, setCurrentPage])

  // Handle collection click with optional callback
  const handleCollectionClick = (collection: Collection) => {
    if (onCollectionClick) {
      onCollectionClick(collection)
    }
  }

  // Handle edit collection with optional callback
  const handleEditCollection = (collection: Collection, e: React.MouseEvent) => {
    e.stopPropagation() // Prevent triggering collection click
    if (onEditCollection) {
      onEditCollection(collection)
    }
  }

  // Handle delete collection with confirmation
  const handleDeleteClick = (collection: Collection, e: React.MouseEvent) => {
    e.stopPropagation() // Prevent triggering collection click
    setCollectionToDelete(collection)
    openDeleteDialog()
  }

  // Handle delete confirmation
  const handleDeleteConfirm = async () => {
    if (collectionToDelete && onDeleteCollection) {
      await onDeleteCollection(collectionToDelete)

      // Refresh the collections list
      const newTotalItems = totalItems - 1
      setTotalItems(newTotalItems)

      // If deleting the last item on the page, go to previous page
      const newTotalPages = Math.ceil(newTotalItems / itemsPerPage)
      if (currentPage > newTotalPages && currentPage > 1) {
        setCurrentPage(currentPage - 1)
      } else {
        // Refresh the current page
        const offset = (currentPage - 1) * itemsPerPage
        const limit = itemsPerPage

        const response = await MarketplaceService.getUserCollections({
          ...filters,
          offset,
          limit,
        })

        setCollections(response.collections)
      }
    }

    closeDeleteDialog()
    setCollectionToDelete(null)
  }

  // Handle create collection with optional callback
  const handleCreateCollection = () => {
    if (onCreateCollection) {
      onCreateCollection()
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

    return (
      <div className="flex flex-col items-center justify-center p-8 text-center">
        <h3 className="text-xl font-semibold mb-2">You don't have any collections yet</h3>
        <p className="text-gray-500 mb-4">Create your first collection to organize your skills.</p>
        <button
          className="px-4 py-2 bg-primary text-white rounded-md hover:bg-primary/90 transition-colors"
          onClick={handleCreateCollection}
        >
          Create Collection
        </button>
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
            onClick={handleCreateCollection}
            aria-label="Create new collection"
          >
            Create Collection
          </button>
        )}
      </div>

      {/* Custom header content */}
      {headerContent}

      {/* Search bar */}
      {showSearchBar && (
        <div className="mb-6">
          <SearchBar
            placeholder="Search your collections..."
            value={filters.searchTerm || ""}
            onChange={handleSearchChange}
            onClear={() => handleSearchChange("")}
            className="w-full max-w-xl"
            debounceMs={300}
            aria-label="Search your collections"
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
              showActions={showActionButtons}
              onEdit={(e) => handleEditCollection(collection, e)}
              onDelete={(e) => handleDeleteClick(collection, e)}
              aria-label={`Collection: ${collection.name}`}
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

      {/* Custom footer content */}
      {footerContent}

      {/* Delete confirmation dialog */}
      <ConfirmationDialog
        isOpen={isDeleteDialogOpen}
        onClose={closeDeleteDialog}
        onConfirm={handleDeleteConfirm}
        title="Delete Collection"
        message={
          collectionToDelete
            ? `Are you sure you want to delete "${collectionToDelete.name}"? This action cannot be undone.`
            : "Are you sure you want to delete this collection? This action cannot be undone."
        }
        confirmLabel="Delete"
        confirmVariant="danger"
        cancelLabel="Cancel"
      />
    </div>
  )
}
