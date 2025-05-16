import React from 'react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ChevronDownIcon, CheckIcon, PlusIcon, XIcon } from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';

interface Tool {
  id: string;
  name: string;
  description: string;
}

interface ToolSelectorProps {
  selectedTools: string[];
  onSelectTools: (toolIds: string[]) => void;
  tools: Tool[];
}

export function ToolSelector({
  selectedTools,
  onSelectTools,
  tools
}: ToolSelectorProps) {
  // Função para alternar a seleção de uma ferramenta
  const toggleTool = (toolId: string) => {
    if (selectedTools.includes(toolId)) {
      onSelectTools(selectedTools.filter(id => id !== toolId));
    } else {
      onSelectTools([...selectedTools, toolId]);
    }
  };

  // Função para remover uma ferramenta selecionada
  const removeTool = (toolId: string) => {
    onSelectTools(selectedTools.filter(id => id !== toolId));
  };

  return (
    <div className="flex flex-wrap gap-2 items-center">
      {/* Badges para ferramentas selecionadas */}
      {selectedTools.length > 0 && (
        <div className="flex flex-wrap gap-1">
          {selectedTools.map(toolId => {
            const tool = tools.find(t => t.id === toolId);
            if (!tool) return null;
            
            return (
              <Badge key={tool.id} variant="secondary" className="flex items-center gap-1">
                {tool.name}
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-4 w-4 p-0"
                  onClick={() => removeTool(tool.id)}
                >
                  <XIcon className="h-3 w-3" />
                  <span className="sr-only">Remover {tool.name}</span>
                </Button>
              </Badge>
            );
          })}
        </div>
      )}
      
      {/* Dropdown para selecionar ferramentas */}
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="outline" size="sm" className="flex items-center gap-1">
            <PlusIcon className="h-4 w-4" />
            <span>Ferramentas</span>
            <ChevronDownIcon className="h-4 w-4" />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="start" className="w-[220px]">
          {tools.map(tool => (
            <DropdownMenuItem
              key={tool.id}
              onClick={() => toggleTool(tool.id)}
              className="flex items-center justify-between"
            >
              <div className="flex flex-col">
                <span>{tool.name}</span>
                <span className="text-xs text-muted-foreground">{tool.description}</span>
              </div>
              {selectedTools.includes(tool.id) && (
                <CheckIcon className="h-4 w-4" />
              )}
            </DropdownMenuItem>
          ))}
        </DropdownMenuContent>
      </DropdownMenu>
    </div>
  );
}
