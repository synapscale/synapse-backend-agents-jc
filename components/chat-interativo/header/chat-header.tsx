import { ConversationTitle } from "./conversation-title"
import { HeaderActions } from "./header-actions"
import ConversationHeader from "../conversation-header"
import type { Conversation } from "@/types/chat"

interface ChatHeaderProps {
  currentConversation: Conversation | undefined
  currentConversationId: string | null
  onNewConversation: () => void
  onUpdateConversationTitle: (title: string) => void
  onDeleteConversation: (id: string) => void
  onExportConversation: () => void
  onToggleSidebar: () => void
  showComponentSelector?: boolean
  onToggleComponentSelector?: () => void
}

export function ChatHeader({
  currentConversation,
  currentConversationId,
  onNewConversation,
  onUpdateConversationTitle,
  onDeleteConversation,
  onExportConversation,
  onToggleSidebar,
  showComponentSelector,
  onToggleComponentSelector,
}: ChatHeaderProps) {
  return (
    <div className="bg-white dark:bg-gray-800 border-b border-gray-100 dark:border-gray-700 shadow-sm flex items-center justify-between p-3 sticky top-0 z-10 transition-colors duration-200">
      <div className="flex items-center">
        {currentConversation && <ConversationTitle title={currentConversation.title} />}
      </div>

      <div className="flex items-center">
        <HeaderActions
          onNewChat={onNewConversation}
          onToggleSidebar={onToggleSidebar}
          showComponentSelector={showComponentSelector}
          onToggleComponentSelector={onToggleComponentSelector}
          isMobile={true}
        />

        {currentConversation && (
          <div className="mr-4">
            <ConversationHeader
              conversation={currentConversation}
              onUpdateTitle={onUpdateConversationTitle}
              onDeleteConversation={() => currentConversationId && onDeleteConversation(currentConversationId)}
              onExportConversation={onExportConversation}
            />
          </div>
        )}
      </div>
    </div>
  )
}
