"use client";

import React from "react";

interface AppLayoutProps {
  children: React.ReactNode;
  sidebar?: React.ReactNode; // Adicionada a prop sidebar opcional
}

export function AppLayout({ children, sidebar }: AppLayoutProps) {
  return (
    <div className="flex h-screen overflow-hidden">
      {sidebar && <div className="hidden lg:block">{sidebar}</div>} {/* Renderiza a sidebar se fornecida */}
      <main className="flex-1 overflow-y-auto p-0 flex flex-col">
        {/* Conteúdo do AppLayout - pode ser ajustado conforme necessário */}
        {/* Removido header e footer placeholders para um layout mais genérico inicialmente */}
        {children}
      </main>
    </div>
  );
}

export default AppLayout;

