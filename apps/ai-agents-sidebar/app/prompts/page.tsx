import { Section } from "@/components/ui/section"
import { Card, CardContent } from "@/components/ui/card"

export default function PromptsPage() {
  return (
    <div className="p-4 md:p-6">
      <div className="max-w-7xl mx-auto">
        <Section title="Prompts" description="Biblioteca de prompts para seus agentes">
          <Card>
            <CardContent className="p-6">
              <div className="flex flex-col items-center justify-center min-h-[400px] text-center">
                <h3 className="text-lg font-medium mb-2">Página em Desenvolvimento</h3>
                <p className="text-muted-foreground mb-4">
                  A biblioteca de prompts está sendo desenvolvida e estará disponível em breve.
                </p>
              </div>
            </CardContent>
          </Card>
        </Section>
      </div>
    </div>
  )
}
