import React from 'react';

export function Sidebar() {
  const menuItems = [
    {
      title: 'Principal',
      items: [
        { name: 'Dashboard', icon: 'dashboard', href: '/dashboard' },
        { name: 'Agentes De IA', icon: 'agents', href: '/agents' },
      ]
    },
    {
      title: 'Ferramentas',
      items: [
        { name: 'Canvas', icon: 'canvas', href: '/canvas' },
        { name: 'Prompts', icon: 'prompts', href: '/prompts' },
        { name: 'Chat', icon: 'chat', href: '/chat', active: true },
      ]
    },
    {
      title: 'Configurações',
      items: [
        { name: 'Configurações', icon: 'settings', href: '/settings' },
      ]
    }
  ];

  return (
    <div className="w-60 h-full border-r bg-white flex flex-col">
      <div className="p-4 flex items-center space-x-2">
        <div className="w-8 h-8 bg-blue-600 rounded-md flex items-center justify-center text-white font-bold">
          JC
        </div>
        <div>
          <h1 className="font-bold">Agente AI</h1>
          <p className="text-xs text-gray-500">Canvas</p>
        </div>
      </div>

      <nav className="flex-1 overflow-y-auto p-2">
        {menuItems.map((section) => (
          <div key={section.title} className="mb-6">
            <h2 className="text-xs font-medium text-gray-500 px-3 mb-2">{section.title}</h2>
            <ul>
              {section.items.map((item) => (
                <li key={item.name}>
                  <a
                    href={item.href}
                    className={`flex items-center space-x-2 px-3 py-2 rounded-md text-sm ${
                      item.active ? 'bg-blue-50 text-blue-600' : 'text-gray-700 hover:bg-gray-100'
                    }`}
                  >
                    <span className="w-5 h-5 flex items-center justify-center">
                      {getIcon(item.icon)}
                    </span>
                    <span>{item.name}</span>
                  </a>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </nav>

      <div className="p-4 border-t flex items-center space-x-2">
        <div className="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center">
          U
        </div>
        <div>
          <p className="text-sm font-medium">Usuário</p>
          <p className="text-xs text-gray-500">Online</p>
        </div>
      </div>
    </div>
  );
}

function getIcon(name) {
  switch (name) {
    case 'dashboard':
      return (
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <rect x="3" y="3" width="7" height="7"></rect>
          <rect x="14" y="3" width="7" height="7"></rect>
          <rect x="14" y="14" width="7" height="7"></rect>
          <rect x="3" y="14" width="7" height="7"></rect>
        </svg>
      );
    case 'agents':
      return (
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
          <circle cx="12" cy="7" r="4"></circle>
        </svg>
      );
    case 'canvas':
      return (
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
          <line x1="3" y1="9" x2="21" y2="9"></line>
          <line x1="9" y1="21" x2="9" y2="9"></line>
        </svg>
      );
    case 'prompts':
      return (
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
          <polyline points="14 2 14 8 20 8"></polyline>
          <line x1="16" y1="13" x2="8" y2="13"></line>
          <line x1="16" y1="17" x2="8" y2="17"></line>
          <polyline points="10 9 9 9 8 9"></polyline>
        </svg>
      );
    case 'chat':
      return (
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
        </svg>
      );
    case 'settings':
      return (
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="12" cy="12" r="3"></circle>
          <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
        </svg>
      );
    default:
      return null;
  }
}
