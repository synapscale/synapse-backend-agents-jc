import React from 'react';
import { MarketplaceBrowser } from '@/components/nodes-v0/marketplace-browser';

export default function MarketplacePage() {
  return (
    <div className="container py-6">
      <MarketplaceBrowser 
        onSelectItem={(itemId) => {
          console.log('Item selecionado:', itemId);
          // Em um cenário real, abriria detalhes do item
        }}
        onInstallItem={(itemId) => {
          console.log('Instalando item:', itemId);
          // Em um cenário real, instalaria o item
        }}
      />
    </div>
  );
}
