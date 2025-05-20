"use client"

import type React from "react"

import { AppLayout } from "@/components/layout/app-layout"
import { MarketplaceSidebar } from "@/components/marketplace/marketplace-sidebar"

export default function MarketplaceLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return <AppLayout sidebar={<MarketplaceSidebar />}>{children}</AppLayout>
}
