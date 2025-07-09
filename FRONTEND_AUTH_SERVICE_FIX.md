# 🚨 Frontend Auth Service Fix

## Problema Identificado

O erro indica que `authService.setToken` não é uma função no frontend:

```
Error: _lib_services_auth__WEBPACK_IMPORTED_MODULE_2__.authService.setToken is not a function
```

## 🔧 Solução: Implementar AuthService no Frontend

### 1. Criar/Corrigir `lib/services/auth.ts`

```typescript
// lib/services/auth.ts
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
  data: {
    access_token: string;
    refresh_token: string | null;
    user: {
      id: string;
      email: string;
      username: string;
      tenant_id: string;
    };
  };
}

class AuthService {
  private readonly API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000/api/v1';
  private readonly TOKEN_KEY = 'auth_token';
  private readonly REFRESH_TOKEN_KEY = 'refresh_token';

  // ✅ Método setToken que estava faltando
  setToken(token: string | null): void {
    if (token) {
      localStorage.setItem(this.TOKEN_KEY, token);
    } else {
      localStorage.removeItem(this.TOKEN_KEY);
    }
  }

  // ✅ Método getToken
  getToken(): string | null {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem(this.TOKEN_KEY);
  }

  // ✅ Método setRefreshToken
  setRefreshToken(token: string | null): void {
    if (token) {
      localStorage.setItem(this.REFRESH_TOKEN_KEY, token);
    } else {
      localStorage.removeItem(this.REFRESH_TOKEN_KEY);
    }
  }

  // ✅ Método getRefreshToken
  getRefreshToken(): string | null {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem(this.REFRESH_TOKEN_KEY);
  }

  // ✅ Método login
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
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data: LoginResponse = await response.json();
      
      // Salvar tokens automaticamente
      this.setToken(data.data.access_token);
      if (data.data.refresh_token) {
        this.setRefreshToken(data.data.refresh_token);
      }

      return data;
    } catch (error) {
      console.error('Auth Service Login Error:', error);
      throw error;
    }
  }

  // ✅ Método logout
  logout(): void {
    this.setToken(null);
    this.setRefreshToken(null);
  }

  // ✅ Método isAuthenticated
  isAuthenticated(): boolean {
    return !!this.getToken();
  }

  // ✅ Método para fazer requests autenticadas
  async authenticatedRequest(url: string, options: RequestInit = {}): Promise<Response> {
    const token = this.getToken();
    
    if (!token) {
      throw new Error('No authentication token available');
    }

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
}

// ✅ Exportar instância singleton
export const authService = new AuthService();
export default authService;
```

### 2. Corrigir Context de Autenticação

```typescript
// context/auth-context.tsx
import { createContext, useContext, useCallback, useState, useEffect } from 'react';
import { authService } from '@/lib/services/auth';

interface AuthContextType {
  user: any;
  login: (credentials: any) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const login = useCallback(async (credentials: any) => {
    try {
      setLoading(true);
      const response = await authService.login(credentials);
      setUser(response.data.user);
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  }, []);

  const logout = useCallback(() => {
    authService.logout();
    setUser(null);
  }, []);

  // ✅ Método de sincronização corrigido
  const syncTokensWithDebouncing = useCallback(async () => {
    try {
      const token = authService.getToken();
      if (token) {
        // Verificar se o token é válido
        const response = await authService.authenticatedRequest('/users/me');
        if (response.ok) {
          const userData = await response.json();
          setUser(userData);
        } else {
          // Token inválido, fazer logout
          logout();
        }
      }
    } catch (error) {
      console.error('Sync tokens error:', error);
      logout();
    }
  }, [logout]);

  useEffect(() => {
    syncTokensWithDebouncing();
  }, [syncTokensWithDebouncing]);

  const value = {
    user,
    login,
    logout,
    isAuthenticated: !!user,
    loading,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
```

### 3. Hook useAuth Corrigido

```typescript
// hooks/useAuth.ts
import { useAuth as useAuthContext } from '@/context/auth-context';

export const useLogin = () => {
  const { login } = useAuthContext();
  
  return {
    login: async (credentials: any) => {
      try {
        await login(credentials);
      } catch (error) {
        console.error('Login hook error:', error);
        throw error;
      }
    }
  };
};

export const useAuth = useAuthContext;
```

### 4. Componente de Login Corrigido

```typescript
// components/auth/login-form.tsx
import { useState } from 'react';
import { useLogin } from '@/hooks/useAuth';

export function LoginForm() {
  const [credentials, setCredentials] = useState({
    email: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const { login } = useLogin();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await login(credentials);
      // Redirect ou atualizar UI
    } catch (error) {
      setError('Erro ao fazer login. Verifique suas credenciais.');
      console.error('Login error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <input
          type="email"
          placeholder="Email"
          value={credentials.email}
          onChange={(e) => setCredentials(prev => ({ ...prev, email: e.target.value }))}
          required
        />
      </div>
      <div>
        <input
          type="password"
          placeholder="Password"
          value={credentials.password}
          onChange={(e) => setCredentials(prev => ({ ...prev, password: e.target.value }))}
          required
        />
      </div>
      {error && <div className="error">{error}</div>}
      <button type="submit" disabled={loading}>
        {loading ? 'Fazendo login...' : 'Login'}
      </button>
    </form>
  );
}
```

## 🧪 Teste da Solução

### 1. Testar AuthService

```typescript
// Teste em console do browser
import { authService } from '@/lib/services/auth';

// Testar login
const testLogin = async () => {
  try {
    const result = await authService.login({
      email: 'joaovictor@liderimobiliaria.com.br',
      password: '@Teste123'
    });
    console.log('Login success:', result);
  } catch (error) {
    console.error('Login error:', error);
  }
};

testLogin();
```

### 2. Verificar Tokens

```typescript
// Verificar se tokens foram salvos
console.log('Token:', authService.getToken());
console.log('Refresh Token:', authService.getRefreshToken());
console.log('Is Authenticated:', authService.isAuthenticated());
```

## 🔧 Configuração do Ambiente

### 1. Variáveis de Ambiente (.env.local)

```env
NEXT_PUBLIC_API_BASE=http://localhost:8000/api/v1
NEXT_PUBLIC_APP_ENV=development
```

### 2. Package.json Dependencies

```json
{
  "dependencies": {
    "next": "^14.0.0",
    "react": "^18.0.0",
    "react-dom": "^18.0.0",
    "typescript": "^5.0.0"
  }
}
```

## 🚨 Checklist de Verificação

- [ ] `authService.setToken` está definido como método
- [ ] `authService.getToken` retorna token do localStorage
- [ ] `authService.login` salva tokens automaticamente
- [ ] Context de autenticação usa authService corretamente
- [ ] Hook useAuth não tem erros de importação
- [ ] Componente de login chama login corretamente
- [ ] Variáveis de ambiente estão configuradas
- [ ] Backend está rodando em localhost:8000

## 🎯 Teste Final

```bash
# 1. Verificar se backend está rodando
curl http://localhost:8000/health

# 2. Testar login direto
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "joaovictor@liderimobiliaria.com.br", "password": "@Teste123"}'

# 3. Verificar se frontend consegue fazer login
# (usar o componente de login na aplicação)
```

Esta solução resolve o problema do `authService.setToken is not a function` implementando todos os métodos necessários no serviço de autenticação do frontend.
