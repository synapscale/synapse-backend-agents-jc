"use client"

import type React from "react"

import { useRef } from "react"
import { Paperclip } from "lucide-react"
import { Button } from "@/components/ui/button"
import { TooltipWrapper } from "@shared/tooltip-wrapper"
import type { DisableableProps } from "@/types/shared"

interface FileUploadButtonProps extends DisableableProps {
  onFileSelect: (e: React.ChangeEvent<HTMLInputElement>) => void
  acceptedFileTypes: string[]
}

export function FileUploadButton({ onFileSelect, acceptedFileTypes, disabled = false }: FileUploadButtonProps) {
  const fileInputRef = useRef<HTMLInputElement>(null)

  return (
    <>
      <input
        type="file"
        ref={fileInputRef}
        onChange={onFileSelect}
        className="hidden"
        multiple
        accept={acceptedFileTypes.join(",")}
      />
      <TooltipWrapper tooltip={disabled ? "File upload disabled" : "Upload files"}>
        <Button
          variant="ghost"
          size="icon"
          className="h-8 w-8 text-gray-400 hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-300 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700"
          onClick={() => fileInputRef.current?.click()}
          disabled={disabled}
        >
          <Paperclip className="h-5 w-5" />
        </Button>
      </TooltipWrapper>
    </>
  )
}
