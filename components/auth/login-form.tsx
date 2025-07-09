/**
 * LoginForm - Componente de login corrigido
 * Integra com AuthService sem erros
 */

'use client';

import { useState, FormEvent } from 'react';
import { useLogin } from '@/hooks/useAuth';
import { type LoginCredentials } from '@/lib/services/auth';

interface LoginFormProps {
  onSuccess?: () => void;
  onError?: (error: string) => void;
}

export function LoginForm({ onSuccess, onError }: LoginFormProps) {
  const [credentials, setCredentials] = useState<LoginCredentials>({
    email: '',
    password: ''
  });
  const [localError, setLocalError] = useState('');
  
  const { login, loading, error } = useLogin();

  /**
   * ✅ Handle form submission - CORRIGIDO
   */
  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLocalError('');

    // Validação básica
    if (!credentials.email || !credentials.password) {
      const errorMsg = 'Por favor, preencha todos os campos';
      setLocalError(errorMsg);
      onError?.(errorMsg);
      return;
    }

    try {
      await login(credentials);
      onSuccess?.();
    } catch (error: any) {
      const errorMsg = error.message || 'Erro ao fazer login. Verifique suas credenciais.';
      setLocalError(errorMsg);
      onError?.(errorMsg);
    }
  };

  const displayError = localError || error;

  return (
    <div className="login-form-container">
      <form onSubmit={handleSubmit} className="login-form">
        <div className="form-header">
          <h2>Login</h2>
          <p>Faça login para acessar o SynapScale</p>
        </div>

        <div className="form-group">
          <label htmlFor="email">Email</label>
          <input
            id="email"
            type="email"
            placeholder="seu@email.com"
            value={credentials.email}
            onChange={(e) => setCredentials(prev => ({ ...prev, email: e.target.value }))}
            required
            disabled={loading}
            className="form-input"
          />
        </div>

        <div className="form-group">
          <label htmlFor="password">Senha</label>
          <input
            id="password"
            type="password"
            placeholder="Sua senha"
            value={credentials.password}
            onChange={(e) => setCredentials(prev => ({ ...prev, password: e.target.value }))}
            required
            disabled={loading}
            className="form-input"
          />
        </div>

        {displayError && (
          <div className="error-message" role="alert">
            {displayError}
          </div>
        )}

        <button
          type="submit"
          disabled={loading}
          className="login-button"
        >
          {loading ? 'Fazendo login...' : 'Entrar'}
        </button>
      </form>

      <style jsx>{`
        .login-form-container {
          max-width: 400px;
          margin: 0 auto;
          padding: 2rem;
        }

        .login-form {
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }

        .form-header {
          text-align: center;
          margin-bottom: 2rem;
        }

        .form-header h2 {
          color: #333;
          margin-bottom: 0.5rem;
        }

        .form-header p {
          color: #666;
          font-size: 0.9rem;
        }

        .form-group {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
        }

        .form-group label {
          font-weight: 500;
          color: #333;
        }

        .form-input {
          padding: 0.75rem;
          border: 1px solid #ddd;
          border-radius: 4px;
          font-size: 1rem;
          transition: border-color 0.2s;
        }

        .form-input:focus {
          outline: none;
          border-color: #007bff;
          box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
        }

        .form-input:disabled {
          background-color: #f8f9fa;
          cursor: not-allowed;
        }

        .error-message {
          background-color: #f8d7da;
          color: #721c24;
          padding: 0.75rem;
          border-radius: 4px;
          border: 1px solid #f5c6cb;
        }

        .login-button {
          background-color: #007bff;
          color: white;
          padding: 0.75rem;
          border: none;
          border-radius: 4px;
          font-size: 1rem;
          font-weight: 500;
          cursor: pointer;
          transition: background-color 0.2s;
        }

        .login-button:hover:not(:disabled) {
          background-color: #0056b3;
        }

        .login-button:disabled {
          background-color: #6c757d;
          cursor: not-allowed;
        }
      `}</style>
    </div>
  );
}

/**
 * ✅ Componente de teste com credenciais padrão
 */
export function LoginFormWithDefaults() {
  const [credentials, setCredentials] = useState<LoginCredentials>({
    email: 'joaovictor@liderimobiliaria.com.br',
    password: '@Teste123'
  });
  
  const { login, loading, error } = useLogin();

  const handleQuickLogin = async () => {
    try {
      await login(credentials);
      alert('Login realizado com sucesso!');
    } catch (error: any) {
      alert(`Erro: ${error.message}`);
    }
  };

  return (
    <div className="quick-login">
      <h3>Teste Rápido</h3>
      <p>Credenciais pré-preenchidas para teste</p>
      
      <div className="credentials-display">
        <p><strong>Email:</strong> {credentials.email}</p>
        <p><strong>Senha:</strong> {credentials.password}</p>
      </div>
      
      <button 
        onClick={handleQuickLogin}
        disabled={loading}
        className="quick-login-button"
      >
        {loading ? 'Fazendo login...' : 'Login Rápido'}
      </button>
      
      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      <style jsx>{`
        .quick-login {
          max-width: 400px;
          margin: 2rem auto;
          padding: 1rem;
          border: 1px solid #ddd;
          border-radius: 4px;
          background-color: #f8f9fa;
        }
        
        .credentials-display {
          background-color: white;
          padding: 1rem;
          border-radius: 4px;
          margin: 1rem 0;
          font-family: monospace;
        }
        
        .quick-login-button {
          width: 100%;
          padding: 0.75rem;
          background-color: #28a745;
          color: white;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          font-weight: 500;
        }
        
        .quick-login-button:hover:not(:disabled) {
          background-color: #218838;
        }
        
        .quick-login-button:disabled {
          background-color: #6c757d;
          cursor: not-allowed;
        }
        
        .error-message {
          background-color: #f8d7da;
          color: #721c24;
          padding: 0.75rem;
          border-radius: 4px;
          margin-top: 1rem;
        }
      `}</style>
    </div>
  );
}

export default LoginForm;
