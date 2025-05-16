import React from 'react';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card } from '@/components/ui/card';

interface PromptEditorProps {
  value: string;
  onChange: (value: string) => void;
  onSave?: () => void;
  isLoading?: boolean;
}

export function PromptEditor({
  value,
  onChange,
  onSave,
  isLoading = false
}: PromptEditorProps) {
  const [activeTab, setActiveTab] = React.useState('editor');
  const [previewContent, setPreviewContent] = React.useState('');
  
  // Gerar preview quando o tab de preview é selecionado
  React.useEffect(() => {
    if (activeTab === 'preview') {
      // Simular processamento de variáveis
      let processed = value;
      processed = processed.replace(/{{input}}/g, '[Entrada do usuário]');
      processed = processed.replace(/{{context}}/g, '[Contexto da conversa]');
      processed = processed.replace(/{{date}}/g, new Date().toLocaleDateString());
      processed = processed.replace(/{{time}}/g, new Date().toLocaleTimeString());
      
      setPreviewContent(processed);
    }
  }, [activeTab, value]);
  
  // Templates de prompt
  const templates = [
    {
      name: 'Assistente Padrão',
      content: 'Você é um assistente AI útil e amigável. Responda às perguntas do usuário de forma clara e concisa.\n\nEntrada do usuário: {{input}}\n\nContexto: {{context}}\n\nData: {{date}}\nHora: {{time}}'
    },
    {
      name: 'Especialista Técnico',
      content: 'Você é um especialista técnico com profundo conhecimento em programação, ciência da computação e tecnologia. Forneça respostas detalhadas e precisas para questões técnicas.\n\nEntrada do usuário: {{input}}\n\nContexto: {{context}}\n\nData: {{date}}\nHora: {{time}}'
    },
    {
      name: 'Gerador de Ideias',
      content: 'Você é um gerador de ideias criativas. Quando o usuário fornecer um tópico ou problema, gere 3-5 ideias inovadoras relacionadas.\n\nTópico: {{input}}\n\nContexto: {{context}}\n\nData: {{date}}\nHora: {{time}}'
    }
  ];

  return (
    <div className="space-y-4">
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid grid-cols-2">
          <TabsTrigger value="editor">Editor</TabsTrigger>
          <TabsTrigger value="preview">Preview</TabsTrigger>
        </TabsList>
        
        <TabsContent value="editor" className="space-y-4">
          <Textarea
            value={value}
            onChange={(e) => onChange(e.target.value)}
            placeholder="Insira o prompt para o agente..."
            className="min-h-[300px] font-mono"
          />
          
          <div className="bg-muted/30 p-4 rounded-md">
            <h3 className="text-sm font-medium mb-2">Variáveis disponíveis</h3>
            <div className="grid grid-cols-2 gap-2 text-sm">
              <div><code>{'{{input}}'}</code> - Entrada do usuário</div>
              <div><code>{'{{context}}'}</code> - Contexto da conversa</div>
              <div><code>{'{{date}}'}</code> - Data atual</div>
              <div><code>{'{{time}}'}</code> - Hora atual</div>
            </div>
          </div>
          
          <div className="space-y-2">
            <h3 className="text-sm font-medium">Templates</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
              {templates.map((template, index) => (
                <Button
                  key={index}
                  variant="outline"
                  className="h-auto py-2 justify-start text-left"
                  onClick={() => onChange(template.content)}
                >
                  <div>
                    <div className="font-medium">{template.name}</div>
                    <div className="text-xs text-muted-foreground truncate">
                      {template.content.substring(0, 50)}...
                    </div>
                  </div>
                </Button>
              ))}
            </div>
          </div>
        </TabsContent>
        
        <TabsContent value="preview">
          <Card className="p-4 min-h-[300px] whitespace-pre-wrap">
            {previewContent || 'Nenhum conteúdo para preview'}
          </Card>
        </TabsContent>
      </Tabs>
      
      {onSave && (
        <div className="flex justify-end">
          <Button onClick={onSave} disabled={isLoading}>
            {isLoading ? 'Salvando...' : 'Salvar Prompt'}
          </Button>
        </div>
      )}
    </div>
  );
}
