import React from 'react';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Button } from '@/components/ui/button';
import { TrashIcon } from 'lucide-react';

interface Conversation {
  id: string;
  title: string;
  lastMessage: string;
  timestamp: Date;
}

interface ConversationListProps {
  conversations: Conversation[];
  selectedConversationId?: string;
  onSelectConversation: (id: string) => void;
  onDeleteConversation: (id: string) => void;
}

export function ConversationList({
  conversations,
  selectedConversationId,
  onSelectConversation,
  onDeleteConversation
}: ConversationListProps) {
  return (
    <ScrollArea className="h-full">
      <div className="p-2 space-y-1">
        {conversations.map(conversation => (
          <div
            key={conversation.id}
            className={`flex items-center justify-between p-2 rounded-md ${
              selectedConversationId === conversation.id ? 'bg-secondary' : 'hover:bg-muted/50'
            }`}
          >
            <div 
              className="flex-1 cursor-pointer truncate"
              onClick={() => onSelectConversation(conversation.id)}
            >
              <div className="font-medium truncate">{conversation.title}</div>
              <div className="text-xs text-muted-foreground truncate">
                {conversation.lastMessage}
              </div>
            </div>
            
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8 opacity-0 group-hover:opacity-100 hover:opacity-100"
              onClick={(e) => {
                e.stopPropagation();
                onDeleteConversation(conversation.id);
              }}
            >
              <TrashIcon className="h-4 w-4" />
              <span className="sr-only">Excluir conversa</span>
            </Button>
          </div>
        ))}
        
        {conversations.length === 0 && (
          <div className="text-center py-4 text-sm text-muted-foreground">
            Nenhuma conversa encontrada
          </div>
        )}
      </div>
    </ScrollArea>
  );
}
