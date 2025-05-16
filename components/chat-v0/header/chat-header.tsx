import React from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { 
  MoreHorizontalIcon, 
  ShareIcon, 
  DownloadIcon, 
  PencilIcon,
  CheckIcon,
  XIcon
} from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';

interface ChatHeaderProps {
  title: string;
  onRename?: (newTitle: string) => void;
  onShare?: () => void;
  onExport?: () => void;
  onSettings?: () => void;
}

export function ChatHeader({
  title,
  onRename,
  onShare,
  onExport,
  onSettings
}: ChatHeaderProps) {
  const [isEditing, setIsEditing] = React.useState(false);
  const [editedTitle, setEditedTitle] = React.useState(title);
  const inputRef = React.useRef<HTMLInputElement>(null);

  // Focar no input quando entrar no modo de edição
  React.useEffect(() => {
    if (isEditing && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isEditing]);

  // Iniciar edição do título
  const handleStartEditing = () => {
    setEditedTitle(title);
    setIsEditing(true);
  };

  // Salvar o título editado
  const handleSaveTitle = () => {
    if (onRename && editedTitle.trim()) {
      onRename(editedTitle);
    }
    setIsEditing(false);
  };

  // Cancelar a edição
  const handleCancelEditing = () => {
    setEditedTitle(title);
    setIsEditing(false);
  };

  // Lidar com tecla Enter e Escape
  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      handleSaveTitle();
    } else if (e.key === 'Escape') {
      handleCancelEditing();
    }
  };

  return (
    <header className="flex items-center justify-between p-4 border-b">
      <div className="flex items-center gap-2">
        {isEditing ? (
          <div className="flex items-center gap-1">
            <Input
              ref={inputRef}
              value={editedTitle}
              onChange={(e) => setEditedTitle(e.target.value)}
              onKeyDown={handleKeyDown}
              className="h-8 w-[200px]"
            />
            <Button
              variant="ghost"
              size="icon"
              onClick={handleSaveTitle}
              className="h-8 w-8"
            >
              <CheckIcon className="h-4 w-4" />
              <span className="sr-only">Salvar</span>
            </Button>
            <Button
              variant="ghost"
              size="icon"
              onClick={handleCancelEditing}
              className="h-8 w-8"
            >
              <XIcon className="h-4 w-4" />
              <span className="sr-only">Cancelar</span>
            </Button>
          </div>
        ) : (
          <div className="flex items-center gap-2">
            <h2 className="text-lg font-medium">{title}</h2>
            {onRename && (
              <Button
                variant="ghost"
                size="icon"
                onClick={handleStartEditing}
                className="h-8 w-8"
              >
                <PencilIcon className="h-4 w-4" />
                <span className="sr-only">Renomear</span>
              </Button>
            )}
          </div>
        )}
      </div>

      <div className="flex items-center gap-2">
        {onShare && (
          <Button
            variant="ghost"
            size="icon"
            onClick={onShare}
            className="h-8 w-8"
          >
            <ShareIcon className="h-4 w-4" />
            <span className="sr-only">Compartilhar</span>
          </Button>
        )}

        {onExport && (
          <Button
            variant="ghost"
            size="icon"
            onClick={onExport}
            className="h-8 w-8"
          >
            <DownloadIcon className="h-4 w-4" />
            <span className="sr-only">Exportar</span>
          </Button>
        )}

        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8"
            >
              <MoreHorizontalIcon className="h-4 w-4" />
              <span className="sr-only">Mais opções</span>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            {onSettings && (
              <DropdownMenuItem onClick={onSettings}>
                Configurações
              </DropdownMenuItem>
            )}
            <DropdownMenuItem onClick={() => console.log('Limpar conversa')}>
              Limpar conversa
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => console.log('Iniciar nova conversa')}>
              Nova conversa
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  );
}
