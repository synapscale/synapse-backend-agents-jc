import React from 'react';
import { Button } from '@/components/ui/button';
import { SettingsIcon } from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';

interface ChatOptionsProps {
  onClearConversation?: () => void;
  onExportConversation?: () => void;
  onSettings?: () => void;
}

export function ChatOptions({
  onClearConversation,
  onExportConversation,
  onSettings
}: ChatOptionsProps) {
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon">
          <SettingsIcon className="h-5 w-5" />
          <span className="sr-only">Opções de chat</span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        {onClearConversation && (
          <DropdownMenuItem onClick={onClearConversation}>
            Limpar conversa
          </DropdownMenuItem>
        )}
        {onExportConversation && (
          <DropdownMenuItem onClick={onExportConversation}>
            Exportar conversa
          </DropdownMenuItem>
        )}
        {onSettings && (
          <DropdownMenuItem onClick={onSettings}>
            Configurações
          </DropdownMenuItem>
        )}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
