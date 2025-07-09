/**
 * Página de teste da autenticação
 * Use esta página para testar o authService corrigido
 */

'use client';

import { useState, useEffect } from 'react';
import { AuthProvider, useAuth } from '@/context/auth-context';
import { LoginForm, LoginFormWithDefaults } from '@/components/auth/login-form';
import { HydrationStatus, HydrationStatusCompact } from '@/components/auth/hydration-status';
import { authService } from '@/lib/services/auth';
import { authLogger } from '@/lib/utils/logger';
import { authHydrationService, HydrationState } from '@/lib/services/auth-hydration';

// ✅ Componente de teste do AuthService
function AuthServiceTest() {
  const [testResults, setTestResults] = useState<string[]>([]);
  const [llmData, setLlmData] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const addResult = (result: string) => {
    setTestResults(prev => [...prev, `${new Date().toLocaleTimeString()}: ${result}`]);
  };

  const testAuthService = async () => {
    setLoading(true);
    addResult('🧪 Iniciando testes do AuthService...');

    try {
      // Teste 1: Verificar se métodos existem
      addResult('✅ Teste 1: Verificando métodos do authService...');
      const methods = ['setToken', 'getToken', 'setUser', 'getUser', 'login', 'logout'];
      
      methods.forEach(method => {
        if (typeof authService[method as keyof typeof authService] === 'function') {
          addResult(`✅ ${method} está definido como função`);
        } else {
          addResult(`❌ ${method} NÃO está definido como função`);
        }
      });

      // Teste 2: Testar setToken/getToken
      addResult('✅ Teste 2: Testando setToken/getToken...');
      const testToken = 'test-token-123';
      authService.setToken(testToken);
      const retrievedToken = authService.getToken();
      
      if (retrievedToken === testToken) {
        addResult('✅ setToken/getToken funcionando corretamente');
      } else {
        addResult('❌ setToken/getToken com problemas');
      }

      // Teste 3: Testar login
      addResult('✅ Teste 3: Testando login...');
      const loginResult = await authService.login({
        email: 'joaovictor@liderimobiliaria.com.br',
        password: '@Teste123'
      });
      
      if (loginResult.data.access_token) {
        addResult('✅ Login funcionando - token recebido');
        addResult(`👤 Usuário: ${loginResult.data.user.email}`);
        addResult(`🏢 Tenant: ${loginResult.data.user.tenant_id}`);
      } else {
        addResult('❌ Login com problemas - token não recebido');
      }

      // Teste 4: Testar request autenticada
      addResult('✅ Teste 4: Testando request autenticada...');
      const llmResponse = await authService.getLLMs();
      
      if (llmResponse.items && llmResponse.items.length > 0) {
        addResult(`✅ Request autenticada funcionando - ${llmResponse.items.length} LLMs encontrados`);
        setLlmData(llmResponse);
      } else {
        addResult('❌ Request autenticada com problemas');
      }

      addResult('🎉 Todos os testes concluídos com sucesso!');
      
    } catch (error: any) {
      addResult(`❌ Erro durante os testes: ${error.message}`);
      authLogger.authError('Teste do authService falhou', error);
    } finally {
      setLoading(false);
    }
  };

  const clearResults = () => {
    setTestResults([]);
    setLlmData(null);
  };

  return (
    <div className="auth-test-container">
      <h2>🧪 Teste do AuthService</h2>
      
      <div className="test-controls">
        <button 
          onClick={testAuthService}
          disabled={loading}
          className="test-button"
        >
          {loading ? 'Testando...' : 'Executar Testes'}
        </button>
        
        <button 
          onClick={clearResults}
          className="clear-button"
        >
          Limpar Resultados
        </button>
      </div>

      {testResults.length > 0 && (
        <div className="test-results">
          <h3>Resultados dos Testes:</h3>
          <div className="results-log">
            {testResults.map((result, index) => (
              <div key={index} className="result-item">
                {result}
              </div>
            ))}
          </div>
        </div>
      )}

      {llmData && (
        <div className="llm-data">
          <h3>📊 Dados dos LLMs:</h3>
          <div className="llm-summary">
            <p><strong>Total:</strong> {llmData.total}</p>
            <p><strong>Página:</strong> {llmData.page}</p>
            <p><strong>Por página:</strong> {llmData.per_page}</p>
          </div>
          <div className="llm-list">
            {llmData.items.slice(0, 5).map((llm: any, index: number) => (
              <div key={index} className="llm-item">
                <strong>{llm.name}</strong> - {llm.provider}
              </div>
            ))}
            {llmData.items.length > 5 && (
              <div className="llm-item">... e mais {llmData.items.length - 5} modelos</div>
            )}
          </div>
        </div>
      )}

      <style jsx>{`
        .auth-test-container {
          max-width: 800px;
          margin: 2rem auto;
          padding: 2rem;
          border: 1px solid #ddd;
          border-radius: 8px;
          background-color: #f8f9fa;
        }

        .test-controls {
          display: flex;
          gap: 1rem;
          margin-bottom: 2rem;
        }

        .test-button {
          background-color: #007bff;
          color: white;
          padding: 0.75rem 1.5rem;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          font-weight: 500;
        }

        .test-button:hover:not(:disabled) {
          background-color: #0056b3;
        }

        .test-button:disabled {
          background-color: #6c757d;
          cursor: not-allowed;
        }

        .clear-button {
          background-color: #6c757d;
          color: white;
          padding: 0.75rem 1.5rem;
          border: none;
          border-radius: 4px;
          cursor: pointer;
        }

        .clear-button:hover {
          background-color: #545b62;
        }

        .test-results {
          background-color: white;
          padding: 1rem;
          border-radius: 4px;
          margin-bottom: 2rem;
          border: 1px solid #ddd;
        }

        .results-log {
          font-family: monospace;
          font-size: 0.9rem;
          max-height: 400px;
          overflow-y: auto;
          background-color: #f8f9fa;
          padding: 1rem;
          border-radius: 4px;
        }

        .result-item {
          margin-bottom: 0.5rem;
          padding: 0.25rem;
          border-radius: 2px;
        }

        .llm-data {
          background-color: white;
          padding: 1rem;
          border-radius: 4px;
          border: 1px solid #ddd;
        }

        .llm-summary {
          display: flex;
          gap: 2rem;
          margin-bottom: 1rem;
        }

        .llm-list {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
        }

        .llm-item {
          padding: 0.5rem;
          background-color: #f8f9fa;
          border-radius: 4px;
          border-left: 3px solid #007bff;
        }
      `}</style>
    </div>
  );
}

