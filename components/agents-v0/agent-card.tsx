import React from 'react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  MoreHorizontalIcon, 
  EditIcon, 
  TrashIcon, 
  PlayIcon,
  StarIcon
} from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';

interface AgentCardProps {
  agent: {
    id: string;
    name: string;
    description: string;
    type: string;
    model: string;
    tags: string[];
    isActive?: boolean;
    isFavorite?: boolean;
    lastUsed?: Date;
  };
  onEdit?: (id: string) => void;
  onDelete?: (id: string) => void;
  onView?: (id: string) => void;
  onToggleActive?: (id: string, active: boolean) => void;
  onToggleFavorite?: (id: string, favorite: boolean) => void;
}

export function AgentCard({
  agent,
  onEdit,
  onDelete,
  onView,
  onToggleActive,
  onToggleFavorite
}: AgentCardProps) {
  return (
    <Card className="p-4 hover:shadow-md transition-shadow">
      <div className="flex justify-between items-start">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="font-medium">{agent.name}</h3>
            {agent.isActive && (
              <Badge variant="success" className="text-xs">Ativo</Badge>
            )}
          </div>
          <p className="text-sm text-muted-foreground line-clamp-2 mt-1">
            {agent.description || "Sem descrição"}
          </p>
        </div>
        
        <div className="flex items-center gap-1">
          {onToggleFavorite && (
            <Button
              variant="ghost"
              size="icon"
              className={`h-8 w-8 ${agent.isFavorite ? 'text-yellow-500' : ''}`}
              onClick={() => onToggleFavorite(agent.id, !agent.isFavorite)}
            >
              <StarIcon className="h-4 w-4" />
              <span className="sr-only">
                {agent.isFavorite ? 'Remover dos favoritos' : 'Adicionar aos favoritos'}
              </span>
            </Button>
          )}
          
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="icon" className="h-8 w-8">
                <MoreHorizontalIcon className="h-4 w-4" />
                <span className="sr-only">Mais opções</span>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              {onView && (
                <DropdownMenuItem onClick={() => onView(agent.id)}>
                  <PlayIcon className="h-4 w-4 mr-2" />
                  Visualizar
                </DropdownMenuItem>
              )}
              {onEdit && (
                <DropdownMenuItem onClick={() => onEdit(agent.id)}>
                  <EditIcon className="h-4 w-4 mr-2" />
                  Editar
                </DropdownMenuItem>
              )}
              {onToggleActive && (
                <DropdownMenuItem 
                  onClick={() => onToggleActive(agent.id, !agent.isActive)}
                >
                  {agent.isActive ? 'Desativar' : 'Ativar'}
                </DropdownMenuItem>
              )}
              {onDelete && (
                <DropdownMenuItem 
                  onClick={() => onDelete(agent.id)}
                  className="text-destructive focus:text-destructive"
                >
                  <TrashIcon className="h-4 w-4 mr-2" />
                  Excluir
                </DropdownMenuItem>
              )}
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
      
      <div className="mt-3 flex flex-wrap gap-2">
        {agent.tags.map((tag, index) => (
          <Badge key={index} variant="outline" className="text-xs">
            {tag}
          </Badge>
        ))}
      </div>
      
      <div className="mt-4 flex items-center justify-between text-xs text-muted-foreground">
        <div>Modelo: {agent.model}</div>
        <div>Tipo: {agent.type}</div>
        {agent.lastUsed && (
          <div>
            Último uso: {new Date(agent.lastUsed).toLocaleDateString()}
          </div>
        )}
      </div>
    </Card>
  );
}
