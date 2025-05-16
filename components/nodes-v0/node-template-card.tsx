import React from 'react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { StarIcon, DownloadIcon, InfoIcon } from 'lucide-react';

interface NodeTemplate {
  id: string;
  name: string;
  description: string;
  category: string;
  author: string;
  downloads: number;
  rating: number;
  tags: string[];
  isInstalled: boolean;
}

interface NodeTemplateCardProps {
  template: NodeTemplate;
  onInstall: (templateId: string) => void;
  onView: (templateId: string) => void;
}

export function NodeTemplateCard({
  template,
  onInstall,
  onView
}: NodeTemplateCardProps) {
  return (
    <Card className="p-4 hover:shadow-md transition-shadow">
      <div className="flex justify-between items-start">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="font-medium">{template.name}</h3>
            {template.isInstalled && (
              <Badge variant="outline" className="text-xs">Instalado</Badge>
            )}
          </div>
          <p className="text-sm text-muted-foreground line-clamp-2 mt-1">
            {template.description}
          </p>
        </div>
      </div>
      
      <div className="mt-3 flex flex-wrap gap-2">
        {template.tags.map((tag, index) => (
          <Badge key={index} variant="secondary" className="text-xs">
            {tag}
          </Badge>
        ))}
      </div>
      
      <div className="mt-4 flex items-center justify-between text-xs text-muted-foreground">
        <div>Autor: {template.author}</div>
        <div className="flex items-center gap-1">
          <StarIcon className="h-3 w-3 text-yellow-500" />
          {template.rating.toFixed(1)}
        </div>
        <div className="flex items-center gap-1">
          <DownloadIcon className="h-3 w-3" />
          {template.downloads.toLocaleString()}
        </div>
      </div>
      
      <div className="mt-4 flex justify-between gap-2">
        <Button
          variant="outline"
          size="sm"
          className="flex-1"
          onClick={() => onView(template.id)}
        >
          <InfoIcon className="h-4 w-4 mr-1" />
          Detalhes
        </Button>
        
        <Button
          variant={template.isInstalled ? "secondary" : "default"}
          size="sm"
          className="flex-1"
          onClick={() => onInstall(template.id)}
        >
          {template.isInstalled ? 'Atualizar' : 'Instalar'}
        </Button>
      </div>
    </Card>
  );
}
