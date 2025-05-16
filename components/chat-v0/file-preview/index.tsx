import React from 'react';
import { Button } from '@/components/ui/button';
import { XIcon } from 'lucide-react';

interface FilePreviewProps {
  files: File[];
  onRemove: (index: number) => void;
}

export function FilePreview({
  files,
  onRemove
}: FilePreviewProps) {
  return (
    <div className="flex flex-wrap gap-2 p-2 bg-muted/20 rounded-md">
      {files.map((file, index) => {
        const isImage = file.type.startsWith('image/');
        
        return (
          <div 
            key={`${file.name}-${index}`}
            className="relative group"
          >
            {isImage ? (
              <div className="relative w-20 h-20 rounded-md overflow-hidden border">
                <img 
                  src={URL.createObjectURL(file)} 
                  alt={file.name}
                  className="w-full h-full object-cover"
                />
                <Button
                  variant="destructive"
                  size="icon"
                  className="h-5 w-5 absolute top-1 right-1 opacity-0 group-hover:opacity-100 transition-opacity"
                  onClick={() => onRemove(index)}
                >
                  <XIcon className="h-3 w-3" />
                  <span className="sr-only">Remover {file.name}</span>
                </Button>
              </div>
            ) : (
              <div className="flex items-center gap-1 bg-muted px-2 py-1 rounded-md text-sm">
                <span className="truncate max-w-[150px]">{file.name}</span>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-5 w-5"
                  onClick={() => onRemove(index)}
                >
                  <XIcon className="h-3 w-3" />
                  <span className="sr-only">Remover {file.name}</span>
                </Button>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
