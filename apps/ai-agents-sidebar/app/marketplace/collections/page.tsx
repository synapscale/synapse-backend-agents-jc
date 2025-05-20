"use client"

import { CollectionsBrowser } from "@/components/marketplace/collections-browser"

export default function CollectionsPage() {
  return (
    <div className="h-full p-4">
      <h1 className="text-2xl font-bold mb-4">Coleções</h1>
      <CollectionsBrowser />
    </div>
  )
}
