"use client"

import React from "react"
import { NodeSidebar } from "../../../../components/workflow/node-sidebar"

export default function WorkflowPage() {
  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Editor de Workflow</h1>
      <div className="bg-white rounded-lg shadow-md p-4">
        <NodeSidebar />
      </div>
    </div>
  )
}
