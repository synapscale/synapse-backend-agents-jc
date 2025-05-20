import React from "react"

export function SettingsSidebar() {
  return (
    <nav style={{ padding: 24 }}>
      <h2 style={{ fontWeight: 600, marginBottom: 16 }}>Configurações</h2>
      <ul style={{ listStyle: "none", padding: 0 }}>
        <li><a href="/settings">Geral</a></li>
        {/* Adicione mais links de configurações aqui */}
      </ul>
    </nav>
  )
}
