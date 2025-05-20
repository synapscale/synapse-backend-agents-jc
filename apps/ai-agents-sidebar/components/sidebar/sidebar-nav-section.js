"use strict";
// Arquivo migrado para packages/ui/sidebar/SidebarNavSection.tsx
// Utilize apenas o componente compartilhado.
Object.defineProperty(exports, "__esModule", { value: true });
exports.SidebarNavSection = SidebarNavSection;
var sidebar_1 = require("@/components/ui/sidebar");
function SidebarNavSection(_a) {
    var title = _a.title, children = _a.children;
    return (<sidebar_1.SidebarGroup>
      <sidebar_1.SidebarGroupLabel className="text-xs font-medium text-muted-foreground">{title}</sidebar_1.SidebarGroupLabel>
      <sidebar_1.SidebarGroupContent>
        <sidebar_1.SidebarMenu>{children}</sidebar_1.SidebarMenu>
      </sidebar_1.SidebarGroupContent>
    </sidebar_1.SidebarGroup>);
}
