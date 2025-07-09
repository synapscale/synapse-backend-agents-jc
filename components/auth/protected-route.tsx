/**
 * ProtectedRoute - Componente para proteger rotas que requerem autenticação
 * Corrige o erro: "Cannot update a component (Router) while rendering a different component (ProtectedRoute)"
 */

'use client';

import { useEffect, useState, ReactNode } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/context/auth-context';
import { HydrationState } from '@/lib/services/auth-hydration';

interface ProtectedRouteProps {
  children: ReactNode;
  fallback?: ReactNode;
  redirectTo?: string;
  requireAuth?: boolean;
  requiredRoles?: string[];
}

export function ProtectedRoute({
  children,
  fallback,
  redirectTo = '/login',
  requireAuth = true,
  requiredRoles = []
}: ProtectedRouteProps) {
  const router = useRouter();
  const { user, isAuthenticated, loading, hydrationState } = useAuth();
  const [shouldRedirect, setShouldRedirect] = useState(false);

  /**
   * ✅ useEffect para redirecionamento - CORRIGE O ERRO
   * Redirecionamento só acontece após o render, não durante
   */
  useEffect(() => {
    // Aguardar hidratação completar
    if (hydrationState === HydrationState.LOADING || loading) {
      return;
    }

    // Se a hidratação falhou, mas ainda está carregando, aguardar
    if (hydrationState === HydrationState.FAILED && loading) {
      return;
    }

    // Verificar se precisa de autenticação
    if (requireAuth && !isAuthenticated) {
      setShouldRedirect(true);
      return;
    }

    // Verificar roles se necessário
    if (requiredRoles.length > 0 && user) {
      const userRoles = user.roles || [];
      const hasRequiredRole = requiredRoles.some(role => userRoles.includes(role));
      
      if (!hasRequiredRole) {
        setShouldRedirect(true);
        return;
      }
    }

    // Usuário autenticado e autorizado
    setShouldRedirect(false);
  }, [isAuthenticated, user, loading, hydrationState, requireAuth, requiredRoles]);

  /**
   * ✅ Efetuar redirecionamento em useEffect separado
   */
  useEffect(() => {
    if (shouldRedirect) {
      const timer = setTimeout(() => {
        router.push(redirectTo);
      }, 100); // Pequeno delay para evitar conflitos

      return () => clearTimeout(timer);
    }
  }, [shouldRedirect, router, redirectTo]);

  /**
   * ✅ Estados de loading
   */
  if (loading || hydrationState === HydrationState.LOADING) {
    return (
      <div className="protected-route-loading">
        <div className="loading-spinner">
          <div className="spinner"></div>
        </div>
        <p>Verificando autenticação...</p>
        
        <style jsx>{`
          .protected-route-loading {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 200px;
            padding: 2rem;
          }

          .loading-spinner {
            margin-bottom: 1rem;
          }

          .spinner {
            width: 40px;
            height: 40px;
            border: 4px solid #f3f3f3;
            border-top: 4px solid #007bff;
            border-radius: 50%;
            animation: spin 1s linear infinite;
          }

          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }

          p {
            color: #666;
            margin: 0;
          }
        `}</style>
      </div>
    );
  }

  /**
   * ✅ Estado de redirecionamento
   */
  if (shouldRedirect) {
    return (
      <div className="protected-route-redirect">
        <div className="redirect-message">
          <div className="redirect-icon">🔐</div>
          <h3>Redirecionando...</h3>
          <p>Você será redirecionado para a página de login.</p>
        </div>
        
        <style jsx>{`
          .protected-route-redirect {
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 200px;
            padding: 2rem;
          }

          .redirect-message {
            text-align: center;
            max-width: 400px;
          }

          .redirect-icon {
            font-size: 3rem;
            margin-bottom: 1rem;
          }

          h3 {
            color: #333;
            margin-bottom: 0.5rem;
          }

          p {
            color: #666;
            margin: 0;
          }
        `}</style>
      </div>
    );
  }

  /**
   * ✅ Fallback para falha de hidratação
   */
  if (hydrationState === HydrationState.FAILED && fallback) {
    return <>{fallback}</>;
  }

  /**
   * ✅ Usuário não autenticado mas não requer auth
   */
  if (!requireAuth) {
    return <>{children}</>;
  }

  /**
   * ✅ Usuário autenticado e autorizado
   */
  if (isAuthenticated) {
    return <>{children}</>;
  }

  /**
   * ✅ Fallback padrão
   */
  return (
    <div className="protected-route-fallback">
      <div className="access-denied">
        <div className="denied-icon">⛔</div>
        <h3>Acesso Negado</h3>
        <p>Você não tem permissão para acessar esta página.</p>
        <button 
          onClick={() => router.push(redirectTo)}
          className="login-button"
        >
          Ir para Login
        </button>
      </div>
      
      <style jsx>{`
        .protected-route-fallback {
          display: flex;
          align-items: center;
          justify-content: center;
          min-height: 300px;
          padding: 2rem;
        }

        .access-denied {
          text-align: center;
          max-width: 400px;
        }

        .denied-icon {
          font-size: 3rem;
          margin-bottom: 1rem;
        }

        h3 {
          color: #dc3545;
          margin-bottom: 0.5rem;
        }

        p {
          color: #666;
          margin-bottom: 1.5rem;
        }

        .login-button {
          background-color: #007bff;
          color: white;
          padding: 0.75rem 1.5rem;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          font-size: 1rem;
          font-weight: 500;
        }

        .login-button:hover {
          background-color: #0056b3;
        }
      `}</style>
    </div>
  );
}

/**
 * ✅ HOC para proteger páginas
 */
export function withProtectedRoute<T extends object>(
  Component: React.ComponentType<T>,
  options: Omit<ProtectedRouteProps, 'children'> = {}
) {
  return function ProtectedComponent(props: T) {
    return (
      <ProtectedRoute {...options}>
        <Component {...props} />
      </ProtectedRoute>
    );
  };
}

/**
 * ✅ Hook para verificar acesso
 */
export function useProtectedRoute(requiredRoles: string[] = []) {
  const { user, isAuthenticated, loading } = useAuth();
  const router = useRouter();

  const hasAccess = () => {
    if (!isAuthenticated) return false;
    
    if (requiredRoles.length === 0) return true;
    
    if (!user) return false;
    
    const userRoles = user.roles || [];
    return requiredRoles.some(role => userRoles.includes(role));
  };

  const redirectToLogin = (path: string = '/login') => {
    setTimeout(() => {
      router.push(path);
    }, 100);
  };

  return {
    hasAccess: hasAccess(),
    isAuthenticated,
    loading,
    user,
    redirectToLogin
  };
}

export default ProtectedRoute;
