import React from 'react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';
import { 
  PlusIcon, 
  XIcon, 
  SaveIcon, 
  PlayIcon,
  CodeIcon,
  SettingsIcon,
  InfoIcon
} from 'lucide-react';

interface NodeEditorProps {
  node?: {
    id: string;
    name: string;
    description: string;
    type: string;
    category: string;
    code: string;
    inputs: Array<{
      id: string;
      name: string;
      type: string;
      required: boolean;
    }>;
    outputs: Array<{
      id: string;
      name: string;
      type: string;
    }>;
    settings: Record<string, any>;
  };
  onSave: (nodeData: any) => void;
  onCancel: () => void;
  onTest: (nodeData: any) => void;
  isLoading?: boolean;
}

export function NodeEditor({
  node = {
    id: '',
    name: '',
    description: '',
    type: 'processor',
    category: 'transformacao',
    code: '',
    inputs: [
      { id: 'input1', name: 'Input 1', type: 'string', required: true }
    ],
    outputs: [
      { id: 'output1', name: 'Output 1', type: 'string' }
    ],
    settings: {}
  },
  onSave,
  onCancel,
  onTest,
  isLoading = false
}: NodeEditorProps) {
  const [data, setData] = React.useState(node);
  const [activeTab, setActiveTab] = React.useState('basic');
  const [newInputName, setNewInputName] = React.useState('');
  const [newOutputName, setNewOutputName] = React.useState('');
  
  // Atualizar campo simples
  const updateField = (field: string, value: any) => {
    setData(prev => ({
      ...prev,
      [field]: value
    }));
  };
  
  // Adicionar input
  const addInput = () => {
    if (newInputName.trim()) {
      const newInput = {
        id: `input-${Date.now()}`,
        name: newInputName.trim(),
        type: 'string',
        required: false
      };
      
      setData(prev => ({
        ...prev,
        inputs: [...prev.inputs, newInput]
      }));
      
      setNewInputName('');
    }
  };
  
  // Remover input
  const removeInput = (inputId: string) => {
    setData(prev => ({
      ...prev,
      inputs: prev.inputs.filter(input => input.id !== inputId)
    }));
  };
  
  // Adicionar output
  const addOutput = () => {
    if (newOutputName.trim()) {
      const newOutput = {
        id: `output-${Date.now()}`,
        name: newOutputName.trim(),
        type: 'string'
      };
      
      setData(prev => ({
        ...prev,
        outputs: [...prev.outputs, newOutput]
      }));
      
      setNewOutputName('');
    }
  };
  
  // Remover output
  const removeOutput = (outputId: string) => {
    setData(prev => ({
      ...prev,
      outputs: prev.outputs.filter(output => output.id !== outputId)
    }));
  };
  
  // Atualizar tipo de input
  const updateInputType = (inputId: string, type: string) => {
    setData(prev => ({
      ...prev,
      inputs: prev.inputs.map(input => 
        input.id === inputId ? { ...input, type } : input
      )
    }));
  };
  
  // Atualizar tipo de output
  const updateOutputType = (outputId: string, type: string) => {
    setData(prev => ({
      ...prev,
      outputs: prev.outputs.map(output => 
        output.id === outputId ? { ...output, type } : output
      )
    }));
  };
  
  // Alternar required para input
  const toggleInputRequired = (inputId: string) => {
    setData(prev => ({
      ...prev,
      inputs: prev.inputs.map(input => 
        input.id === inputId ? { ...input, required: !input.required } : input
      )
    }));
  };
  
  // Salvar formulário
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSave(data);
  };
  
  // Testar node
  const handleTest = () => {
    onTest(data);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid grid-cols-4 w-full">
          <TabsTrigger value="basic">Informações Básicas</TabsTrigger>
          <TabsTrigger value="io">Entradas/Saídas</TabsTrigger>
          <TabsTrigger value="code">Código</TabsTrigger>
          <TabsTrigger value="settings">Configurações</TabsTrigger>
        </TabsList>
        
        <TabsContent value="basic" className="space-y-4 pt-4">
          <div className="space-y-2">
            <label htmlFor="name" className="text-sm font-medium">Nome</label>
            <Input
              id="name"
              value={data.name}
              onChange={(e) => updateField('name', e.target.value)}
              placeholder="Nome do node"
              required
            />
          </div>
          
          <div className="space-y-2">
            <label htmlFor="description" className="text-sm font-medium">Descrição</label>
            <Textarea
              id="description"
              value={data.description}
              onChange={(e) => updateField('description', e.target.value)}
              placeholder="Descreva o propósito deste node"
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
              <option value="source">Fonte de Dados</option>
              <option value="processor">Processador</option>
              <option value="sink">Destino de Dados</option>
              <option value="control">Controle de Fluxo</option>
            </select>
          </div>
          
          <div className="space-y-2">
            <label htmlFor="category" className="text-sm font-medium">Categoria</label>
            <select
              id="category"
              value={data.category}
              onChange={(e) => updateField('category', e.target.value)}
              className="w-full rounded-md border border-input bg-background px-3 py-2"
            >
              <option value="entrada">Entrada de Dados</option>
              <option value="transformacao">Transformação de Dados</option>
              <option value="fluxo">Fluxo de Controle</option>
              <option value="saida">Saída de Dados</option>
              <option value="ia">Inteligência Artificial</option>
            </select>
          </div>
        </TabsContent>
        
        <TabsContent value="io" className="space-y-6 pt-4">
          <div className="space-y-4">
            <h3 className="font-medium">Entradas</h3>
            
            {data.inputs.map((input, index) => (
              <Card key={input.id} className="p-3 flex items-center justify-between">
                <div className="flex items-center gap-3 flex-1">
                  <div className="font-medium">{input.name}</div>
                  
                  <select
                    value={input.type}
                    onChange={(e) => updateInputType(input.id, e.target.value)}
                    className="rounded-md border border-input bg-background px-2 py-1 text-sm"
                  >
                    <option value="string">Texto</option>
                    <option value="number">Número</option>
                    <option value="boolean">Booleano</option>
                    <option value="object">Objeto</option>
                    <option value="array">Array</option>
                  </select>
                  
                  <Button
                    type="button"
                    variant={input.required ? "default" : "outline"}
                    size="sm"
                    onClick={() => toggleInputRequired(input.id)}
                  >
                    {input.required ? 'Obrigatório' : 'Opcional'}
                  </Button>
                </div>
                
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  onClick={() => removeInput(input.id)}
                >
                  <XIcon className="h-4 w-4" />
                  <span className="sr-only">Remover entrada</span>
                </Button>
              </Card>
            ))}
            
            <div className="flex gap-2">
              <Input
                value={newInputName}
                onChange={(e) => setNewInputName(e.target.value)}
                placeholder="Nome da nova entrada"
                className="flex-1"
              />
              <Button 
                type="button" 
                onClick={addInput}
                disabled={!newInputName.trim()}
              >
                <PlusIcon className="h-4 w-4 mr-1" />
                Adicionar
              </Button>
            </div>
          </div>
          
          <div className="space-y-4">
            <h3 className="font-medium">Saídas</h3>
            
            {data.outputs.map((output, index) => (
              <Card key={output.id} className="p-3 flex items-center justify-between">
                <div className="flex items-center gap-3 flex-1">
                  <div className="font-medium">{output.name}</div>
                  
                  <select
                    value={output.type}
                    onChange={(e) => updateOutputType(output.id, e.target.value)}
                    className="rounded-md border border-input bg-background px-2 py-1 text-sm"
                  >
                    <option value="string">Texto</option>
                    <option value="number">Número</option>
                    <option value="boolean">Booleano</option>
                    <option value="object">Objeto</option>
                    <option value="array">Array</option>
                  </select>
                </div>
                
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  onClick={() => removeOutput(output.id)}
                >
                  <XIcon className="h-4 w-4" />
                  <span className="sr-only">Remover saída</span>
                </Button>
              </Card>
            ))}
            
            <div className="flex gap-2">
              <Input
                value={newOutputName}
                onChange={(e) => setNewOutputName(e.target.value)}
                placeholder="Nome da nova saída"
                className="flex-1"
              />
              <Button 
                type="button" 
                onClick={addOutput}
                disabled={!newOutputName.trim()}
              >
                <PlusIcon className="h-4 w-4 mr-1" />
                Adicionar
              </Button>
            </div>
          </div>
        </TabsContent>
        
        <TabsContent value="code" className="space-y-4 pt-4">
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <label htmlFor="code" className="text-sm font-medium">Código</label>
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={handleTest}
              >
                <PlayIcon className="h-4 w-4 mr-1" />
                Testar
              </Button>
            </div>
            
            <Textarea
              id="code"
              value={data.code}
              onChange={(e) => updateField('code', e.target.value)}
              placeholder="// Insira o código JavaScript para este node"
              rows={15}
              className="font-mono"
            />
          </div>
          
          <div className="bg-muted/30 p-4 rounded-md">
            <h3 className="text-sm font-medium mb-2">Exemplo de código</h3>
            <pre className="text-xs overflow-auto p-2 bg-muted rounded-md">
{`// Exemplo de processador de texto
function process(inputs, outputs) {
  // Obter entrada
  const text = inputs.text;
  
  // Processar
  const processed = text.toUpperCase();
  
  // Definir saída
  outputs.result = processed;
  
  // Retornar sucesso
  return true;
}`}
            </pre>
          </div>
        </TabsContent>
        
        <TabsContent value="settings" className="space-y-4 pt-4">
          <div className="bg-muted/30 p-4 rounded-md mb-4">
            <div className="flex items-center gap-2">
              <InfoIcon className="h-5 w-5 text-blue-500" />
              <p className="text-sm">
                As configurações permitem que os usuários personalizem o comportamento do node
                sem modificar o código.
              </p>
            </div>
          </div>
          
          <div className="space-y-4">
            <Card className="p-4">
              <h3 className="font-medium mb-2">Configurações Avançadas</h3>
              <p className="text-sm text-muted-foreground mb-4">
                Esta funcionalidade será implementada em uma versão futura.
              </p>
              
              <Button variant="outline" disabled>
                <SettingsIcon className="h-4 w-4 mr-1" />
                Configurar Parâmetros
              </Button>
            </Card>
          </div>
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
          disabled={isLoading || !data.name}
        >
          {isLoading ? 'Salvando...' : 'Salvar Node'}
        </Button>
      </div>
    </form>
  );
}
