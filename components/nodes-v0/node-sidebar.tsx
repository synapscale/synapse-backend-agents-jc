import React from 'react';
import { Card } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { SearchIcon, PlusIcon, FilterIcon } from 'lucide-react';

interface NodeSidebarProps {
  onSelectCategory: (category: string) => void;
  onSearch: (query: string) => void;
  onCreateNode: () => void;
  selectedCategory: string;
}

export function NodeSidebar({
  onSelectCategory,
  onSearch,
  onCreateNode,
  selectedCategory
}: NodeSidebarProps) {
  const [searchQuery, setSearchQuery] = React.useState('');
  
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    onSearch(searchQuery);
  };
  
  const categories = [
    { id: 'all', name: 'Todas Categorias' },
    { id: 'entrada', name: 'Entrada de Dados' },
    { id: 'transformacao', name: 'Transformação de Dados' },
    { id: 'fluxo', name: 'Fluxo de Controle' },
    { id: 'saida', name: 'Saída de Dados' },
    { id: 'ia', name: 'Inteligência Artificial' }
  ];

  return (
    <div className="w-64 border-r h-full flex flex-col">
      <div className="p-4 border-b">
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-medium">Nodes</h2>
          <Button size="sm" onClick={onCreateNode}>
            <PlusIcon className="h-4 w-4 mr-1" />
            Criar
          </Button>
        </div>
        
        <form onSubmit={handleSearch} className="relative">
          <SearchIcon className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Buscar nodes..."
            className="pl-9"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </form>
      </div>
      
      <Tabs defaultValue="categories" className="flex-1 flex flex-col">
        <TabsList className="grid grid-cols-2 mx-4 mt-4">
          <TabsTrigger value="categories">Categorias</TabsTrigger>
          <TabsTrigger value="recent">Recentes</TabsTrigger>
        </TabsList>
        
        <TabsContent value="categories" className="flex-1 overflow-auto p-2">
          <div className="space-y-1">
            {categories.map((category) => (
              <Button
                key={category.id}
                variant={selectedCategory === category.id ? "secondary" : "ghost"}
                className="w-full justify-start"
                onClick={() => onSelectCategory(category.id)}
              >
                {category.name}
              </Button>
            ))}
          </div>
        </TabsContent>
        
        <TabsContent value="recent" className="flex-1 overflow-auto p-2">
          <div className="space-y-1">
            <Button variant="ghost" className="w-full justify-start">
              Extrator de Texto PDF
            </Button>
            <Button variant="ghost" className="w-full justify-start">
              Classificador de Sentimento
            </Button>
            <Button variant="ghost" className="w-full justify-start">
              Conector de API REST
            </Button>
          </div>
        </TabsContent>
      </Tabs>
      
      <div className="p-4 border-t">
        <Button variant="outline" className="w-full" onClick={() => window.location.href = '/marketplace'}>
          Marketplace
        </Button>
      </div>
    </div>
  );
}
