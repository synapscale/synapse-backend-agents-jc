/**
 * useAuth Hook - Hook customizado para autenticação
 * Simplifica o uso do AuthContext
 */

'use client';

import { useAuth as useAuthContext } from '@/context/auth-context';
import { type LoginCredentials } from '@/lib/services/auth';

/**
 * ✅ Hook useLogin - CORRIGIDO
 */
export const useLogin = () => {
  const { login, loading, error } = useAuthContext();
  
  return {
    login: async (credentials: LoginCredentials) => {
      try {
        await login(credentials);
      } catch (error) {
        console.error('Login hook error:', error);
        throw error;
      }
    },
    loading,
    error,
  };
};

/**
 * ✅ Hook useLogout - CORRIGIDO
 */
export const useLogout = () => {
  const { logout, loading } = useAuthContext();
  
  return {
    logout: async () => {
      try {
        await logout();
      } catch (error) {
        console.error('Logout hook error:', error);
        throw error;
      }
    },
    loading,
  };
};

/**
 * ✅ Hook useCurrentUser
 */
export const useCurrentUser = () => {
  const { user, loading, refreshUser } = useAuthContext();
  
  return {
    user,
    loading,
    refreshUser,
    isAuthenticated: !!user,
  };
};

/**
 * ✅ Hook principal useAuth
 */
export const useAuth = useAuthContext;

// ✅ Exportar hooks específicos
export { useLogin, useLogout, useCurrentUser };
