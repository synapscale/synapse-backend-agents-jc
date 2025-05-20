"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.SidebarNavItem = SidebarNavItem;
var React = require("react");
var link_1 = require("next/link");
var utils_1 = require("@/lib/utils");
var sidebar_1 = require("@/components/ui/sidebar");
function SidebarNavItem(_a) {
    var href = _a.href, icon = _a.icon, label = _a.label, isActive = _a.isActive, className = _a.className;
    return (<sidebar_1.SidebarMenuItem>
      <sidebar_1.SidebarMenuButton asChild isActive={isActive} className={(0, utils_1.cn)("transition-colors py-1.5 sm:py-2 text-xs sm:text-sm", className)}>
        <link_1.default href={href}>
          {React.cloneElement(icon, {
            className: "mr-2 h-3.5 w-3.5 sm:h-4 sm:w-4",
            "aria-hidden": "true",
        })}
          <span>{label}</span>
        </link_1.default>
      </sidebar_1.SidebarMenuButton>
    </sidebar_1.SidebarMenuItem>);
}
// Arquivo migrado para packages/ui/sidebar/SidebarNavItem.tsx
// Utilize apenas o componente compartilhado.
