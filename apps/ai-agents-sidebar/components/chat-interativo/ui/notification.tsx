"use client"

import { useEffect, useState } from "react"
import { X, CheckCircle, AlertCircle, Info } from "lucide-react"
import { useApp } from "@/contexts/app-context"

type NotificationType = "success" | "error" | "info"

interface NotificationProps {
  type?: NotificationType
  message?: string
  duration?: number
  onClose?: () => void
}

export function Notification({ type = "info", message: propMessage, duration = 3000, onClose }: NotificationProps) {
  const [visible, setVisible] = useState(true)
  const { lastAction, setLastAction } = useApp()
  const message = propMessage || lastAction

  useEffect(() => {
    if (message) {
      setVisible(true)
      const timer = setTimeout(() => {
        setVisible(false)
        if (onClose) onClose()
        if (!propMessage) setLastAction(null)
      }, duration)

      return () => clearTimeout(timer)
    } else {
      setVisible(false)
    }
  }, [message, duration, onClose, propMessage, setLastAction])

  if (!message || !visible) return null

  const icons = {
    success: <CheckCircle className="h-5 w-5 text-green-500" />,
    error: <AlertCircle className="h-5 w-5 text-red-500" />,
    info: <Info className="h-5 w-5 text-primary" />,
  }

  const bgColors = {
    success: "bg-green-50 dark:bg-green-900/20 border-green-100 dark:border-green-800/30",
    error: "bg-red-50 dark:bg-red-900/20 border-red-100 dark:border-red-800/30",
    info: "bg-primary-50 dark:bg-primary-900/20 border-primary-100 dark:border-primary-800/30",
  }

  const textColors = {
    success: "text-green-800 dark:text-green-300",
    error: "text-red-800 dark:text-red-300",
    info: "text-primary-800 dark:text-primary-300",
  }

  return (
    <div className="fixed bottom-4 right-4 z-50 animate-in slide-in-from-bottom-5">
      <div className={`flex items-center p-3 pr-4 rounded-lg shadow-md border ${bgColors[type]}`}>
        <div className="mr-3">{icons[type]}</div>
        <div className={`mr-2 text-sm font-medium ${textColors[type]}`}>{message}</div>
        <button
          onClick={() => {
            setVisible(false)
            if (onClose) onClose()
            if (!propMessage) setLastAction(null)
          }}
          className="ml-auto -mr-1 flex-shrink-0 rounded-full p-1 hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
        >
          <X className="h-4 w-4 text-gray-500 dark:text-gray-400" />
        </button>
      </div>
    </div>
  )
}
