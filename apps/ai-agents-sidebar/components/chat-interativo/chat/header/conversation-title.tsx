interface ConversationTitleProps {
  title: string
  isActive?: boolean
}

export function ConversationTitle({ title, isActive = true }: ConversationTitleProps) {
  return (
    <div className="flex items-center">
      <div className={`w-2 h-2 ${isActive ? "bg-green-400" : "bg-gray-300"} rounded-full mr-2`}></div>
      <h2 className="font-medium text-sm truncate ml-1 text-gray-700 dark:text-gray-200">{title}</h2>
    </div>
  )
}
