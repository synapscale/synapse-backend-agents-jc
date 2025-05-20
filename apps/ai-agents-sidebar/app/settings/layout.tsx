"use client"

import type React from "react"

import { AppLayout } from "@/components/layout/app-layout"
import { SettingsSidebar } from "@/components/settings/settings-sidebar"

export default function SettingsLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return <AppLayout sidebar={<SettingsSidebar />}>{children}</AppLayout>
}
