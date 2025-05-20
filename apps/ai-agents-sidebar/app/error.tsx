"use client"

import { useEffect } from "react"
import Link from "next/link"
import { Button } from "@/components/ui/button"

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    // Log the error to an error reporting service
    console.error(error)
  }, [error])

  return (
    <div className="flex min-h-screen flex-col items-center justify-center text-center p-4">
      <div className="max-w-md">
        <h1 className="text-4xl font-bold mb-4">Algo deu errado</h1>
        <p className="text-muted-foreground mb-6">
          Ocorreu um erro ao processar sua solicitação. Nossa equipe foi notificada.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Button onClick={reset} variant="outline">
            Tentar novamente
          </Button>
          <Link href="/">
            <Button className="bg-purple-600 hover:bg-purple-700">Voltar para o início</Button>
          </Link>
        </div>
      </div>
    </div>
  )
}
