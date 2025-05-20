"use client"

/// <reference types="react" />

import { useState, useEffect, useCallback } from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { Bot, LayoutDashboard, Settings, Sparkles, Layers, FileText, MessageSquare, Menu, X } from "lucide-react"
// Os componentes Button, cn, Sidebar, SidebarContent, SidebarHeader devem ser importados do próprio pacote ui ou de pacotes compartilhados futuramente
import { SidebarNavItem } from "./SidebarNavItem"
import { SidebarNavSection } from "./SidebarNavSection"

const NAV_SECTIONS = [
	{
		title: "Principal",
		items: [
			{ href: "/dashboard", label: "Dashboard", icon: <LayoutDashboard /> },
			{ href: "/agentes", label: "Agentes De IA", icon: <Bot /> },
		],
	},
	{
		title: "Ferramentas",
		items: [
			{ href: "/canvas", label: "Canvas", icon: <Layers /> },
			{ href: "/prompts", label: "Prompts", icon: <FileText /> },
			{ href: "/chat", label: "Chat", icon: <MessageSquare /> },
		],
	},
	{
		title: "Configurações",
		items: [{ href: "/settings", label: "Configurações", icon: <Settings /> }],
	},
]

export const Sidebar = () => {
	const pathname = usePathname()
	const [isMobile, setIsMobile] = useState(false)
	const [isOpen, setIsOpen] = useState(false)

	useEffect(() => {
		const checkIfMobile = () => {
			setIsMobile(window.innerWidth < 768)
		}
		checkIfMobile()
		window.addEventListener("resize", checkIfMobile)
		return () => window.removeEventListener("resize", checkIfMobile)
	}, [])

	useEffect(() => {
		if (isMobile) {
			setIsOpen(false)
		}
	}, [pathname, isMobile])

	const toggleSidebar = useCallback(() => {
		setIsOpen((prev) => !prev)
	}, [])

	const isItemActive = useCallback(
		(href: string) => {
			if (href === "/agentes") {
				return pathname === "/agentes" || pathname.startsWith("/agentes/")
			}
			return pathname === href
		},
		[pathname],
	)

	return (
		<>
			{/* Botão de menu para dispositivos móveis */}
			{isMobile && (
				<button
					onClick={toggleSidebar}
					aria-label={isOpen ? "Fechar menu" : "Abrir menu"}
					aria-expanded={isOpen}
					aria-controls="sidebar"
					style={{ position: 'fixed', top: 12, left: 12, zIndex: 50, height: 36, width: 36 }}
				>
					{isOpen ? <X size={20} /> : <Menu size={20} />}
				</button>
			)}

			<div
				id="sidebar"
				aria-label="Navegação principal"
				style={{
					border: 0,
					transition: 'all 0.3s',
					position: isMobile ? 'fixed' : 'relative',
					top: 0,
					left: 0,
					zIndex: 40,
					height: '100%',
					background: '#fff',
					transform: isMobile ? (isOpen ? 'translateX(0)' : 'translateX(-100%)') : 'none',
					width: 256,
				}}
			>
				<div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 16 }}>
					<Link href="/" aria-label="Página inicial" style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
						<div style={{ display: 'flex', height: 32, width: 32, alignItems: 'center', justifyContent: 'center', borderRadius: 8, background: '#9333ea', color: '#fff' }}>
							<Sparkles size={16} />
						</div>
						<span style={{ fontSize: 16, fontWeight: 600 }}>Canva E Agentes</span>
					</Link>
				</div>
				<div>
					{NAV_SECTIONS.map((section) => (
						<SidebarNavSection key={section.title} title={section.title}>
							{section.items.map((item) => (
								<SidebarNavItem
									key={item.href}
									href={item.href}
									icon={item.icon}
									label={item.label}
									isActive={isItemActive(item.href)}
								/>
							))}
						</SidebarNavSection>
					))}
				</div>
			</div>

			{/* Overlay para dispositivos móveis */}
			{isMobile && isOpen && (
				<div
					onClick={toggleSidebar}
					style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.2)', zIndex: 30, backdropFilter: 'blur(2px)' }}
					aria-hidden="true"
				/>
			)}
		</>
	)
}
