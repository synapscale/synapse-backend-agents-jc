import * as React from "react";
import Link from "next/link";

interface SidebarNavItemProps {
  href: string;
  icon: React.ReactNode;
  label: string;
  isActive: boolean;
  className?: string;
}

export function SidebarNavItem({
  href,
  icon,
  label,
  isActive,
  className,
}: SidebarNavItemProps) {
  return (
    <div style={{ marginBottom: 8 }}>
      <Link
        href={href}
        style={{
          display: "flex",
          alignItems: "center",
          padding: "8px 12px",
          borderRadius: 6,
          background: isActive ? "#ede9fe" : "transparent",
          color: isActive ? "#7c3aed" : "#222",
          fontWeight: 500,
          fontSize: 14,
          textDecoration: "none",
          gap: 8,
        }}
      >
        {React.isValidElement(icon)
          ? React.cloneElement(icon as React.ReactElement<any>, {
              className: "sidebar-icon",
              "aria-hidden": "true",
            })
          : icon}
        <span>{label}</span>
      </Link>
    </div>
  );
}
