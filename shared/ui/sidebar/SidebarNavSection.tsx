import type * as React from "react";

interface SidebarNavSectionProps {
  title: string;
  children: React.ReactNode;
}

export function SidebarNavSection({
  title,
  children,
}: SidebarNavSectionProps) {
  // Adapte aqui para usar componentes compartilhados futuramente
  return (
    <div style={{ marginBottom: 16 }}>
      <div
        style={{
          fontSize: 12,
          fontWeight: 500,
          color: "#888",
          marginBottom: 4,
        }}
      >
        {title}
      </div>
      <div>{children}</div>
    </div>
  );
}
