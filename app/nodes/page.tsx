import React from 'react';
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';

export default function NodesPage() {
  return (
    <div className="flex h-full">
      {/* Sidebar estreita à esquerda */}
      <div className="w-12 border-r flex flex-col items-center py-4 bg-white">
        <button className="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center mb-4">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 5L5 12L12 19M5 12H19" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </button>
        <button className="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center mb-4">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M19 11H5M19 11C20.1046 11 21 11.8954 21 13V19C21 20.1046 20.1046 21 19 21H5C3.89543 21 3 20.1046 3 19V13C3 11.8954 3.89543 11 5 11M19 11V9C19 7.89543 18.1046 7 17 7M5 11V9C5 7.89543 5.89543 7 7 7M7 7V5C7 3.89543 7.89543 3 9 3H15C16.1046 3 17 3.89543 17 5V7M7 7H17" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </button>
        <button className="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M10.325 4.317C10.751 2.561 13.249 2.561 13.675 4.317C13.7389 4.5808 13.8642 4.82578 14.0407 5.032C14.2172 5.23822 14.4399 5.39985 14.6907 5.50375C14.9414 5.60764 15.2132 5.65085 15.4838 5.62987C15.7544 5.60889 16.0162 5.5243 16.248 5.383C17.791 4.443 19.558 6.209 18.618 7.753C18.4769 7.98466 18.3924 8.24634 18.3715 8.51677C18.3506 8.78721 18.3938 9.05877 18.4975 9.30938C18.6013 9.55999 18.7627 9.78258 18.9687 9.95905C19.1747 10.1355 19.4194 10.2609 19.683 10.325C21.439 10.751 21.439 13.249 19.683 13.675C19.4192 13.7389 19.1742 13.8642 18.968 14.0407C18.7618 14.2172 18.6001 14.4399 18.4963 14.6907C18.3924 14.9414 18.3491 15.2132 18.3701 15.4838C18.3911 15.7544 18.4757 16.0162 18.617 16.248C19.557 17.791 17.791 19.558 16.247 18.618C16.0153 18.4769 15.7537 18.3924 15.4832 18.3715C15.2128 18.3506 14.9412 18.3938 14.6906 18.4975C14.44 18.6013 14.2174 18.7627 14.0409 18.9687C13.8645 19.1747 13.7391 19.4194 13.675 19.683C13.249 21.439 10.751 21.439 10.325 19.683C10.2611 19.4192 10.1358 19.1742 9.95929 18.968C9.7828 18.7618 9.56011 18.6001 9.30935 18.4963C9.05859 18.3924 8.78683 18.3491 8.51621 18.3701C8.24559 18.3911 7.98375 18.4757 7.752 18.617C6.209 19.557 4.442 17.791 5.382 16.247C5.5231 16.0153 5.60755 15.7537 5.62848 15.4832C5.64942 15.2128 5.60624 14.9412 5.50247 14.6906C5.3987 14.44 5.23726 14.2174 5.03127 14.0409C4.82529 13.8645 4.58056 13.7391 4.317 13.675C2.561 13.249 2.561 10.751 4.317 10.325C4.5808 10.2611 4.82578 10.1358 5.032 9.95929C5.23822 9.7828 5.39985 9.56011 5.50375 9.30935C5.60764 9.05859 5.65085 8.78683 5.62987 8.51621C5.60889 8.24559 5.5243 7.98375 5.383 7.752C4.443 6.209 6.209 4.442 7.753 5.382C8.753 5.99 10.049 5.452 10.325 4.317Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            <path d="M15 12C15 13.6569 13.6569 15 12 15C10.3431 15 9 13.6569 9 12C9 10.3431 10.3431 9 12 9C13.6569 9 15 10.3431 15 12Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </button>
      </div>
      
      {/* Painel lateral com abas */}
      <div className="w-80 border-r bg-white flex flex-col">
        <div className="p-4 border-b">
          <h2 className="font-medium">Canvas</h2>
        </div>
        
        <div className="border-b">
          <Tabs defaultValue="templates" className="w-full">
            <TabsList className="grid grid-cols-3 w-full">
              <TabsTrigger value="navegar">Navegar</TabsTrigger>
              <TabsTrigger value="templates">Templates</TabsTrigger>
              <TabsTrigger value="meus-nodes">Meus Nodes</TabsTrigger>
            </TabsList>
          </Tabs>
        </div>
        
        <div className="p-4">
          <div className="relative mb-4">
            <Input
              type="text"
              placeholder="Buscar nodes..."
              className="pl-8 pr-4 py-2 w-full"
            />
            <svg
              className="absolute left-3 top-2.5 h-4 w-4 text-gray-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
              />
            </svg>
          </div>
          
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-medium">Templates</h3>
            <Button variant="ghost" size="sm" className="h-8 px-2">
              <span className="mr-1">+</span> Novo
            </Button>
          </div>
          
          <div className="text-center py-8">
            <p className="text-gray-500 mb-4">Você ainda não criou nenhum template.</p>
            <Button variant="outline" size="sm" className="mx-auto">
              <span className="mr-1">+</span> Criar Primeiro Template
            </Button>
          </div>
        </div>
      </div>
      
      {/* Área principal */}
      <div className="flex-1 bg-white p-4 flex flex-col">
        <div className="flex justify-end mb-4">
          <div className="flex items-center space-x-2 bg-white rounded-md border px-2 py-1">
            <button className="p-1 hover:bg-gray-100 rounded">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M10 19L3 12M3 12L10 5M3 12H21" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </button>
            <button className="p-1 hover:bg-gray-100 rounded">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M14 5L21 12M21 12L14 19M21 12H3" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </button>
            <button className="p-1 hover:bg-gray-100 rounded">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M21 21L15 15M17 10C17 13.866 13.866 17 10 17C6.13401 17 3 13.866 3 10C3 6.13401 6.13401 3 10 3C13.866 3 17 6.13401 17 10Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </button>
            <button className="p-1 hover:bg-gray-100 rounded">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M21 21L15 15M10 17C13.866 17 17 13.866 17 10C17 6.13401 13.866 3 10 3C6.13401 3 3 6.13401 3 10C3 13.866 6.13401 17 10 17Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                <path d="M12 7H8M10 9V5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </button>
            <button className="p-1 hover:bg-gray-100 rounded">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M9 3H5C3.89543 3 3 3.89543 3 5V9M9 3H15M9 3V5C9 7.76142 11.2386 10 14 10H15M15 3H19C20.1046 3 21 3.89543 21 5V9M15 3V5C15 7.76142 12.7614 10 10 10H9M9 21H5C3.89543 21 3 20.1046 3 19V15M9 21H15M9 21V19C9 16.2386 11.2386 14 14 14H15M15 21H19C20.1046 21 21 20.1046 21 19V15M15 21V19C15 16.2386 12.7614 14 10 14H9M3 9V15M21 9V15" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </button>
            <div className="h-4 border-r mx-1"></div>
            <button className="flex items-center space-x-1 px-2 py-1 hover:bg-gray-100 rounded text-sm">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 3V5M12 19V21M5 12H3M21 12H19M18.364 5.63604L16.95 7.04999M7.05 16.95L5.636 18.364M16.95 16.95L18.364 18.364M7.05 7.04999L5.636 5.63604" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
              <span>Tema: Padrão</span>
            </button>
          </div>
        </div>
        
        <div className="flex-1 flex flex-col items-center justify-center">
          <h2 className="text-2xl font-bold mb-2">Canvas Vazio</h2>
          <p className="text-gray-500">Arraste e solte nodes da sidebar para começar a construir seu fluxo.</p>
        </div>
      </div>
    </div>
  );
}
