import type { ReactNode } from "react"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"
import type { WithTooltipProps } from "@/types/shared"

interface TooltipWrapperProps extends WithTooltipProps {
  children: ReactNode
}

export function TooltipWrapper({
  children,
  tooltip,
  tooltipSide = "top",
  tooltipAlign = "center",
}: TooltipWrapperProps) {
  if (!tooltip) return <>{children}</>

  return (
    <TooltipProvider>
      <Tooltip delayDuration={300}>
        <TooltipTrigger asChild>{children}</TooltipTrigger>
        <TooltipContent side={tooltipSide} align={tooltipAlign}>
          {tooltip}
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  )
}
