import React from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { PlusIcon, XIcon } from 'lucide-react';

interface AgentFormProps {
  initialData?: {
    id?: string;
    name: string;
    description: string;
    type: string;
    model: string;
    prompt: string;
    parameters: {
      temperature: number;
      top_p: number;
      max_tokens: number;
    };
    tags: string[];
    connections: Array<{
      id: string;
      name: string;
      type: string;
    }>;
  };
  onSave: (data: any) => void;
  onCancel: () => void;
  isLoading?: boolean;
}

export function AgentForm({
  initialData = {
    name: '',
    description: '',
    type: 'assistant',
    model: 'gpt-4o',
    prompt: '',
    parameters: {
      temperature: 0.7,
      top_p: 1,
      max_tokens: 1000
    },
    tags: [],
    connections: []
  },
  onSave,
  onCancel,
  isLoading = false
}: AgentFormProps) {
  const [data, setData] = React.useState(initialData);
  const [activeTab, setActiveTab] = React.useState('basic');
  const [newTag, setNewTag] = React.useState('');
  const [hasChanges, setHasChanges] = React.useState(false);

  // Detectar mudanças
  React.useEffect(() => {
    setHasChanges(JSON.stringify(data) !== JSON.stringify(initialData));
  }, [data, initialData]);

  // Atualizar campo simples
  const updateField = (field: string, value: any) => {
    setData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  // Atualizar parâmetro
  const updateParameter = (param: string, value: any) => {
    setData(prev => ({
      ...prev,
      parameters: {
        ...prev.parameters,
        [param]: value
      }
    }));
  };

  // Adicionar tag
  const addTag = () => {
    if (newTag.trim() && !data.tags.includes(newTag.trim())) {
      setData(prev => ({
        ...prev,
        tags: [...prev.tags, newTag.trim()]
      }));
      setNewTag('');
    }
  };

  // Remover tag
  const removeTag = (tag: string) => {
    setData(prev => ({
      ...prev,
      tags: prev.tags.filter(t => t !== tag)
    }));
  };

  // Lidar com tecla Enter no campo de tag
  const handleTagKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      addTag();
    }
  };

  // Salvar formulário
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSave(data);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid grid-cols-4 w-full">
          <TabsTrigger value="basic">Informações Básicas</TabsTrigger>
          <TabsTrigger value="prompt">Prompt</TabsTrigger>
          <TabsTrigger value="parameters">Parâmetros</TabsTrigger>
          <TabsTrigger value="connections">Conexões</TabsTrigger>
        </TabsList>
        
        <TabsContent value="basic" className="space-y-4 pt-4">
          <div className="space-y-2">
            <label htmlFor="name" className="text-sm font-medium">Nome</label>
            <Input
              id="name"
              value={data.name}
              onChange={(e) => updateField('name', e.target.value)}
              placeholder="Nome do agente"
              required
            />
          </div>
          
          <div className="space-y-2">
            <label htmlFor="description" className="text-sm font-medium">Descrição</label>
            <Textarea
              id="description"
              value={data.description}
              onChange={(e) => updateField('description', e.target.value)}
              placeholder="Descreva o propósito deste agente"
              rows={3}
            />
          </div>
          
          <div className="space-y-2">
            <label htmlFor="type" className="text-sm font-medium">Tipo</label>
            <select
              id="type"
              value={data.type}
              onChange={(e) => updateField('type', e.target.value)}
              className="w-full rounded-md border border-input bg-background px-3 py-2"
            >
              <option value="assistant">Assistente</option>
              <option value="function">Função</option>
              <option value="tool">Ferramenta</option>
              <option value="system">Sistema</option>
            </select>
          </div>
          
          <div className="space-y-2">
            <label htmlFor="model" className="text-sm font-medium">Modelo</label>
            <select
              id="model"
              value={data.model}
              onChange={(e) => updateField('model', e.target.value)}
              className="w-full rounded-md border border-input bg-background px-3 py-2"
            >
              <option value="gpt-4o">GPT-4o</option>
              <option value="gpt-4">GPT-4</option>
              <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
              <option value="claude-3">Claude 3</option>
            </select>
          </div>
          
          <div className="space-y-2">
            <label className="text-sm font-medium">Tags</label>
            <div className="flex flex-wrap gap-2 mb-2">
              {data.tags.map(tag => (
                <Badge key={tag} variant="secondary" className="flex items-center gap-1">
                  {tag}
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-4 w-4 p-0"
                    onClick={() => removeTag(tag)}
                    type="button"
                  >
                    <XIcon className="h-3 w-3" />
                    <span className="sr-only">Remover {tag}</span>
                  </Button>
                </Badge>
              ))}
            </div>
            <div className="flex gap-2">
              <Input
                value={newTag}
                onChange={(e) => setNewTag(e.target.value)}
                onKeyDown={handleTagKeyDown}
                placeholder="Adicionar tag"
              />
              <Button 
                type="button" 
                variant="outline" 
                onClick={addTag}
                disabled={!newTag.trim()}
              >
                <PlusIcon className="h-4 w-4" />
                <span className="sr-only">Adicionar tag</span>
              </Button>
            </div>
          </div>
        </TabsContent>
        
        <TabsContent value="prompt" className="space-y-4 pt-4">
          <div className="space-y-2">
            <label htmlFor="prompt" className="text-sm font-medium">Prompt</label>
            <Textarea
              id="prompt"
              value={data.prompt}
              onChange={(e) => updateField('prompt', e.target.value)}
              placeholder="Insira o prompt para o agente"
              rows={15}
              className="font-mono"
            />
          </div>
          
          <div className="bg-muted/30 p-4 rounded-md">
            <h3 className="text-sm font-medium mb-2">Variáveis disponíveis</h3>
            <div className="grid grid-cols-2 gap-2 text-sm">
              <div><code>{'{{input}}'}</code> - Entrada do usuário</div>
              <div><code>{'{{context}}'}</code> - Contexto da conversa</div>
              <div><code>{'{{date}}'}</code> - Data atual</div>
              <div><code>{'{{time}}'}</code> - Hora atual</div>
            </div>
          </div>
        </TabsContent>
        
        <TabsContent value="parameters" className="space-y-4 pt-4">
          <div className="space-y-4">
            <div>
              <div className="flex justify-between mb-2">
                <label htmlFor="temperature" className="text-sm font-medium">
                  Temperatura: {data.parameters.temperature}
                </label>
                <span className="text-xs text-muted-foreground">
                  Criatividade vs. Precisão
                </span>
              </div>
              <input
                id="temperature"
                type="range"
                min="0"
                max="2"
                step="0.1"
                value={data.parameters.temperature}
                onChange={(e) => updateParameter('temperature', parseFloat(e.target.value))}
                className="w-full"
              />
              <div className="flex justify-between text-xs text-muted-foreground">
                <span>Preciso</span>
                <span>Criativo</span>
              </div>
            </div>
            
            <div>
              <div className="flex justify-between mb-2">
                <label htmlFor="top_p" className="text-sm font-medium">
                  Top P: {data.parameters.top_p}
                </label>
                <span className="text-xs text-muted-foreground">
                  Diversidade de respostas
                </span>
              </div>
              <input
                id="top_p"
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={data.parameters.top_p}
                onChange={(e) => updateParameter('top_p', parseFloat(e.target.value))}
                className="w-full"
              />
            </div>
            
            <div>
              <div className="flex justify-between mb-2">
                <label htmlFor="max_tokens" className="text-sm font-medium">
                  Máximo de tokens: {data.parameters.max_tokens}
                </label>
                <span className="text-xs text-muted-foreground">
                  Tamanho máximo da resposta
                </span>
              </div>
              <input
                id="max_tokens"
                type="range"
                min="100"
                max="4000"
                step="100"
                value={data.parameters.max_tokens}
                onChange={(e) => updateParameter('max_tokens', parseInt(e.target.value))}
                className="w-full"
              />
            </div>
          </div>
          
          <Card className="p-4 bg-muted/30">
            <h3 className="text-sm font-medium mb-2">Presets</h3>
            <div className="flex flex-wrap gap-2">
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={() => {
                  updateParameter('temperature', 0.3);
                  updateParameter('top_p', 0.9);
                  updateParameter('max_tokens', 1000);
                }}
              >
                Preciso
              </Button>
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={() => {
                  updateParameter('temperature', 0.7);
                  updateParameter('top_p', 1);
                  updateParameter('max_tokens', 1500);
                }}
              >
                Balanceado
              </Button>
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={() => {
                  updateParameter('temperature', 1.2);
                  updateParameter('top_p', 0.9);
                  updateParameter('max_tokens', 2000);
                }}
              >
                Criativo
              </Button>
            </div>
          </Card>
        </TabsContent>
        
        <TabsContent value="connections" className="space-y-4 pt-4">
          <div className="bg-muted/30 p-4 rounded-md mb-4">
            <p className="text-sm">
              Conecte este agente a outros agentes para criar fluxos de trabalho complexos.
              As conexões permitem que os agentes compartilhem informações e trabalhem juntos.
            </p>
          </div>
          
          {data.connections.length > 0 ? (
            <div className="space-y-2">
              {data.connections.map(connection => (
                <Card key={connection.id} className="p-3 flex justify-between items-center">
                  <div>
                    <div className="font-medium">{connection.name}</div>
                    <div className="text-xs text-muted-foreground">{connection.type}</div>
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => {
                      setData(prev => ({
                        ...prev,
                        connections: prev.connections.filter(c => c.id !== connection.id)
                      }));
                    }}
                  >
                    <XIcon className="h-4 w-4" />
                    <span className="sr-only">Remover conexão</span>
                  </Button>
                </Card>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-muted-foreground">
              Nenhuma conexão configurada
            </div>
          )}
          
          <Button
            type="button"
            variant="outline"
            className="w-full"
            onClick={() => {
              // Em um cenário real, abriria um modal para selecionar agentes
              const mockConnection = {
                id: `connection-${Date.now()}`,
                name: `Agente ${Math.floor(Math.random() * 100)}`,
                type: ['Assistente', 'Função', 'Ferramenta'][Math.floor(Math.random() * 3)]
              };
              
              setData(prev => ({
                ...prev,
                connections: [...prev.connections, mockConnection]
              }));
            }}
          >
            <PlusIcon className="h-4 w-4 mr-2" />
            Adicionar Conexão
          </Button>
        </TabsContent>
      </Tabs>
      
      <div className="flex justify-end gap-2 pt-4 border-t">
        <Button
          type="button"
          variant="outline"
          onClick={onCancel}
        >
          Cancelar
        </Button>
        <Button
          type="submit"
          disabled={isLoading || !data.name || !hasChanges}
        >
          {isLoading ? 'Salvando...' : 'Salvar Agente'}
        </Button>
      </div>
    </form>
  );
}
