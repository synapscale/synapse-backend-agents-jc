"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"

export default function NovoAgentePage() {
  const router = useRouter()

  // Redirect to the agent form with "novo" as the ID
  useEffect(() => {
    router.replace("/agentes/novo")
  }, [router])

  return null
}