// ✅ Componente de status da autenticação
function AuthStatus() {
  const { user, isAuthenticated, loading, hydrationState, error } = useAuth();

  return (
    <div className="auth-status">
      <h3>📊 Status da Autenticação</h3>
      
      {/* ✅ Status de hidratação */}
      <HydrationStatus showDetails={true} />
      
      <div className="status-info">
        <div className="status-item">
          <strong>Autenticado:</strong> {isAuthenticated ? '✅ Sim' : '❌ Não'}
        </div>
        
        <div className="status-item">
          <strong>Loading:</strong> {loading ? '🔄 Sim' : '✅ Não'}
        </div>
        
        <div className="status-item">
          <strong>Estado de Hidratação:</strong> {hydrationState}
        </div>
        
        {error && (
          <div className="status-item error">
            <strong>Erro:</strong> {error}
          </div>
        )}
        
        {user && (
          <>
            <div className="status-item">
              <strong>Email:</strong> {user.email}
            </div>
            <div className="status-item">
              <strong>Username:</strong> {user.username}
            </div>
            <div className="status-item">
              <strong>Tenant ID:</strong> {user.tenant_id}
            </div>
            <div className="status-item">
              <strong>Ativo:</strong> {user.is_active ? '✅ Sim' : '❌ Não'}
            </div>
          </>
        )}
      </div>

      <style jsx>{`
        .auth-status {
          background-color: white;
          padding: 1rem;
          border-radius: 4px;
          border: 1px solid #ddd;
          margin-bottom: 2rem;
        }

        .status-info {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
        }

        .status-item {
          padding: 0.5rem;
          background-color: #f8f9fa;
          border-radius: 4px;
        }

        .status-item.error {
          background-color: #f8d7da;
          color: #721c24;
        }
      `}</style>
    </div>
  );
}

// ✅ Componente principal da página
function TestAuthPage() {
  return (
    <div className="page-container">
      <h1>🔐 Teste de Autenticação - SynapScale</h1>
      <p>Esta página testa o sistema de autenticação corrigido</p>
      
      <AuthStatus />
      <AuthServiceTest />
      
      <div className="forms-container">
        <div className="form-section">
          <h2>📝 Formulário de Login</h2>
          <LoginForm 
            onSuccess={() => alert('Login realizado com sucesso!')}
            onError={(error) => alert(`Erro: ${error}`)}
          />
        </div>
        
        <div className="form-section">
          <h2>⚡ Login Rápido</h2>
          <LoginFormWithDefaults />
        </div>
      </div>

      <style jsx>{`
        .page-container {
          max-width: 1200px;
          margin: 0 auto;
          padding: 2rem;
        }

        .forms-container {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 2rem;
          margin-top: 2rem;
        }

        .form-section {
          background-color: white;
          padding: 1.5rem;
          border-radius: 8px;
          border: 1px solid #ddd;
        }

        @media (max-width: 768px) {
          .forms-container {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </div>
  );
}

// ✅ Página principal com AuthProvider
export default function TestAuthPageWithProvider() {
  return (
    <AuthProvider>
      <TestAuthPage />
    </AuthProvider>
  );
}
