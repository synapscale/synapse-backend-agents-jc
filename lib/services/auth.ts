/**
 * AuthService - Serviço de autenticação para o frontend
 * Corrige o erro: authService.setToken is not a function
 */

interface AuthTokens {
  accessToken: string | null;
  refreshToken: string | null;
}

interface LoginCredentials {
  email: string;
  password: string;
}

interface LoginResponse {
  status: string;
  message: string;
  data: {
    access_token: string;
    refresh_token: string | null;
    token_type: string;
    user: {
      id: string;
      email: string;
      username: string;
      is_active: boolean;
      is_verified: boolean;
      tenant_id: string;
    };
  };
  request_id: string;
  timestamp: string;
}

interface User {
  id: string;
  email: string;
  username: string;
  is_active: boolean;
  is_verified: boolean;
  tenant_id: string;
}

class AuthService {
  private readonly API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000/api/v1';
  private readonly TOKEN_KEY = 'synapse_auth_token';
  private readonly REFRESH_TOKEN_KEY = 'synapse_refresh_token';
  private readonly USER_KEY = 'synapse_user';

  /**
   * ✅ Método setToken - CORRIGE O ERRO PRINCIPAL
   */
  setToken(token: string | null): void {
    if (typeof window === 'undefined') return;
    
    if (token) {
      localStorage.setItem(this.TOKEN_KEY, token);
    } else {
      localStorage.removeItem(this.TOKEN_KEY);
    }
  }

  /**
   * ✅ Método getToken
   */
  getToken(): string | null {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem(this.TOKEN_KEY);
  }

  /**
   * ✅ Método setRefreshToken
   */
  setRefreshToken(token: string | null): void {
    if (typeof window === 'undefined') return;
    
    if (token) {
      localStorage.setItem(this.REFRESH_TOKEN_KEY, token);
    } else {
      localStorage.removeItem(this.REFRESH_TOKEN_KEY);
    }
  }

  /**
   * ✅ Método getRefreshToken
   */
  getRefreshToken(): string | null {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem(this.REFRESH_TOKEN_KEY);
  }

  /**
   * ✅ Método setUser
   */
  setUser(user: User | null): void {
    if (typeof window === 'undefined') return;
    
    if (user) {
      localStorage.setItem(this.USER_KEY, JSON.stringify(user));
    } else {
      localStorage.removeItem(this.USER_KEY);
    }
  }

  /**
   * ✅ Método getUser
   */
  getUser(): User | null {
    if (typeof window === 'undefined') return null;
    
    const userData = localStorage.getItem(this.USER_KEY);
    if (!userData) return null;
    
    try {
      return JSON.parse(userData);
    } catch (error) {
      console.error('Error parsing user data:', error);
      return null;
    }
  }

  /**
   * ✅ Método login - INTEGRADO COM BACKEND
   */
  async login(credentials: LoginCredentials): Promise<LoginResponse> {
    try {
      const response = await fetch(`${this.API_BASE}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(credentials),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.message || `HTTP ${response.status}: ${response.statusText}`);
      }

      const data: LoginResponse = await response.json();
      
      // ✅ Salvar tokens e usuário automaticamente
      this.setToken(data.data.access_token);
      if (data.data.refresh_token) {
        this.setRefreshToken(data.data.refresh_token);
      }
      this.setUser(data.data.user);

      return data;
    } catch (error) {
      console.error('AuthService Login Error:', error);
      throw error;
    }
  }

  /**
   * ✅ Método logout
   */
  async logout(): Promise<void> {
    try {
      const token = this.getToken();
      if (token) {
        // Tentar fazer logout no backend
        await fetch(`${this.API_BASE}/auth/logout`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        }).catch(() => {
          // Ignorar erros de logout no backend
        });
      }
    } finally {
      // Sempre limpar dados locais
      this.setToken(null);
      this.setRefreshToken(null);
      this.setUser(null);
    }
  }

  /**
   * ✅ Método isAuthenticated
   */
  isAuthenticated(): boolean {
    return !!this.getToken();
  }

  /**
   * ✅ Método para fazer requests autenticadas
   */
  async authenticatedRequest(endpoint: string, options: RequestInit = {}): Promise<Response> {
    const token = this.getToken();
    
    if (!token) {
      throw new Error('No authentication token available');
    }

    const url = endpoint.startsWith('http') ? endpoint : `${this.API_BASE}${endpoint}`;
    
    const headers = {
      ...options.headers,
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    };

    return fetch(url, {
      ...options,
      headers,
    });
  }

  /**
   * ✅ Método para verificar se o usuário é válido
   */
  async verifyUser(): Promise<User | null> {
    try {
      const response = await this.authenticatedRequest('/users/me');
      
      if (!response.ok) {
        throw new Error('User verification failed');
      }

      const userData = await response.json();
      this.setUser(userData);
      return userData;
    } catch (error) {
      console.error('User verification error:', error);
      // Limpar dados inválidos
      this.logout();
      return null;
    }
  }

  /**
   * ✅ Método para obter lista de LLMs (exemplo de uso)
   */
  async getLLMs(): Promise<any> {
    try {
      const response = await this.authenticatedRequest('/llms/');
      
      if (!response.ok) {
        throw new Error('Failed to fetch LLMs');
      }

      return await response.json();
    } catch (error) {
      console.error('Get LLMs error:', error);
      throw error;
    }
  }

  /**
   * ✅ Método para criar workflow (exemplo de uso)
   */
  async createWorkflow(workflowData: any): Promise<any> {
    try {
      const response = await this.authenticatedRequest('/workflows/', {
        method: 'POST',
        body: JSON.stringify(workflowData),
      });
      
      if (!response.ok) {
        throw new Error('Failed to create workflow');
      }

      return await response.json();
    } catch (error) {
      console.error('Create workflow error:', error);
      throw error;
    }
  }
}

// ✅ Exportar instância singleton
export const authService = new AuthService();
export default authService;

// ✅ Exportar tipos para uso em outros arquivos
export type { LoginCredentials, LoginResponse, User, AuthTokens };
