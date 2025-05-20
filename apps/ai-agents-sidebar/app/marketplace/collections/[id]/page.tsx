"use client"

import { CollectionDetails } from "@/components/marketplace/collection-details"

export default function CollectionDetailsPage({ params }: { params: { id: string } }) {
  return (
    <div className="h-full p-4">
      <CollectionDetails collectionId={params.id} />
    </div>
  )
}
