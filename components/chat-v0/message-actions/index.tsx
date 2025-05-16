import React from 'react';
import { Button } from '@/components/ui/button';
import { CopyIcon, RefreshIcon } from 'lucide-react';

interface MessageActionsProps {
  onCopy?: () => void;
  onRegenerate?: () => void;
}

export function MessageActions({
  onCopy,
  onRegenerate
}: MessageActionsProps) {
  return (
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
    </div>
  );
}
