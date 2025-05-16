import React from 'react';
import { Button } from '@/components/ui/button';
import { ChevronDownIcon, CheckIcon } from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';

interface Model {
  id: string;
  name: string;
  description: string;
}

interface ModelSelectorProps {
  selectedModel: string;
  onSelectModel: (modelId: string) => void;
  models: Model[];
}

export function ModelSelector({
  selectedModel,
  onSelectModel,
  models
}: ModelSelectorProps) {
  // Encontrar o modelo selecionado
  const selected = models.find(model => model.id === selectedModel) || models[0];

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" className="flex items-center gap-2">
          <span>Modelo: {selected.name}</span>
          <ChevronDownIcon className="h-4 w-4" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="start" className="w-[220px]">
        {models.map(model => (
          <DropdownMenuItem
            key={model.id}
            onClick={() => onSelectModel(model.id)}
            className="flex items-center justify-between"
          >
            <div className="flex flex-col">
              <span>{model.name}</span>
              <span className="text-xs text-muted-foreground">{model.description}</span>
            </div>
            {model.id === selectedModel && (
              <CheckIcon className="h-4 w-4" />
            )}
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
