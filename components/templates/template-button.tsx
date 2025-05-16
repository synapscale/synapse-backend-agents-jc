"use client"

import { useState, useCallback } from "react"
import { FileText } from "lucide-react"
import { TemplatesModal, type PromptTemplate } from "@/components/templates/templates-modal" // Adjusted path
import { IconButton } from "@/components/ui/icon-button"

interface TemplateButtonProps {
  currentPrompt: string
  onSelectTemplate: (template: PromptTemplate) => void
}

export function TemplateButton({ currentPrompt, onSelectTemplate }: TemplateButtonProps) {
  const [isModalOpen, setIsModalOpen] = useState(false)

  const toggleModal = useCallback(() => {
    setIsModalOpen((prev) => !prev)
  }, [])

  const handleSelectTemplate = useCallback(
    (template: PromptTemplate) => {
      onSelectTemplate(template)
      setIsModalOpen(false)
    },
    [onSelectTemplate],
  )

  return (
    <>
      <IconButton
        variant="outline"
        size="sm"
        icon={<FileText />}
        label="Templates"
        className="h-7 sm:h-8 text-xs rounded-full flex-shrink-0"
        onClick={toggleModal}
        aria-haspopup="dialog"
        aria-expanded={isModalOpen}
      />

      <TemplatesModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSelectTemplate={handleSelectTemplate}
        currentPrompt={currentPrompt}
      />
    </>
  )
}

