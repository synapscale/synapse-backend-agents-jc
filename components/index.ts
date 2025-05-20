import * as React from "react";

// Exportação dos componentes principais
export { default as Sidebar } from "./sidebar/Sidebar";
export { SidebarNavItem } from "./sidebar/SidebarNavItem";
export { SidebarNavSection } from "./sidebar/SidebarNavSection";

// Exportação dos componentes de chat
export * from "./chat";

// Exportação dos componentes de workflow
export * from "./workflow";

// Exportação dos componentes de UI
export { default as SidebarProvider, useSidebar } from "./ui/sidebar";

// Exportação padrão para facilitar importações
const Components = {
  // Adicionar aqui todos os componentes principais à medida que forem criados
};

export default Components;
