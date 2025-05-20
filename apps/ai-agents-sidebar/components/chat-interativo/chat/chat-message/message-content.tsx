import type { ReactNode } from "react"
import { cn } from "@/lib/utils"
import type { Message } from "@/types/chat"

interface MessageContentProps {
  message: Message
  children: ReactNode
  className?: string
}

export function MessageContent({ message, children, className }: MessageContentProps) {
  const isUserMessage = message.role === "user"
  const isError = message.isError

  return (
    <div
      className={cn(
        "rounded-2xl p-4 shadow-sm border transition-colors duration-200",
        isUserMessage
          ? "bg-primary/10 dark:bg-primary/20 text-gray-800 dark:text-gray-200 border-primary/5 dark:border-primary/10"
          : "bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-200 border-gray-100 dark:border-gray-700",
        isError && "bg-red-50 dark:bg-red-900/20 border-red-100 dark:border-red-800/30",
        className,
      )}
    >
      {children}
    </div>
  )
}
