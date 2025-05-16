import React from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { PromptEditor } from '@/components/agents-v0/prompt-editor';

export default function AgentEditPage({ params }: { params: { id: string } }) {
  const [activeTab, setActiveTab] = React.useState('basic');
  const [prompt, setPrompt] = React.useState(`Você é um assistente AI útil e amigável. Responda às perguntas do usuário de forma clara e concisa.

Entrada do usuário: {{input}}

Contexto: {{context}}

Data: {{date}}
Hora: {{time}}`);

  // Em um cenário real, carregaria os dados do agente com base no ID
  const agentId = params.id;

  return (
    <div className="container py-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Editar Agente</h1>
        
        <div className="flex items-center gap-2">
          <Button variant="outline" onClick={() => window.location.href = '/agents'}>
            Cancelar
          </Button>
          <Button onClick={() => {
            console.log('Salvando alterações');
            // Em um cenário real, salvaria as alterações
            window.location.href = '/agents';
          }}>
            Salvar Alterações
          </Button>
        </div>
      </div>
      
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid grid-cols-4 w-full">
          <TabsTrigger value="basic">Informações Básicas</TabsTrigger>
          <TabsTrigger value="prompt">Prompt</TabsTrigger>
          <TabsTrigger value="parameters">Parâmetros</TabsTrigger>
          <TabsTrigger value="connections">Conexões</TabsTrigger>
        </TabsList>
        
        <TabsContent value="basic">
          <div className="bg-muted/30 p-8 rounded-md text-center">
            <p>Edição de informações básicas do agente {agentId}</p>
          </div>
        </TabsContent>
        
        <TabsContent value="prompt">
          <PromptEditor
            value={prompt}
            onChange={setPrompt}
            onSave={() => {
              console.log('Salvando prompt');
              // Em um cenário real, salvaria o prompt
            }}
          />
        </TabsContent>
        
        <TabsContent value="parameters">
          <div className="bg-muted/30 p-8 rounded-md text-center">
            <p>Edição de parâmetros do agente {agentId}</p>
          </div>
        </TabsContent>
        
        <TabsContent value="connections">
          <div className="bg-muted/30 p-8 rounded-md text-center">
            <p>Edição de conexões do agente {agentId}</p>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
