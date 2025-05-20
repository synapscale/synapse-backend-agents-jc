// Página migrada do node-sidebar
"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { MarketplaceBrowser } from "../../components/marketplace/marketplace-browser"
import { UserMarketplaceItems } from "../../components/marketplace/user-marketplace-items"

// Static placeholder component for PublishSkillForm
function StaticPublishSkillForm() {
  return (
    <div className="p-4">
      <h2 className="text-xl font-bold mb-4">Publish Skill</h2>
      <p>This is a static placeholder for the publish skill form.</p>
    </div>
  )
}

export default function MarketplacePage() {
  // Use a simple string state for the active tab
  const [activeTab, setActiveTab] = useState("browse")

  // Render the appropriate content based on the active tab
  let content
  if (activeTab === "browse") {
    content = <MarketplaceBrowser />
  } else if (activeTab === "my-items") {
    content = <UserMarketplaceItems />
  } else if (activeTab === "publish") {
    content = <StaticPublishSkillForm />
  }

  return (
    <div className="h-full flex flex-col">
      <div className="border-b">
        <div className="container mx-auto px-4 py-2">
          <div className="flex space-x-1">
            <Button
              variant={activeTab === "browse" ? "default" : "ghost"}
              onClick={() => setActiveTab("browse")}
              className="rounded-none border-b-2 border-transparent data-[state=active]:border-primary"
            >
              Explorar
            </Button>
            <Button
              variant={activeTab === "my-items" ? "default" : "ghost"}
              onClick={() => setActiveTab("my-items")}
              className="rounded-none border-b-2 border-transparent data-[state=active]:border-primary"
            >
              Meus Itens
            </Button>
            <Button
              variant={activeTab === "publish" ? "default" : "ghost"}
              onClick={() => setActiveTab("publish")}
              className="rounded-none border-b-2 border-transparent data-[state=active]:border-primary"
            >
              Publicar Skill
            </Button>
          </div>
        </div>
      </div>
      <div className="flex-1 overflow-auto">
        {content}
      </div>
    </div>
  )
}
