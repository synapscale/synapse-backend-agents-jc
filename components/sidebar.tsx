"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { motion, AnimatePresence } from "framer-motion"
import { 
  LayoutGrid, 
  FileText, 
  MessageSquare, 
  Users, 
  Settings, 
  ChevronLeft,
  ChevronRight,
  Download,
  Home,
  Layers,
  Bot,
  FileCode,
  MessagesSquare,
  UserRound,
  Cog
} from "lucide-react"
import { useSidebar } from "@/context/sidebar-context"

export function Sidebar() {
  const pathname = usePathname()
  const [isMobile, setIsMobile] = useState(false)
  const { isCollapsed, isOpen, toggle, toggleCollapse } = useSidebar()

  // Detectar se é mobile
  useEffect(() => {
    const checkIfMobile = () => {
      setIsMobile(window.innerWidth < 768)
      if (window.innerWidth < 768) {
        // Não fazemos nada com o estado de colapso aqui, apenas detectamos mobile
      }
    }
    
    checkIfMobile()
    window.addEventListener("resize", checkIfMobile)
    
    return () => {
      window.removeEventListener("resize", checkIfMobile)
    }
  }, [])

  // Fechar sidebar no mobile quando mudar de rota
  useEffect(() => {
    if (isMobile && isOpen) {
      toggle()
    }
  }, [pathname, isMobile, isOpen, toggle])

  const toggleSidebar = () => {
    if (isMobile) {
      toggle()
    } else {
      toggleCollapse()
    }
  }

  const sidebarVariants = {
    expanded: { width: "16rem", transition: { duration: 0.3, ease: "easeInOut" } },
    collapsed: { width: "4.5rem", transition: { duration: 0.3, ease: "easeInOut" } },
    mobileOpen: { x: 0, transition: { duration: 0.3, ease: "easeInOut" } },
    mobileClosed: { x: "-100%", transition: { duration: 0.3, ease: "easeInOut" } }
  }

  const navItems = [
    {
      name: "Editor de Workflow",
      href: "/",
      icon: <Home className="h-5 w-5" />,
    },
    {
      name: "Canvas",
      href: "/canvas",
      icon: <Layers className="h-5 w-5" />,
    },
    {
      name: "Agentes De IA",
      href: "/agentes",
      icon: <Bot className="h-5 w-5" />,
    },
    {
      name: "Documentação",
      href: "/docs",
      icon: <FileCode className="h-5 w-5" />,
    },
    {
      name: "Chat Interativo",
      href: "/chat",
      icon: <MessagesSquare className="h-5 w-5" />,
    },
    {
      name: "Equipe",
      href: "/team",
      icon: <UserRound className="h-5 w-5" />,
    },
    {
      name: "Configurações",
      href: "/settings",
      icon: <Cog className="h-5 w-5" />,
    },
  ]

  return (
    <>
      {/* Overlay para mobile */}
      {isMobile && isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 0.5 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 bg-black z-40"
          onClick={toggle}
        />
      )}
      
      {/* Sidebar */}
      <motion.nav
        className="fixed top-0 left-0 h-full bg-card border-r border-border overflow-hidden shadow-md"
        style={{ zIndex: 40 }}
        variants={isMobile ? 
          { open: sidebarVariants.mobileOpen, closed: sidebarVariants.mobileClosed } : 
          { expanded: sidebarVariants.expanded, collapsed: sidebarVariants.collapsed }
        }
        initial={isMobile ? "closed" : "expanded"}
        animate={isMobile ? (isOpen ? "open" : "closed") : (isCollapsed ? "collapsed" : "expanded")}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4">
          <Link href="/" className="flex items-center gap-2">
            <div className="flex items-center justify-center w-9 h-9 rounded-md bg-transparent text-white shadow-sm">
              <img src="/images/synapscale-symbol.png" alt="SynapScale Logo" className="w-8 h-8" />
            </div>
            {(!isCollapsed || (isMobile && isOpen)) && (
              <motion.span
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="font-semibold text-lg bg-gradient-to-r from-[#f35500] to-[#ff7e00] bg-clip-text text-transparent"
              >
                SynapScale
              </motion.span>
            )}
          </Link>
          
          {/* Botão de toggle */}
          <button
            onClick={toggleSidebar}
            className="p-1.5 rounded-md hover:bg-muted transition-colors hover:text-primary"
            aria-label={isCollapsed ? "Expandir sidebar" : "Colapsar sidebar"}
          >
            {isCollapsed || (isMobile && !isOpen) ? 
              <ChevronRight className="h-4 w-4" /> : 
              <ChevronLeft className="h-4 w-4" />
            }
          </button>
        </div>
        
        {/* Links de navegação */}
        <div className="py-4">
          <ul className="space-y-1 px-2">
            {navItems.map((item) => {
              const isActive = pathname === item.href || pathname.startsWith(`${item.href}/`)
              
              return (
                <li key={item.href}>
                  <Link
                    href={item.href}
                    className={`flex items-center gap-3 px-3 py-2.5 rounded-md transition-all duration-200 ${
                      isActive 
                        ? "bg-gradient-to-r from-primary/20 to-primary/5 text-primary font-medium shadow-sm" 
                        : "text-muted-foreground hover:bg-muted hover:text-foreground"
                    }`}
                  >
                    <motion.div
                      whileHover={{ scale: 1.1 }}
                      whileTap={{ scale: 0.95 }}
                      className={isActive ? "text-primary" : "text-muted-foreground"}
                    >
                      {item.icon}
                    </motion.div>
                    
                    {(!isCollapsed || (isMobile && isOpen)) && (
                      <motion.span
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        transition={{ duration: 0.2 }}
                      >
                        {item.name}
                      </motion.span>
                    )}
                  </Link>
                </li>
              )
            })}
          </ul>
        </div>
        
        {/* Footer */}
        <div className="absolute bottom-0 left-0 right-0 p-4">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-full bg-gradient-to-br from-[#f35500] to-[#ff7e00] flex items-center justify-center shadow-sm">
              <span className="text-sm font-medium text-white">U</span>
            </div>
            
            {(!isCollapsed || (isMobile && isOpen)) && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="flex flex-col"
              >
                <span className="text-sm font-medium">Usuário</span>
                <span className="text-xs text-muted-foreground">Online</span>
              </motion.div>
            )}
          </div>
        </div>
      </motion.nav>
      
      {/* Botão de menu mobile */}
      {isMobile && !isOpen && (
        <motion.button
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed top-4 left-4 z-50 p-2 rounded-md bg-card shadow-md"
          onClick={toggle}
          aria-label="Abrir menu"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="h-5 w-5">
            <line x1="3" y1="12" x2="21" y2="12"></line>
            <line x1="3" y1="6" x2="21" y2="6"></line>
            <line x1="3" y1="18" x2="21" y2="18"></line>
          </svg>
        </motion.button>
      )}
    </>
  )
}
