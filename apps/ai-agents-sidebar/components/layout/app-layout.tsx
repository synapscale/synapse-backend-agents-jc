import React from "react"

interface AppLayoutProps {
  sidebar?: React.ReactNode
  children: React.ReactNode
}

export function AppLayout({ sidebar, children }: AppLayoutProps) {
  return (
    <div style={{ display: "flex", minHeight: "100vh" }}>
      {sidebar && <aside style={{ width: 240, borderRight: "1px solid #eee" }}>{sidebar}</aside>}
      <main style={{ flex: 1 }}>{children}</main>
    </div>
  )
}
