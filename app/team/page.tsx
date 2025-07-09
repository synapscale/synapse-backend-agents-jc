/**
 * Team Page - Página da equipe protegida
 * Usa dados reais da API e banco oficial
 */

'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/context/auth-context';
import { ProtectedRoute } from '@/components/auth/protected-route';
import { LoadingSpinner } from '@/components/common/loading-spinner';
import { HydrationStatusCompact } from '@/components/auth/hydration-status';
import { authService } from '@/lib/services/auth';
import { authLogger } from '@/lib/utils/logger';

interface TeamMember {
  id: string;
  email: string;
  username: string;
  is_active: boolean;
  is_verified: boolean;
  tenant_id: string;
  created_at: string;
  updated_at: string;
}

interface WorkspaceData {
  id: string;
  name: string;
  tenant_id: string;
  is_active: boolean;
  created_at: string;
}

interface TenantData {
  id: string;
  name: string;
  is_active: boolean;
  created_at: string;
}

function TeamPageContent() {
  const { user, isAuthenticated } = useAuth();
  const [teamMembers, setTeamMembers] = useState<TeamMember[]>([]);
  const [workspaces, setWorkspaces] = useState<WorkspaceData[]>([]);
  const [tenantInfo, setTenantInfo] = useState<TenantData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  /**
   * ✅ Buscar dados reais da API
   */
  useEffect(() => {
    const fetchTeamData = async () => {
      if (!isAuthenticated) return;

      try {
        setLoading(true);
        setError(null);

        authLogger.info('Buscando dados da equipe da API');

        // Buscar informações do tenant atual
        try {
          const tenantResponse = await authService.authenticatedRequest('/tenants/me');
          if (tenantResponse.ok) {
            const tenantData = await tenantResponse.json();
            setTenantInfo(tenantData);
            authLogger.info('Dados do tenant carregados', { tenantName: tenantData.name });
          }
        } catch (error) {
          authLogger.warn('Erro ao buscar dados do tenant', error);
        }

        // Buscar workspaces do tenant
        try {
          const workspaceResponse = await authService.authenticatedRequest('/workspaces/');
          if (workspaceResponse.ok) {
            const workspaceData = await workspaceResponse.json();
            setWorkspaces(workspaceData.items || []);
            authLogger.info('Workspaces carregados', { count: workspaceData.items?.length || 0 });
          }
        } catch (error) {
          authLogger.warn('Erro ao buscar workspaces', error);
        }

        // Buscar usuários do tenant (se endpoint existir)
        try {
          const usersResponse = await authService.authenticatedRequest('/users/');
          if (usersResponse.ok) {
            const usersData = await usersResponse.json();
            setTeamMembers(usersData.items || []);
            authLogger.info('Membros da equipe carregados', { count: usersData.items?.length || 0 });
          }
        } catch (error) {
          // Se não houver endpoint de usuários, usar apenas o usuário atual
          authLogger.info('Endpoint de usuários não disponível, usando usuário atual');
          if (user) {
            setTeamMembers([user]);
          }
        }

      } catch (error: any) {
        const errorMessage = error.message || 'Erro ao carregar dados da equipe';
        setError(errorMessage);
        authLogger.authError('Erro ao buscar dados da equipe', error);
      } finally {
        setLoading(false);
      }
    };

    fetchTeamData();
  }, [isAuthenticated, user]);

  /**
   * ✅ Buscar estatísticas reais
   */
  const [stats, setStats] = useState({
    totalWorkflows: 0,
    totalLLMs: 0,
    totalExecutions: 0
  });

  useEffect(() => {
    const fetchStats = async () => {
      if (!isAuthenticated) return;

      try {
        // Buscar workflows
        const workflowsResponse = await authService.authenticatedRequest('/workflows/');
        if (workflowsResponse.ok) {
          const workflowsData = await workflowsResponse.json();
          setStats(prev => ({ ...prev, totalWorkflows: workflowsData.total || 0 }));
        }

        // Buscar LLMs
        const llmsResponse = await authService.authenticatedRequest('/llms/');
        if (llmsResponse.ok) {
          const llmsData = await llmsResponse.json();
          setStats(prev => ({ ...prev, totalLLMs: llmsData.total || 0 }));
        }

        // Buscar execuções
        const executionsResponse = await authService.authenticatedRequest('/executions/');
        if (executionsResponse.ok) {
          const executionsData = await executionsResponse.json();
          setStats(prev => ({ ...prev, totalExecutions: executionsData.total || 0 }));
        }

      } catch (error) {
        authLogger.warn('Erro ao buscar estatísticas', error);
      }
    };

    fetchStats();
  }, [isAuthenticated]);

  if (loading) {
    return (
      <div className="team-loading">
        <LoadingSpinner size="large" message="Carregando dados da equipe..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className="team-error">
        <h2>❌ Erro ao Carregar Dados</h2>
        <p>{error}</p>
        <button onClick={() => window.location.reload()}>
          🔄 Tentar Novamente
        </button>
      </div>
    );
  }

  return (
    <div className="team-page">
      <div className="page-header">
        <div className="header-content">
          <h1>👥 Nossa Equipe</h1>
          <p>Conheça os membros da nossa equipe</p>
        </div>
        
        <div className="header-status">
          <HydrationStatusCompact />
        </div>
      </div>

      <div className="current-user-info">
        <h2>📊 Informações do Usuário Atual</h2>
        <div className="user-card">
          <div className="user-avatar">👤</div>
          <div className="user-details">
            <h3>{user?.username || 'Usuário'}</h3>
            <p><strong>Email:</strong> {user?.email}</p>
            <p><strong>Tenant:</strong> {user?.tenant_id}</p>
            <p><strong>Status:</strong> {user?.is_active ? '✅ Ativo' : '❌ Inativo'}</p>
          </div>
        </div>
      </div>

      <div className="team-section">
        <h2>👥 Membros da Equipe</h2>
        <div className="team-grid">
          {teamMembers.map((member) => (
            <div key={member.id} className="team-card">
              <div className="member-avatar">
                {member.avatar || '👤'}
              </div>
              <div className="member-info">
                <h3>{member.name}</h3>
                <p className="member-email">{member.email}</p>
                <span className="member-role">{member.role}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="actions-section">
        <h2>🔧 Ações Disponíveis</h2>
        <div className="action-buttons">
          <button className="action-btn primary">
            👥 Adicionar Membro
          </button>
          <button className="action-btn secondary">
            📊 Relatórios
          </button>
          <button className="action-btn secondary">
            ⚙️ Configurações
          </button>
        </div>
      </div>

      <style jsx>{`
        .team-page {
          max-width: 1200px;
          margin: 0 auto;
          padding: 2rem;
        }

        .page-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 2rem;
          padding-bottom: 1rem;
          border-bottom: 1px solid #dee2e6;
        }

        .header-content h1 {
          margin: 0 0 0.5rem 0;
          color: #333;
        }

        .header-content p {
          margin: 0;
          color: #666;
        }

        .current-user-info {
          background-color: #f8f9fa;
          padding: 1.5rem;
          border-radius: 8px;
          margin-bottom: 2rem;
        }

        .current-user-info h2 {
          margin-top: 0;
          color: #333;
        }

        .user-card {
          display: flex;
          align-items: center;
          gap: 1rem;
          background-color: white;
          padding: 1rem;
          border-radius: 8px;
          border: 1px solid #dee2e6;
        }

        .user-avatar {
          font-size: 3rem;
          width: 60px;
          height: 60px;
          display: flex;
          align-items: center;
          justify-content: center;
          background-color: #e9ecef;
          border-radius: 50%;
        }

        .user-details h3 {
          margin: 0 0 0.5rem 0;
          color: #333;
        }

        .user-details p {
          margin: 0.25rem 0;
          font-size: 0.9rem;
          color: #666;
        }

        .team-section {
          margin-bottom: 2rem;
        }

        .team-section h2 {
          margin-bottom: 1rem;
          color: #333;
        }

        .team-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
          gap: 1rem;
        }

        .team-card {
          background-color: white;
          padding: 1.5rem;
          border-radius: 8px;
          border: 1px solid #dee2e6;
          transition: transform 0.2s, box-shadow 0.2s;
        }

        .team-card:hover {
          transform: translateY(-2px);
          box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }

        .member-avatar {
          font-size: 2.5rem;
          text-align: center;
          margin-bottom: 1rem;
        }

        .member-info {
          text-align: center;
        }

        .member-info h3 {
          margin: 0 0 0.5rem 0;
          color: #333;
        }

        .member-email {
          margin: 0 0 0.5rem 0;
          color: #666;
          font-size: 0.9rem;
        }

        .member-role {
          background-color: #007bff;
          color: white;
          padding: 0.25rem 0.5rem;
          border-radius: 12px;
          font-size: 0.8rem;
          font-weight: 500;
        }

        .actions-section {
          background-color: #f8f9fa;
          padding: 1.5rem;
          border-radius: 8px;
        }

        .actions-section h2 {
          margin-top: 0;
          color: #333;
        }

        .action-buttons {
          display: flex;
          gap: 1rem;
          flex-wrap: wrap;
        }

        .action-btn {
          padding: 0.75rem 1.5rem;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          font-size: 1rem;
          font-weight: 500;
          transition: background-color 0.2s;
        }

        .action-btn.primary {
          background-color: #007bff;
          color: white;
        }

        .action-btn.primary:hover {
          background-color: #0056b3;
        }

        .action-btn.secondary {
          background-color: #6c757d;
          color: white;
        }

        .action-btn.secondary:hover {
          background-color: #545b62;
        }

        @media (max-width: 768px) {
          .team-page {
            padding: 1rem;
          }

          .page-header {
            flex-direction: column;
            gap: 1rem;
            align-items: flex-start;
          }

          .user-card {
            flex-direction: column;
            text-align: center;
          }

          .action-buttons {
            flex-direction: column;
          }
        }
      `}</style>
    </div>
  );
}

/**
 * ✅ Página da equipe com ProtectedRoute corrigido
 */
export default function TeamPage() {
  return (
    <ProtectedRoute
      requireAuth={true}
      redirectTo="/login"
      fallback={
        <div className="team-fallback">
          <h2>⚠️ Erro de Autenticação</h2>
          <p>Não foi possível verificar sua autenticação. Tente novamente.</p>
          
          <style jsx>{`
            .team-fallback {
              text-align: center;
              padding: 2rem;
              background-color: #f8d7da;
              color: #721c24;
              border-radius: 8px;
              margin: 2rem;
            }
          `}</style>
        </div>
      }
    >
      <TeamPageContent />
    </ProtectedRoute>
  );
}
