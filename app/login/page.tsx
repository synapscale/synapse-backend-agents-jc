/**
 * Login Page - Página de login
 * Integra com AuthProvider e ProtectedRoute
 */

'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { AuthProvider, useAuth } from '@/context/auth-context';
import { LoginForm } from '@/components/auth/login-form';
import { HydrationStatus } from '@/components/auth/hydration-status';

function LoginPageContent() {
  const { isAuthenticated, loading } = useAuth();
  const router = useRouter();

  // Redirecionar se já estiver autenticado
  useEffect(() => {
    if (isAuthenticated && !loading) {
      router.push('/team');
    }
  }, [isAuthenticated, loading, router]);

  // Mostrar loading se já estiver autenticado
  if (isAuthenticated && loading) {
    return (
      <div className="login-redirect">
        <h2>✅ Já Autenticado</h2>
        <p>Redirecionando para a página da equipe...</p>
        
        <style jsx>{`
          .login-redirect {
            text-align: center;
            padding: 2rem;
            background-color: #d4edda;
            color: #155724;
            border-radius: 8px;
            margin: 2rem;
          }
        `}</style>
      </div>
    );
  }

  return (
    <div className="login-page">
      <div className="login-container">
        <div className="login-header">
          <h1>🔐 Login - SynapScale</h1>
          <p>Faça login para acessar sua conta</p>
        </div>

        {/* Status de hidratação */}
        <HydrationStatus />

        <div className="login-form-container">
          <LoginForm
            onSuccess={() => {
              console.log('Login bem-sucedido, redirecionando...');
              router.push('/team');
            }}
            onError={(error) => {
              console.error('Erro no login:', error);
            }}
          />
        </div>

        <div className="login-footer">
          <div className="test-credentials">
            <h3>🧪 Credenciais de Teste</h3>
            <div className="credentials-box">
              <p><strong>Email:</strong> joaovictor@liderimobiliaria.com.br</p>
              <p><strong>Senha:</strong> @Teste123</p>
            </div>
          </div>

          <div className="features">
            <h3>✨ Recursos Disponíveis</h3>
            <ul>
              <li>✅ Autenticação JWT</li>
              <li>✅ Hidratação automática</li>
              <li>✅ Retry em caso de falha</li>
              <li>✅ Fallback para guest</li>
              <li>✅ Logging detalhado</li>
            </ul>
          </div>
        </div>
      </div>

      <style jsx>{`
        .login-page {
          min-height: 100vh;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 2rem;
        }

        .login-container {
          background-color: white;
          border-radius: 12px;
          box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
          padding: 2rem;
          max-width: 500px;
          width: 100%;
        }

        .login-header {
          text-align: center;
          margin-bottom: 2rem;
        }

        .login-header h1 {
          color: #333;
          margin-bottom: 0.5rem;
        }

        .login-header p {
          color: #666;
          margin: 0;
        }

        .login-form-container {
          margin-bottom: 2rem;
        }

        .login-footer {
          border-top: 1px solid #dee2e6;
          padding-top: 2rem;
        }

        .test-credentials {
          background-color: #f8f9fa;
          padding: 1rem;
          border-radius: 8px;
          margin-bottom: 1.5rem;
        }

        .test-credentials h3 {
          margin-top: 0;
          color: #333;
        }

        .credentials-box {
          background-color: white;
          padding: 1rem;
          border-radius: 4px;
          border: 1px solid #dee2e6;
          font-family: monospace;
        }

        .credentials-box p {
          margin: 0.5rem 0;
          color: #333;
        }

        .features {
          background-color: #e3f2fd;
          padding: 1rem;
          border-radius: 8px;
        }

        .features h3 {
          margin-top: 0;
          color: #1565c0;
        }

        .features ul {
          margin: 0;
          padding-left: 1.5rem;
        }

        .features li {
          margin-bottom: 0.5rem;
          color: #333;
        }

        @media (max-width: 600px) {
          .login-page {
            padding: 1rem;
          }

          .login-container {
            padding: 1.5rem;
          }
        }
      `}</style>
    </div>
  );
}

/**
 * ✅ Página de login com AuthProvider
 */
export default function LoginPage() {
  return (
    <AuthProvider>
      <LoginPageContent />
    </AuthProvider>
  );
}
