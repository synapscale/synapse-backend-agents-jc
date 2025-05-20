"use client"

import { useState } from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Search, Tag, ShoppingBasketIcon as Collection, Star, Package } from "lucide-react"

export function MarketplaceSidebar() {
  const [searchQuery, setSearchQuery] = useState("")
  const pathname = usePathname()

  const isActive = (path: string) => {
    return pathname === path
  }

  return (
    <div className="h-full w-full flex flex-col">
      <div className="p-4">
        <div className="relative">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" aria-hidden="true" />
          <Input
            placeholder="Buscar no marketplace..."
            className="pl-8"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            aria-label="Buscar no marketplace"
          />
        </div>
      </div>

      <div className="px-2 py-2">
        <div className="px-2 py-2 text-sm font-medium">Navegação</div>
        <div className="space-y-1">
          <Link href="/marketplace">
            <Button
              variant={isActive("/marketplace") ? "secondary" : "ghost"}
              className="w-full justify-start"
              aria-pressed={isActive("/marketplace")}
            >
              <Package className="h-4 w-4 mr-2" />
              Todos os Itens
            </Button>
          </Link>
          <Link href="/marketplace/collections">
            <Button
              variant={isActive("/marketplace/collections") ? "secondary" : "ghost"}
              className="w-full justify-start"
              aria-pressed={isActive("/marketplace/collections")}
            >
              <Collection className="h-4 w-4 mr-2" />
              Coleções
            </Button>
          </Link>
          <Link href="/marketplace/favorites">
            <Button
              variant={isActive("/marketplace/favorites") ? "secondary" : "ghost"}
              className="w-full justify-start"
              aria-pressed={isActive("/marketplace/favorites")}
            >
              <Star className="h-4 w-4 mr-2" />
              Favoritos
            </Button>
          </Link>
        </div>
      </div>

      <div className="px-2 py-2">
        <div className="px-2 py-2 text-sm font-medium">Categorias</div>
        <div className="space-y-1">
          <Button variant="ghost" className="w-full justify-start">
            <Tag className="h-4 w-4 mr-2" />
            Processamento de Dados
          </Button>
          <Button variant="ghost" className="w-full justify-start">
            <Tag className="h-4 w-4 mr-2" />
            Inteligência Artificial
          </Button>
          <Button variant="ghost" className="w-full justify-start">
            <Tag className="h-4 w-4 mr-2" />
            Integração de APIs
          </Button>
          <Button variant="ghost" className="w-full justify-start">
            <Tag className="h-4 w-4 mr-2" />
            Automação
          </Button>
        </div>
      </div>
    </div>
  )
}
