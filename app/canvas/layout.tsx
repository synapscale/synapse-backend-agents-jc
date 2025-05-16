"use client"

import type React from "react"

import { AppLayout } from "@/components/layout/app-layout"
import { NodeSidebar } from "@/components/node-sidebar/node-sidebar"
import { CanvasProvider } from "@/contexts/canvas-context"

export default function CanvasLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <CanvasProvider>
      <AppLayout sidebar={<NodeSidebar />}>{children}</AppLayout>
    </CanvasProvider>
  )
}
