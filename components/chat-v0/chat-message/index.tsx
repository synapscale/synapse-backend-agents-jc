import React from 'react';
import { Card } from '@/components/ui/card';
import { Avatar } from '@/components/ui/avatar';
import { Button } from '@/components/ui/button';
import { formatDistanceToNow } from 'date-fns';
import { ptBR } from 'date-fns/locale';
import { CopyIcon, RefreshIcon, ThumbsUpIcon, ThumbsDownIcon } from 'lucide-react';

interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  attachments?: Array<{
    id: string;
    name: string;
    type: string;
    url: string;
  }>;
}

interface ChatMessageProps {
  message: Message;
  onCopy?: () => void;
  onRegenerate?: () => void;
  onFeedback?: (isPositive: boolean) => void;
}

export function ChatMessage({
  message,
  onCopy,
  onRegenerate,
  onFeedback
}: ChatMessageProps) {
  const isUser = message.role === 'user';
  
  // Função para renderizar o conteúdo com formatação básica
  const renderContent = (content: string) => {
    // Implementação simples - em um cenário real, usaríamos um parser de markdown
    return content.split('\n').map((line, i) => (
      <React.Fragment key={i}>
        {line}
        {i < content.split('\n').length - 1 && <br />}
      </React.Fragment>
    ));
  };
  
  // Função para renderizar anexos
  const renderAttachments = () => {
    if (!message.attachments || message.attachments.length === 0) return null;
    
    return (
      <div className="mt-2 space-y-2">
        {message.attachments.map(attachment => {
          const isImage = attachment.type.startsWith('image/');
          
          return (
            <div key={attachment.id} className="rounded-md overflow-hidden border">
              {isImage ? (
                <img 
                  src={attachment.url} 
                  alt={attachment.name}
                  className="max-h-60 object-contain"
                />
              ) : (
                <div className="p-2 bg-muted/20 text-sm flex items-center gap-2">
                  <span className="truncate">{attachment.name}</span>
                  <Button variant="ghost" size="sm" asChild>
                    <a href={attachment.url} download={attachment.name}>
                      Download
                    </a>
                  </Button>
                </div>
              )}
            </div>
          );
        })}
      </div>
    );
  };

  return (
    <div className={`flex gap-4 ${isUser ? 'justify-end' : 'justify-start'}`}>
      {!isUser && (
        <Avatar className="h-8 w-8 shrink-0">
          <div className="bg-primary text-primary-foreground h-full w-full flex items-center justify-center text-sm font-medium">
            AI
          </div>
        </Avatar>
      )}
      
      <div className={`flex flex-col ${isUser ? 'items-end' : 'items-start'} max-w-[80%]`}>
        <Card className={`p-3 ${isUser ? 'bg-primary text-primary-foreground' : 'bg-muted/30'}`}>
          <div className="text-sm">
            {renderContent(message.content)}
            {renderAttachments()}
          </div>
        </Card>
        
        <div className="flex items-center gap-2 mt-1 text-xs text-muted-foreground">
          <span>
            {formatDistanceToNow(new Date(message.timestamp), { 
              addSuffix: true,
              locale: ptBR
            })}
          </span>
          
          {!isUser && (
            <div className="flex items-center gap-1">
              {onCopy && (
                <Button 
                  variant="ghost" 
                  size="icon" 
                  className="h-6 w-6" 
                  onClick={onCopy}
                >
                  <CopyIcon className="h-3 w-3" />
                  <span className="sr-only">Copiar</span>
                </Button>
              )}
              
              {onRegenerate && (
                <Button 
                  variant="ghost" 
                  size="icon" 
                  className="h-6 w-6" 
                  onClick={onRegenerate}
                >
                  <RefreshIcon className="h-3 w-3" />
                  <span className="sr-only">Regenerar</span>
                </Button>
              )}
              
              {onFeedback && (
                <>
                  <Button 
                    variant="ghost" 
                    size="icon" 
                    className="h-6 w-6" 
                    onClick={() => onFeedback(true)}
                  >
                    <ThumbsUpIcon className="h-3 w-3" />
                    <span className="sr-only">Feedback positivo</span>
                  </Button>
                  
                  <Button 
                    variant="ghost" 
                    size="icon" 
                    className="h-6 w-6" 
                    onClick={() => onFeedback(false)}
                  >
                    <ThumbsDownIcon className="h-3 w-3" />
                    <span className="sr-only">Feedback negativo</span>
                  </Button>
                </>
              )}
            </div>
          )}
        </div>
      </div>
      
      {isUser && (
        <Avatar className="h-8 w-8 shrink-0">
          <div className="bg-secondary text-secondary-foreground h-full w-full flex items-center justify-center text-sm font-medium">
            EU
          </div>
        </Avatar>
      )}
    </div>
  );
}
