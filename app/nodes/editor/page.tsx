import React from 'react';
import { NodeSidebar } from '@/components/nodes-v0/node-sidebar';
import { NodeEditor } from '@/components/nodes-v0/node-editor';

export default function NodeEditorPage() {
  return (
    <div className="flex h-full">
      <NodeSidebar 
        onSelectCategory={(category) => {
          console.log('Categoria selecionada:', category);
        }}
        onSearch={(query) => {
          console.log('Busca por:', query);
        }}
        onCreateNode={() => {
          console.log('Criar novo node');
        }}
        selectedCategory="all"
      />
      
      <div className="flex-1 p-6 overflow-auto">
        <h1 className="text-2xl font-bold mb-6">Editor de Node</h1>
        
        <NodeEditor 
          onSave={(nodeData) => {
            console.log('Salvando node:', nodeData);
            // Em um cenário real, enviaria para a API
          }}
          onCancel={() => {
            console.log('Cancelando edição');
            // Em um cenário real, voltaria para a listagem
          }}
          onTest={(nodeData) => {
            console.log('Testando node:', nodeData);
            // Em um cenário real, executaria o teste
          }}
        />
      </div>
    </div>
  );
}
