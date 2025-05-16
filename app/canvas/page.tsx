import React from 'react';
import { NodeSidebar } from '@/components/node-sidebar/node-sidebar';

export default function CanvasPage() {
  return (
    <div className="flex h-full">
      <NodeSidebar />
      <div className="flex-1 p-4">
        <div className="h-full flex items-center justify-center text-center">
          <div>
            <h2 className="text-2xl font-semibold mb-2">Canvas Vazio</h2>
            <p className="text-muted-foreground">Arraste e solte nodes da sidebar para começar a construir seu fluxo.</p>
          </div>
        </div>
      </div>
    </div>
  );
}
