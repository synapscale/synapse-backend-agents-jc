"use client"

import type { ReactNode } from "react"
import { Button } from "@/components/ui/button"
import { TooltipWrapper } from "@shared/tooltip-wrapper"
import type { WithTooltipProps } from "@/types/shared"

interface HeaderButtonProps extends WithTooltipProps {
  icon: ReactNode
  onClick: () => void
  active?: boolean
  className?: string
}

export function HeaderButton({
  icon,
  onClick,
  tooltip,
  tooltipSide = "bottom",
  active = false,
  className = "",
}: HeaderButtonProps) {
  return (
    <TooltipWrapper tooltip={tooltip} tooltipSide={tooltipSide}>
      <Button
        variant="ghost"
        size="icon"
        className={`rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 ${
          active ? "bg-gray-100 dark:bg-gray-700" : ""
        } ${className}`}
        onClick={onClick}
      >
        {icon}
      </Button>
    </TooltipWrapper>
  )
}
