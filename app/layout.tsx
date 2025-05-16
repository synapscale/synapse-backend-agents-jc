import type React from "react"
import type { Metadata } from "next"
import { Inter } from "next/font/google"
import "./globals.css"
import { ThemeProvider } from "@/components/theme-provider"
import { AppProvider } from "@/contexts/app-context"
import ComponentSelector from "@/components/component-selector/component-selector"

const inter = Inter({ subsets: ["latin"] })

export const metadata: Metadata = {
  title: "Chat Interativo",
  description: "Interface de chat interativa com múltiplos modelos e ferramentas",
    generator: 'v0.dev'
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="pt-BR" suppressHydrationWarning>
      <body className={inter.className}>
        <ThemeProvider attribute="class" defaultTheme="system" enableSystem disableTransitionOnChange>
          <AppProvider>
            {children}
            <ComponentSelector />
          </AppProvider>
        </ThemeProvider>
      </body>
    </html>
  )
}
