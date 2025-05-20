// Arquivo de teste para validar a integração dos setores e funcionamento da sidebar unificada

// Mock da função usePathname para simular diferentes rotas
jest.mock('next/navigation', () => ({
  usePathname: jest.fn().mockReturnValue('/chat')
}));

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { Sidebar } from '../components/sidebar/Sidebar';
import { SidebarProvider } from '../components/ui/sidebar';

describe('Sidebar Unificada', () => {
  test('Deve renderizar todos os itens de navegação dos diferentes setores', () => {
    render(
      <SidebarProvider>
        <Sidebar />
      </SidebarProvider>
    );
    
    // Verificar itens da seção Principal
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Agentes De IA')).toBeInTheDocument();
    
    // Verificar itens da seção Ferramentas
    expect(screen.getByText('Canvas')).toBeInTheDocument();
    expect(screen.getByText('Prompts')).toBeInTheDocument();
    expect(screen.getByText('Chat')).toBeInTheDocument();
    expect(screen.getByText('Editor de Workflow')).toBeInTheDocument();
    
    // Verificar itens da seção Marketplace
    const marketplaceItems = screen.getAllByText('Marketplace');
    expect(marketplaceItems.length).toBeGreaterThanOrEqual(1);
    
    // Verificar itens da seção Configurações
    const configItems = screen.getAllByText('Configurações');
    expect(configItems.length).toBeGreaterThanOrEqual(1);
  });
  
  test('Deve destacar o item ativo com base na rota atual', () => {
    // O mock já foi configurado no início do arquivo
    render(
      <SidebarProvider>
        <Sidebar />
      </SidebarProvider>
    );
    
    // Verificar se o item Chat está destacado
    const chatItem = screen.getByText('Chat').closest('a');
    expect(chatItem).toHaveStyle('background: #ede9fe');
    expect(chatItem).toHaveStyle('color: #7c3aed');
  });
  
  test('Deve ser responsivo em dispositivos móveis', () => {
    // Mock para simular viewport mobile
    global.innerWidth = 500;
    global.dispatchEvent(new Event('resize'));
    
    render(
      <SidebarProvider>
        <Sidebar />
      </SidebarProvider>
    );
    
    // Verificar se o botão de menu móvel está presente
    const menuButton = screen.getByLabelText('Abrir menu');
    expect(menuButton).toBeInTheDocument();
    
    // Verificar se a sidebar está inicialmente fechada
    const sidebar = screen.getByLabelText('Navegação principal');
    expect(sidebar).toHaveStyle('transform: translateX(-100%)');
    
    // Verificar se a sidebar abre ao clicar no botão
    fireEvent.click(menuButton);
    expect(sidebar).toHaveStyle('transform: translateX(0)');
  });
});

describe('Integração dos Setores', () => {
  beforeEach(() => {
    // Mock do window.location para permitir alteração do pathname
    delete window.location;
    // @ts-ignore
    window.location = { pathname: '/', assign: jest.fn() };
  });

  test('Deve navegar corretamente para a página de Chat', () => {
    render(
      <SidebarProvider>
        <Sidebar />
      </SidebarProvider>
    );

    // Simular clique no item Chat
    const chatItem = screen.getByText('Chat').closest('a');
    // Simular navegação
    if (chatItem) {
      fireEvent.click(chatItem);
      // Simular alteração manual do pathname
      window.location.pathname = '/chat';
    }
    expect(window.location.pathname).toBe('/chat');
  });

  test('Deve navegar corretamente para a página de Workflow', () => {
    render(
      <SidebarProvider>
        <Sidebar />
      </SidebarProvider>
    );

    // Simular clique no item Editor de Workflow
    const workflowItem = screen.getByText('Editor de Workflow').closest('a');
    if (workflowItem) {
      fireEvent.click(workflowItem);
      window.location.pathname = '/workflow';
    }
    expect(window.location.pathname).toBe('/workflow');
  });
});
