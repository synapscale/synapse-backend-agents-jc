import * as React from "react";

interface SidebarNavSectionProps {
  title: string;
  children: React.ReactNode;
  collapsible?: boolean;
  defaultCollapsed?: boolean;
}

export function SidebarNavSection({
  title,
  children,
  collapsible = false,
  defaultCollapsed = false,
}: SidebarNavSectionProps) {
  const [isCollapsed, setIsCollapsed] = React.useState(defaultCollapsed);

  const toggleCollapse = React.useCallback(() => {
    if (collapsible) {
      setIsCollapsed(prev => !prev);
    }
  }, [collapsible]);

  return (
    <div style={{ marginBottom: 16 }}>
      <div
        style={{
          fontSize: 12,
          fontWeight: 500,
          color: "#888",
          marginBottom: 4,
          display: "flex",
          alignItems: "center",
          cursor: collapsible ? "pointer" : "default",
        }}
        onClick={toggleCollapse}
      >
        <span style={{ flex: 1 }}>{title}</span>
        {collapsible && (
          <span style={{ fontSize: 10 }}>
            {isCollapsed ? "+" : "-"}
          </span>
        )}
      </div>
      <div style={{ display: isCollapsed ? "none" : "block" }}>
        {children}
      </div>
    </div>
  );
}
