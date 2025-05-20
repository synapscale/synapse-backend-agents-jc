"use client"

import type React from "react"

import { CanvasProvider } from "@/contexts/canvas-context"

export default function CanvasLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return <CanvasProvider>{children}</CanvasProvider>
}
