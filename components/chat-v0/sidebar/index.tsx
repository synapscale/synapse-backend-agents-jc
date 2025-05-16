import React from 'react';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { PlusIcon } from 'lucide-react';

interface Conversation {
  id: string;
  title: string;
  lastMessage: string;
  timestamp: Date;
}

interface ChatSidebarProps {
  conversations: Conversation[];
  selectedConversationId?: string;
  onSelectConversation: (id: string) => void;
  onNewConversation: () => void;
}

export function ChatSidebar({
  conversations,
  selectedConversationId,
  onSelectConversation,
  onNewConversation
}: ChatSidebarProps) {
  return (
    <div className="w-64 border-r h-full flex flex-col">
      <div className="p-4 border-b">
        <Button 
          onClick={onNewConversation}
          className="w-full"
        >
          <PlusIcon className="h-4 w-4 mr-2" />
          Nova Conversa
        </Button>
      </div>
      
      <ScrollArea className="flex-1">
        <div className="p-2 space-y-1">
          {conversations.map(conversation => (
            <Button
              key={conversation.id}
              variant={selectedConversationId === conversation.id ? "secondary" : "ghost"}
              className="w-full justify-start text-left h-auto py-2"
              onClick={() => onSelectConversation(conversation.id)}
            >
              <div className="truncate">
                <div className="font-medium truncate">{conversation.title}</div>
                <div className="text-xs text-muted-foreground truncate">
                  {conversation.lastMessage}
                </div>
              </div>
            </Button>
          ))}
          
          {conversations.length === 0 && (
            <div className="text-center py-4 text-sm text-muted-foreground">
              Nenhuma conversa encontrada
            </div>
          )}
        </div>
      </ScrollArea>
    </div>
  );
}
