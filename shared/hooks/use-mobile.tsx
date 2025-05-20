import { useEffect, useState } from "react";

/**
 * Hook compartilhado para detectar se está em mobile.
 * Uso: const isMobile = useMobile();
 */
export function useMobile(breakpoint = 768): boolean {
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const checkIfMobile = () => {
      setIsMobile(window.innerWidth < breakpoint);
    };
    checkIfMobile();
    window.addEventListener("resize", checkIfMobile);
    return () => window.removeEventListener("resize", checkIfMobile);
  }, [breakpoint]);

  return isMobile;
}

// Hook compartilhado para todo o ecossistema
// Implemente aqui hooks reutilizáveis e use nos apps
