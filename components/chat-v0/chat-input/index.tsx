import React from 'react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { PaperclipIcon, SendIcon, XIcon } from 'lucide-react';

interface ChatInputProps {
  onSendMessage: (content: string, attachments: File[]) => void;
  isLoading?: boolean;
  placeholder?: string;
}

export function ChatInput({
  onSendMessage,
  isLoading = false,
  placeholder = "Envie uma mensagem..."
}: ChatInputProps) {
  const [content, setContent] = React.useState('');
  const [attachments, setAttachments] = React.useState<File[]>([]);
  const [isPasting, setIsPasting] = React.useState(false);
  const fileInputRef = React.useRef<HTMLInputElement>(null);

  // Função para lidar com o envio da mensagem
  const handleSend = () => {
    if (!content.trim() && attachments.length === 0) return;
    
    onSendMessage(content, attachments);
    setContent('');
    setAttachments([]);
  };

  // Função para lidar com a tecla Enter
  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // Função para lidar com a seleção de arquivos
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const newFiles = Array.from(e.target.files);
      setAttachments(prev => [...prev, ...newFiles]);
      
      // Limpar o input para permitir selecionar o mesmo arquivo novamente
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  // Função para remover um arquivo
  const removeFile = (index: number) => {
    setAttachments(prev => prev.filter((_, i) => i !== index));
  };

  // Função para lidar com o paste de imagens
  const handlePaste = (e: React.ClipboardEvent) => {
    const items = e.clipboardData?.items;
    if (!items) return;

    for (let i = 0; i < items.length; i++) {
      if (items[i].type.indexOf('image') !== -1) {
        const file = items[i].getAsFile();
        if (file) {
          setAttachments(prev => [...prev, file]);
        }
      }
    }
  };

  return (
    <div className="space-y-2">
      {/* Área de preview de arquivos */}
      {attachments.length > 0 && (
        <div className="flex flex-wrap gap-2 p-2 bg-muted/20 rounded-md">
          {attachments.map((file, index) => (
            <div 
              key={`${file.name}-${index}`}
              className="flex items-center gap-1 bg-muted px-2 py-1 rounded-md text-sm"
            >
              <span className="truncate max-w-[150px]">{file.name}</span>
              <Button
                variant="ghost"
                size="icon"
                className="h-5 w-5"
                onClick={() => removeFile(index)}
              >
                <XIcon className="h-3 w-3" />
              </Button>
            </div>
          ))}
        </div>
      )}
      
      {/* Área de input */}
      <div className="flex items-center gap-2">
        <Button
          variant="ghost"
          size="icon"
          className="shrink-0"
          onClick={() => fileInputRef.current?.click()}
          type="button"
        >
          <PaperclipIcon className="h-5 w-5" />
          <span className="sr-only">Anexar arquivo</span>
        </Button>
        
        <Input
          value={content}
          onChange={(e) => setContent(e.target.value)}
          onKeyDown={handleKeyDown}
          onPaste={handlePaste}
          placeholder={placeholder}
          disabled={isLoading}
          className="flex-1"
        />
        
        <Button
          onClick={handleSend}
          disabled={isLoading || (!content.trim() && attachments.length === 0)}
          className="shrink-0"
        >
          <SendIcon className="h-5 w-5" />
          <span className="sr-only">Enviar</span>
        </Button>
        
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileChange}
          multiple
          className="hidden"
        />
      </div>
    </div>
  );
}
