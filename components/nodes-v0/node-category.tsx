import React from 'react';
import { Card } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { SearchIcon, PlusIcon, FilterIcon } from 'lucide-react';
import { NodeTemplateCard } from './node-template-card';

interface NodeCategoryProps {
  onSelectTemplate: (templateId: string) => void;
  onInstallTemplate: (templateId: string) => void;
}

export function NodeCategory({ onSelectTemplate, onInstallTemplate }: NodeCategoryProps) {
  const [searchQuery, setSearchQuery] = React.useState('');
  const [activeTab, setActiveTab] = React.useState('all');
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
  
  // Dados de exemplo para templates
  const templates = [
    {
      id: 'template1',
      name: 'Extrator de Texto PDF',
      description: 'Extrai texto de arquivos PDF com suporte a OCR para imagens.',
      category: 'entrada',
      author: 'SynapScale',
      downloads: 1245,
      rating: 4.7,
      tags: ['PDF', 'Extração', 'OCR'],
      isInstalled: true
    },
    {
      id: 'template2',
      name: 'Classificador de Sentimento',
      description: 'Analisa o sentimento de textos usando modelos de IA pré-treinados.',
      category: 'ia',
      author: 'AI Community',
      downloads: 987,
      rating: 4.5,
      tags: ['NLP', 'Sentimento', 'Análise'],
      isInstalled: false
    },
    {
      id: 'template3',
      name: 'Transformador de JSON',
      description: 'Converte e transforma estruturas JSON com suporte a JSONPath.',
      category: 'transformacao',
      author: 'DataFlow',
      downloads: 756,
      rating: 4.2,
      tags: ['JSON', 'Transformação', 'Dados'],
      isInstalled: false
    },
    {
      id: 'template4',
      name: 'Conector de API REST',
      description: 'Conecta-se a APIs REST com suporte a autenticação OAuth e JWT.',
      category: 'entrada',
      author: 'API Tools',
      downloads: 1532,
      rating: 4.8,
      tags: ['API', 'REST', 'Integração'],
      isInstalled: true
    },
    {
      id: 'template5',
      name: 'Gerador de Relatórios',
      description: 'Cria relatórios em PDF, Excel ou HTML a partir de dados estruturados.',
      category: 'saida',
      author: 'ReportMaster',
      downloads: 876,
      rating: 4.4,
      tags: ['Relatórios', 'PDF', 'Excel'],
      isInstalled: false
    },
    {
      id: 'template6',
      name: 'Processador de Condições',
      description: 'Avalia condições complexas com suporte a expressões lógicas avançadas.',
      category: 'fluxo',
      author: 'LogicFlow',
      downloads: 654,
      rating: 4.3,
      tags: ['Condições', 'Lógica', 'Fluxo'],
      isInstalled: false
    }
  ];
  
  const filteredTemplates = templates.filter(template => 
    (activeCategory === 'all' || template.category === activeCategory) &&
    (activeTab === 'all' || 
     (activeTab === 'installed' && template.isInstalled) ||
     (activeTab === 'community' && !template.isInstalled))
  );
  
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Biblioteca de Nodes</h2>
        
        <Button onClick={() => {}}>
          <PlusIcon className="h-4 w-4 mr-2" />
          Criar Node
        </Button>
      </div>
      
      <div className="flex items-center space-x-4">
        <div className="relative flex-1">
          <SearchIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
          <Input
            placeholder="Buscar nodes..."
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
        <TabsList className="grid grid-cols-3 w-full">
          <TabsTrigger value="all">Todos</TabsTrigger>
          <TabsTrigger value="installed">Instalados</TabsTrigger>
          <TabsTrigger value="community">Comunidade</TabsTrigger>
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
            {filteredTemplates.map((template) => (
              <NodeTemplateCard
                key={template.id}
                template={template}
                onInstall={onInstallTemplate}
                onView={onSelectTemplate}
              />
            ))}
          </div>
          
          {filteredTemplates.length === 0 && (
            <Card className="p-8 text-center text-muted-foreground">
              Nenhum node encontrado para os filtros selecionados.
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
