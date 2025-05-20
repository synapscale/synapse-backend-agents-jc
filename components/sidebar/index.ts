import * as React from "react";

interface IndexExportProps {
  Sidebar: React.ComponentType;
  SidebarNavItem: React.ComponentType<any>;
  SidebarNavSection: React.ComponentType<any>;
}

// Exportando todos os componentes de sidebar de forma centralizada
export const Sidebar = React.lazy(() => import("./Sidebar").then(module => ({ default: module.Sidebar })));
export const SidebarNavItem = React.lazy(() => import("./SidebarNavItem").then(module => ({ default: module.SidebarNavItem })));
export const SidebarNavSection = React.lazy(() => import("./SidebarNavSection").then(module => ({ default: module.SidebarNavSection })));

// Exportação padrão para facilitar importações
const SidebarComponents: IndexExportProps = {
  Sidebar,
  SidebarNavItem,
  SidebarNavSection
};

export default SidebarComponents;
