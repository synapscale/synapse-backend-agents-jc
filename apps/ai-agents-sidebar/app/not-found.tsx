import Link from "next/link"
import { Button } from "@/components/ui/button"

export default function NotFound() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center text-center p-4">
      <div className="max-w-md">
        <h1 className="text-4xl font-bold mb-4">404 - Página não encontrada</h1>
        <p className="text-muted-foreground mb-6">A página que você está procurando não existe ou foi movida.</p>
        <Link href="/">
          <Button className="bg-purple-600 hover:bg-purple-700">Voltar para o início</Button>
        </Link>
      </div>
    </div>
  )
}
