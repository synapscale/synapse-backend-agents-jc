"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { LayoutGrid, FileText, MessageSquare, BarChart2, Users, Settings } from "lucide-react"
import { useApp } from "@/contexts/app-context"

export default function Sidebar() {
  const pathname = usePathname()
  const { isSidebarOpen } = useApp()

  const menuItems = [
    {
      title: "Editor de Workflow",
      icon: <LayoutGrid className="h-5 w-5" />,
      href: "/editor",
    },
    {
      title: "Documentação",
      icon: <FileText className="h-5 w-5" />,
      href: "/docs",
    },
    {
      title: "Chat Interativo",
      icon: <MessageSquare className="h-5 w-5" />,
      href: "/chat",
    },
    {
      title: "Dashboard",
      icon: <BarChart2 className="h-5 w-5" />,
      href: "/dashboard",
    },
    {
      title: "Equipe",
      icon: <Users className="h-5 w-5" />,
      href: "/team",
    },
    {
      title: "Configurações",
      icon: <Settings className="h-5 w-5" />,
      href: "/settings",
    },
  ]

  // Adicionar classe condicional para dispositivos móveis
  const sidebarClass = `w-64 bg-white border-r border-gray-200 h-screen flex flex-col ${
    isSidebarOpen ? "block" : "hidden md:flex"
  }`

  return (
    <div className={sidebarClass}>
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center">
          <div className="h-8 w-8 rounded-md bg-blue-600 text-white flex items-center justify-center font-bold mr-2">
            JC
          </div>
          <div>
            <h2 className="font-bold">Agente AI</h2>
            <p className="text-sm text-gray-500">Canvas</p>
          </div>
        </div>
      </div>
      <nav className="flex-1 p-4">
        <ul className="space-y-2">
          {menuItems.map((item) => {
            const isActive = pathname === item.href
            return (
              <li key={item.href}>
                <Link
                  href={item.href}
                  className={`flex items-center p-2 rounded-md ${
                    isActive ? "bg-gray-100 text-blue-600" : "text-gray-700 hover:bg-gray-50"
                  }`}
                >
                  {item.icon}
                  <span className="ml-3">{item.title}</span>
                </Link>
              </li>
            )
          })}
        </ul>
      </nav>
      <div className="p-4 border-t border-gray-200">
        <div className="flex items-center">
          <div className="h-8 w-8 rounded-full bg-gray-200 flex items-center justify-center mr-2">
            <span className="text-sm">U</span>
          </div>
          <div>
            <p className="text-sm font-medium">Usuário</p>
            <p className="text-xs text-gray-500">Online</p>
          </div>
        </div>
      </div>
    </div>
  )
}
