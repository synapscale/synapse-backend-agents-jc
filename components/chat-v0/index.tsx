import React from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Avatar } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ScrollArea } from '@/components/ui/scroll-area';
import { 
  PaperclipIcon, 
  SendIcon, 
  MoreHorizontalIcon, 
  PlusIcon,
  ChevronDownIcon,
  SearchIcon,
  RefreshIcon,
  ThumbsUpIcon,
  ThumbsDownIcon,
  CopyIcon,
  ShareIcon,
  DownloadIcon,
  PencilIcon,
  XIcon
} from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import { ptBR } from 'date-fns/locale';

// Componentes internos
import { ChatInput } from './chat-input';
import { ChatMessage } from './chat-message';
import { ChatHeader } from './header/chat-header';
import { ModelSelector } from './model-selector';
import { PersonalitySelector } from './personality-selector';
import { ToolSelector } from './tool-selector';

// Tipos
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

interface ChatInterfaceProps {
  initialMessages?: Message[];
  onSendMessage?: (message: string, attachments: File[]) => Promise<void>;
  isLoading?: boolean;
  showSidebar?: boolean;
  onToggleSidebar?: () => void;
}

export function ChatInterface({
  initialMessages = [],
  onSendMessage,
  isLoading = false,
  showSidebar = true,
  onToggleSidebar
}: ChatInterfaceProps) {
  const [messages, setMessages] = React.useState<Message[]>(initialMessages);
  const [selectedModel, setSelectedModel] = React.useState('gpt-4o');
  const [selectedPersonality, setSelectedPersonality] = React.useState('default');
  const [selectedTools, setSelectedTools] = React.useState<string[]>([]);
  const messagesEndRef = React.useRef<HTMLDivElement>(null);

  // Scroll para a última mensagem quando novas mensagens são adicionadas
  React.useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Função para lidar com o envio de mensagens
  const handleSendMessage = async (content: string, attachments: File[]) => {
    if (!content.trim() && attachments.length === 0) return;

    // Adicionar mensagem do usuário
    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: 'user',
      content,
      timestamp: new Date(),
      attachments: attachments.map(file => ({
        id: `attachment-${Date.now()}-${file.name}`,
        name: file.name,
        type: file.type,
        url: URL.createObjectURL(file)
      }))
    };

    setMessages(prev => [...prev, userMessage]);

    // Chamar callback de envio se fornecido
    if (onSendMessage) {
      await onSendMessage(content, attachments);
    }

    // Simular resposta do assistente (em um cenário real, isso viria do backend)
    setTimeout(() => {
      const assistantMessage: Message = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: 'Esta é uma resposta simulada do assistente. Em um cenário real, esta resposta viria do backend após processamento.',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, assistantMessage]);
    }, 1000);
  };

  return (
    <div className="flex flex-col h-full bg-background">
      <ChatHeader 
        title="Nova Conversa" 
        onRename={(newTitle) => console.log('Renomear para:', newTitle)}
        onShare={() => console.log('Compartilhar conversa')}
        onExport={() => console.log('Exportar conversa')}
      />
      
      <div className="flex flex-1 overflow-hidden">
        {/* Área principal de chat */}
        <div className="flex flex-col flex-1 overflow-hidden">
          {/* Área de mensagens */}
          <ScrollArea className="flex-1 p-4">
            <div className="space-y-4">
              {messages.map((message) => (
                <ChatMessage
                  key={message.id}
                  message={message}
                  onCopy={() => console.log('Copiar mensagem:', message.id)}
                  onRegenerate={message.role === 'assistant' ? () => console.log('Regenerar resposta') : undefined}
                  onFeedback={(isPositive) => console.log(`Feedback ${isPositive ? 'positivo' : 'negativo'}`)}
                />
              ))}
              <div ref={messagesEndRef} />
            </div>
          </ScrollArea>
          
          {/* Área de configurações e entrada */}
          <div className="border-t p-4 space-y-4">
            <div className="flex flex-wrap gap-2">
              <ModelSelector 
                selectedModel={selectedModel}
                onSelectModel={setSelectedModel}
                models={[
                  { id: 'gpt-4o', name: 'GPT-4o', description: 'Modelo mais avançado com capacidades multimodais' },
                  { id: 'gpt-4', name: 'GPT-4', description: 'Modelo avançado para tarefas complexas' },
                  { id: 'gpt-3.5-turbo', name: 'GPT-3.5 Turbo', description: 'Modelo rápido para tarefas gerais' },
                  { id: 'claude-3', name: 'Claude 3', description: 'Modelo da Anthropic com forte raciocínio' }
                ]}
              />
              
              <PersonalitySelector
                selectedPersonality={selectedPersonality}
                onSelectPersonality={setSelectedPersonality}
                personalities={[
                  { id: 'default', name: 'Padrão', description: 'Assistente equilibrado e neutro' },
                  { id: 'creative', name: 'Criativo', description: 'Foco em respostas criativas e inspiradoras' },
                  { id: 'precise', name: 'Preciso', description: 'Foco em precisão e detalhes técnicos' },
                  { id: 'friendly', name: 'Amigável', description: 'Tom conversacional e acessível' }
                ]}
              />
              
              <ToolSelector
                selectedTools={selectedTools}
                onSelectTools={setSelectedTools}
                tools={[
                  { id: 'web-search', name: 'Busca Web', description: 'Pesquisar informações na internet' },
                  { id: 'code-interpreter', name: 'Interpretador de Código', description: 'Executar código e análise de dados' },
                  { id: 'image-generation', name: 'Geração de Imagens', description: 'Criar imagens a partir de descrições' },
                  { id: 'file-analysis', name: 'Análise de Arquivos', description: 'Analisar conteúdo de arquivos' }
                ]}
              />
            </div>
            
            <ChatInput 
              onSendMessage={handleSendMessage}
              isLoading={isLoading}
              placeholder="Envie uma mensagem ou arquivos..."
            />
          </div>
        </div>
      </div>
    </div>
  );
}
