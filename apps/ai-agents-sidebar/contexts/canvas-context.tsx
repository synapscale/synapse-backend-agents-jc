import React, { createContext, useContext } from "react"

// Contexto mínimo para evitar erro de importação
const CanvasContext = createContext({})

export const CanvasProvider = ({ children }: { children: React.ReactNode }) => (
  <CanvasContext.Provider value={{}}>{children}</CanvasContext.Provider>
)

export const useCanvas = () => useContext(CanvasContext)
