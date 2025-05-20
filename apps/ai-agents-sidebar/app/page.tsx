"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"

/**
 * Root page component
 *
 * Esta página redireciona do caminho raiz (/) para a página de configurações (/settings)
 * usando navegação client-side.
 */
export default function HomePage() {
  const router = useRouter()

  useEffect(() => {
    router.replace("/settings")
  }, [router])

  // Retorna um loading mínimo enquanto redireciona
  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="text-center">
        <div
          className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-current border-r-transparent align-[-0.125em] motion-reduce:animate-[spin_1.5s_linear_infinite]"
          role="status"
        >
          <span className="!absolute !-m-px !h-px !w-px !overflow-hidden !whitespace-nowrap !border-0 !p-0 ![clip:rect(0,0,0,0)]">
            Loading...
          </span>
        </div>
        <p className="mt-2 text-sm text-gray-500">Redirecionando...</p>
      </div>
    </div>
  )
}
