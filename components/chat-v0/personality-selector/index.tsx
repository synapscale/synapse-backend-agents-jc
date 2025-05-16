import React from 'react';
import { Button } from '@/components/ui/button';
import { ChevronDownIcon, CheckIcon } from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';

interface Personality {
  id: string;
  name: string;
  description: string;
}

interface PersonalitySelectorProps {
  selectedPersonality: string;
  onSelectPersonality: (personalityId: string) => void;
  personalities: Personality[];
}

export function PersonalitySelector({
  selectedPersonality,
  onSelectPersonality,
  personalities
}: PersonalitySelectorProps) {
  // Encontrar a personalidade selecionada
  const selected = personalities.find(p => p.id === selectedPersonality) || personalities[0];

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" className="flex items-center gap-2">
          <span>Personalidade: {selected.name}</span>
          <ChevronDownIcon className="h-4 w-4" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="start" className="w-[220px]">
        {personalities.map(personality => (
          <DropdownMenuItem
            key={personality.id}
            onClick={() => onSelectPersonality(personality.id)}
            className="flex items-center justify-between"
          >
            <div className="flex flex-col">
              <span>{personality.name}</span>
              <span className="text-xs text-muted-foreground">{personality.description}</span>
            </div>
            {personality.id === selectedPersonality && (
              <CheckIcon className="h-4 w-4" />
            )}
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
