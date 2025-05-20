import * as React from "react";
import Link from "next/link";

interface SidebarNavItemProps {
  href: string;
  icon: React.ReactNode;
  label: string;
  isActive: boolean;
  className?: string;
  badge?: string | number;
  onClick?: () => void;
}

export function SidebarNavItem({
  href,
  icon,
  label,
  isActive,
  className,
  badge,
  onClick,
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
        onClick={onClick}
      >
        {React.isValidElement(icon)
          ? React.cloneElement(icon as React.ReactElement<any>, {
              className: "sidebar-icon",
              "aria-hidden": "true",
              size: 18,
            })
          : icon}
        <span style={{ flex: 1 }}>{label}</span>
        {badge && (
          <span
            style={{
              display: "inline-flex",
              alignItems: "center",
              justifyContent: "center",
              borderRadius: "9999px",
              padding: "0 6px",
              height: "18px",
              minWidth: "18px",
              fontSize: "12px",
              fontWeight: "500",
              backgroundColor: isActive ? "#7c3aed" : "#e5e7eb",
              color: isActive ? "white" : "#4b5563",
            }}
          >
            {badge}
          </span>
        )}
      </Link>
    </div>
  );
}
