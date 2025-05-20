// Mock básico do MarketplaceService para evitar erro de build

export const MarketplaceService = {
  async searchItems({ type, sortBy, page, pageSize }: any) {
    // Retorna um mock de itens
    return {
      items: [
        { id: 1, name: 'Item 1', description: 'Descrição do item 1' },
        { id: 2, name: 'Item 2', description: 'Descrição do item 2' }
      ]
    };
  },
  async getFeaturedCollections(count: number) {
    // Retorna um mock de coleções
    return [
      { id: 1, name: 'Coleção 1', items: [] },
      { id: 2, name: 'Coleção 2', items: [] }
    ];
  }
};
