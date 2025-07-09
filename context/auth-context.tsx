/**
 * AuthContext - Context de autenticação com hidratação corrigida
 * Resolve problemas de sincronização e hidratação
 */

'use client';

import { createContext, useContext, useCallback, useState, useEffect, ReactNode } from 'react';
import { authService, type LoginCredentials, type User } from '@/lib/services/auth';
import { 
  authHydrationService, 
  HydrationState, 
  AuthError, 
  AuthErrorCode 
} from '@/lib/services/auth-hydration';
import { authLogger } from '@/lib/utils/logger';

interface AuthContextType {
  user: User | null;
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => Promise<void>;
  isAuthenticated: boolean;
  loading: boolean;
  error: string | null;
  clearError: () => void;
  refreshUser: () => Promise<void>;
  hydrationState: HydrationState;
  retryHydration: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [hydrationState, setHydrationState] = useState<HydrationState>(HydrationState.PENDING);

  /**
   * ✅ Login function - CORRIGIDA
   */
  const login = useCallback(async (credentials: LoginCredentials) => {
    try {
      setLoading(true);
      setError(null);
      
      authLogger.info('Iniciando processo de login', { email: credentials.email });
      
      const response = await authService.login(credentials);
      setUser(response.data.user);
      
      authLogger.authSuccess('Login realizado com sucesso', {
        userId: response.data.user.id,
        email: response.data.user.email
      });
      
    } catch (error: any) {
      const errorMessage = error.message || 'Erro ao fazer login';
      setError(errorMessage);
      authLogger.authError('Falha no login', error);
      throw error;
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * ✅ Logout function - CORRIGIDA
   */
  const logout = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      authLogger.info('Iniciando processo de logout');
      
      await authService.logout();
      setUser(null);
      
      // Resetar estado de hidratação
      authHydrationService.reset();
      setHydrationState(HydrationState.PENDING);
      
      authLogger.authSuccess('Logout realizado com sucesso');
      
    } catch (error: any) {
      authLogger.authError('Erro durante logout', error);
      // Sempre limpar o usuário mesmo se houver erro
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * ✅ Refresh user function
   */
  const refreshUser = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      authLogger.info('Atualizando dados do usuário');
      
      const userData = await authService.verifyUser();
      setUser(userData);
      
      if (userData) {
        authLogger.info('Dados do usuário atualizados com sucesso');
      } else {
        authLogger.info('Usuário não encontrado, fazendo logout');
      }
      
    } catch (error: any) {
      authLogger.authError('Erro ao atualizar usuário', error);
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * ✅ Retry hydration function
   */
  const retryHydration = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      authLogger.info('Reexecutando hidratação do estado');
      
      const result = await authHydrationService.refresh();
      
      if (result.success) {
        setUser(result.user);
        setHydrationState(HydrationState.SUCCESS);
        authLogger.authSuccess('Hidratação reexecutada com sucesso');
      } else {
        setHydrationState(HydrationState.FAILED);
        if (result.error) {
          setError(result.error.message);
          authLogger.authError('Falha na reexecução da hidratação', result.error);
        }
      }
      
    } catch (error: any) {
      setHydrationState(HydrationState.FAILED);
      setError(error.message || 'Erro na reexecução da hidratação');
      authLogger.authError('Erro crítico na reexecução da hidratação', error);
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * ✅ Clear error function
   */
  const clearError = useCallback(() => {
    setError(null);
    authLogger.info('Erro de autenticação limpo');
  }, []);

  /**
   * ✅ Initialize auth state com hidratação - CORRIGIDA
   */
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        setLoading(true);
        setError(null);
        setHydrationState(HydrationState.LOADING);
        
        authLogger.info('Iniciando inicialização do estado de autenticação');
        
        // Configurar serviço de hidratação
        authHydrationService.configure({
          maxRetries: 3,
          retryDelay: 1000,
          timeout: 10000,
          validateToken: true,
          fallbackToGuest: true
        });
        
        // ✅ Executar hidratação do estado
        const result = await authHydrationService.hydrateAuthState();
        
        if (result.success) {
          setUser(result.user);
          setHydrationState(HydrationState.SUCCESS);
          
          authLogger.authSuccess('Estado de autenticação hidratado com sucesso', {
            user: result.user?.email || 'guest',
            attempts: result.attempts
          });
        } else {
          setHydrationState(HydrationState.FAILED);
          
          if (result.error) {
            // Não mostrar erro de hidratação como erro crítico para o usuário
            if (result.error.code === AuthErrorCode.HYDRATION_FAILED) {
              authLogger.warn('Hidratação falhou, iniciando como convidado');
            } else {
              setError(result.error.message);
              authLogger.authError('Falha na hidratação do estado', result.error);
            }
          }
        }
        
      } catch (error: any) {
        setHydrationState(HydrationState.FAILED);
        setError(error.message || 'Erro na inicialização da autenticação');
        authLogger.authError('Erro crítico na inicialização', error);
      } finally {
        setLoading(false);
      }
    };

    initializeAuth();
  }, []);

  /**
   * ✅ Context value
   */
  const value: AuthContextType = {
    user,
    login,
    logout,
    isAuthenticated: !!user,
    loading,
    error,
    clearError,
    refreshUser,
    hydrationState,
    retryHydration,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

/**
 * ✅ useAuth hook - CORRIGIDO
 */
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// ✅ Exportar tipos
export type { AuthContextType };
