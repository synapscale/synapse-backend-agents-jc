"use client"

import { useState } from "react"
import Link from "next/link";
import { usePathname } from 'next/navigation';
import {
  ChevronLeft,
  ChevronRight,
  LayoutGrid,
  Settings,
  Users,
  Workflow,
  FileText, // Ícone para Documentação
  MessageCircle // Ícone para Chat
} from "lucide-react"
import { cn } from "@/lib/utils"

interface SidebarProps {
  className?: string
}

const navItems = [
  { href: "/", icon: Workflow, label: "Editor de Workflow" },
  { href: "/docs", icon: FileText, label: "Documentação" },
  { href: "/chat", icon: MessageCircle, label: "Chat Interativo" },
  { href: "/dashboard", icon: LayoutGrid, label: "Dashboard" }, // Exemplo, pode ser removido ou adaptado
  { href: "/team", icon: Users, label: "Equipe" }, // Exemplo, pode ser removido ou adaptado
  { href: "/settings", icon: Settings, label: "Configurações" }, // Exemplo, pode ser removido ou adaptado
];

export function Sidebar({ className }: SidebarProps) {
  const [collapsed, setCollapsed] = useState(false);
  const pathname = usePathname();

  return (
    <div
      className={cn(
        "flex h-full flex-col border-r bg-white dark:bg-gray-900 dark:border-gray-700 transition-all duration-300 ease-in-out",
        collapsed ? "w-16" : "w-64",
        className,
      )}
    >
      {/* Header with logo and collapse button */}
      <div className="flex h-16 items-center justify-between border-b dark:border-gray-700 px-4">
        <div className="flex items-center overflow-hidden">
          <Link href="/" className="flex-shrink-0">
            <div className="flex h-8 w-8 items-center justify-center rounded-md bg-blue-600 text-white">JC</div>
          </Link>
          <h1
            className={cn(
              "ml-3 text-lg font-semibold text-gray-800 dark:text-white transition-opacity duration-200",
              collapsed ? "opacity-0 w-0" : "opacity-100",
            )}
          >
            Agente AI Canvas
          </h1>
        </div>
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="flex h-8 w-8 items-center justify-center rounded-md hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-600 dark:text-gray-400"
        >
          {collapsed ? <ChevronRight size={18} /> : <ChevronLeft size={18} />}
        </button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto p-2">
        <ul className="space-y-1">
          {navItems.map((item) => (
            <li key={item.label}>
              <Link
                href={item.href}
                className={cn(
                  "flex items-center rounded-md px-3 py-2 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800",
                  pathname === item.href && "bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400",
                )}
              >
                <item.icon size={20} className="flex-shrink-0" />
                <span
                  className={cn(
                    "ml-3 transition-opacity duration-200",
                    collapsed ? "opacity-0 w-0 hidden" : "opacity-100",
                  )}
                >
                  {item.label}
                </span>
              </Link>
            </li>
          ))}
        </ul>
      </nav>

      {/* Footer */}
      <div className="border-t dark:border-gray-700 p-4">
        <div className="flex items-center">
          <div className="h-8 w-8 rounded-full bg-gray-200 dark:bg-gray-700">
            {/* Idealmente, uma imagem de usuário aqui */}
          </div>
          <div className={cn("ml-3 transition-opacity duration-200", collapsed ? "opacity-0 w-0" : "opacity-100")}>
            <p className="text-sm font-medium text-gray-800 dark:text-white">Usuário</p>
            <p className="text-xs text-gray-500 dark:text-gray-400">Online</p>
          </div>
        </div>
      </div>
    </div>
  )
}

