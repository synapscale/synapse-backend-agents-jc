import React from 'react';
import { Card } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { SearchIcon, PlusIcon, FilterIcon } from 'lucide-react';
import { NodeTemplateCard } from './node-template-card';

interface MarketplaceBrowserProps {
  onSelectItem: (itemId: string) => void;
  onInstallItem: (itemId: string) => void;
}

export function MarketplaceBrowser({ onSelectItem, onInstallItem }: MarketplaceBrowserProps) {
  const [searchQuery, setSearchQuery] = React.useState('');
  const [activeTab, setActiveTab] = React.useState('popular');
  const [activeCategory, setActiveCategory] = React.useState('all');
  
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    // Implementar lógica de busca
  };
  
  const categories = [
    { id: 'all', name: 'Todas Categorias' },
    { id: 'entrada', name: 'Entrada de Dados' },
    { id: 'transformacao', name: 'Transformação de Dados' },
    { id: 'fluxo', name: 'Fluxo de Controle' },
    { id: 'saida', name: 'Saída de Dados' },
    { id: 'ia', name: 'Inteligência Artificial' }
  ];
  
  // Dados de exemplo para itens do marketplace
  const marketplaceItems = [
    {
      id: 'item1',
      name: 'Extrator de Texto PDF Pro',
      description: 'Versão avançada do extrator de texto PDF com suporte a OCR para imagens e documentos escaneados.',
      category: 'entrada',
      author: 'SynapScale',
      downloads: 2345,
      rating: 4.8,
      tags: ['PDF', 'Extração', 'OCR', 'Premium'],
      isInstalled: false
    },
    {
      id: 'item2',
      name: 'Análise de Sentimento Multilíngue',
      description: 'Analisa o sentimento de textos em mais de 20 idiomas usando modelos de IA avançados.',
      category: 'ia',
      author: 'AI Community',
      downloads: 1876,
      rating: 4.7,
      tags: ['NLP', 'Sentimento', 'Multilíngue'],
      isInstalled: false
    },
    {
      id: 'item3',
      name: 'Transformador de Dados Universal',
      description: 'Converte entre múltiplos formatos de dados: JSON, XML, CSV, YAML e mais.',
      category: 'transformacao',
      author: 'DataFlow',
      downloads: 3421,
      rating: 4.9,
      tags: ['Transformação', 'Dados', 'Conversão'],
      isInstalled: false
    },
    {
      id: 'item4',
      name: 'Conector de API GraphQL',
      description: 'Conecta-se a APIs GraphQL com suporte a autenticação e gerenciamento de cache.',
      category: 'entrada',
      author: 'API Tools',
      downloads: 1245,
      rating: 4.6,
      tags: ['API', 'GraphQL', 'Integração'],
      isInstalled: false
    },
    {
      id: 'item5',
      name: 'Dashboard Dinâmico',
      description: 'Cria dashboards interativos a partir de dados estruturados com múltiplos tipos de visualização.',
      category: 'saida',
      author: 'ReportMaster',
      downloads: 2187,
      rating: 4.5,
      tags: ['Dashboard', 'Visualização', 'Interativo'],
      isInstalled: false
    },
    {
      id: 'item6',
      name: 'Orquestrador de Fluxo',
      description: 'Gerencia fluxos complexos com paralelismo, condições e tratamento de erros avançado.',
      category: 'fluxo',
      author: 'LogicFlow',
      downloads: 1876,
      rating: 4.7,
      tags: ['Fluxo', 'Orquestração', 'Paralelismo'],
      isInstalled: false
    }
  ];
  
  const filteredItems = marketplaceItems.filter(item => 
    (activeCategory === 'all' || item.category === activeCategory)
  );
  
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Marketplace</h2>
        
        <Button onClick={() => window.location.href = '/marketplace/publish'}>
          <PlusIcon className="h-4 w-4 mr-2" />
          Publicar Node
        </Button>
      </div>
      
      <div className="flex items-center space-x-4">
        <div className="relative flex-1">
          <SearchIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
          <Input
            placeholder="Buscar no marketplace..."
            className="pl-9"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
        
        <Button variant="outline" size="icon">
          <FilterIcon className="h-5 w-5" />
        </Button>
      </div>
      
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid grid-cols-4 w-full">
          <TabsTrigger value="popular">Populares</TabsTrigger>
          <TabsTrigger value="recent">Recentes</TabsTrigger>
          <TabsTrigger value="trending">Em Alta</TabsTrigger>
          <TabsTrigger value="my">Meus Itens</TabsTrigger>
        </TabsList>
      </Tabs>
      
      <div className="flex gap-6">
        <div className="w-64 shrink-0">
          <h3 className="font-medium mb-3">Categorias</h3>
          
          <div className="space-y-1">
            {categories.map((category) => (
              <Button
                key={category.id}
                variant={activeCategory === category.id ? "secondary" : "ghost"}
                className="w-full justify-start"
                onClick={() => setActiveCategory(category.id)}
              >
                {category.name}
              </Button>
            ))}
          </div>
        </div>
        
        <div className="flex-1">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {filteredItems.map((item) => (
              <NodeTemplateCard
                key={item.id}
                template={item}
                onInstall={onInstallItem}
                onView={onSelectItem}
              />
            ))}
          </div>
          
          {filteredItems.length === 0 && (
            <Card className="p-8 text-center text-muted-foreground">
              Nenhum item encontrado para os filtros selecionados.
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
