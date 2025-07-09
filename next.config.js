/** @type {import('next').NextConfig} */
const nextConfig = {
  // Configurações para suportar styled-jsx
  experimental: {
    // Habilitar styled-jsx para componentes com CSS inline
    styledComponents: true,
  },
  
  // Configurações de reescrita para API proxy (opcional)
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/api/:path*',
      },
    ];
  },
  
  // Configurações de cabeçalhos para CORS
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'Access-Control-Allow-Origin',
            value: '*',
          },
          {
            key: 'Access-Control-Allow-Methods',
            value: 'GET, POST, PUT, DELETE, OPTIONS',
          },
          {
            key: 'Access-Control-Allow-Headers',
            value: 'Content-Type, Authorization',
          },
        ],
      },
    ];
  },
  
  // Configurações de ambiente
  env: {
    NEXT_PUBLIC_API_BASE: process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000/api/v1',
    NEXT_PUBLIC_APP_ENV: process.env.NEXT_PUBLIC_APP_ENV || 'development',
  },
  
  // Configurações de TypeScript
  typescript: {
    // Não falhar o build por erros de TypeScript em desenvolvimento
    ignoreBuildErrors: process.env.NODE_ENV === 'development',
  },
  
  // Configurações de ESLint
  eslint: {
    // Não falhar o build por erros de ESLint em desenvolvimento
    ignoreDuringBuilds: process.env.NODE_ENV === 'development',
  },
};

module.exports = nextConfig;
