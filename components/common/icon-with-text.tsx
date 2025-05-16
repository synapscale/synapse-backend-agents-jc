import { cn } from "@/lib/utils"
import type { BaseProps, WithIconProps } from "@/types/shared"

interface IconWithTextProps extends BaseProps, WithIconProps {
  text: string
}

export function IconWithText({ icon, text, iconPosition = "left", className }: IconWithTextProps) {
  return (
    <div className={cn("flex items-center", className)}>
      {iconPosition === "left" && icon && <span className="mr-2">{icon}</span>}
      <span>{text}</span>
      {iconPosition === "right" && icon && <span className="ml-2">{icon}</span>}
    </div>
  )
}
