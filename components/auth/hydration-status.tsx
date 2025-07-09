/**
 * HydrationStatus - Componente para mostrar o status da hidratação
 * Útil para debug e monitoramento
 */

'use client';

import { useAuth } from '@/context/auth-context';
import { HydrationState } from '@/lib/services/auth-hydration';

interface HydrationStatusProps {
  showDetails?: boolean;
  className?: string;
}

export function HydrationStatus({ showDetails = false, className = '' }: HydrationStatusProps) {
  const { hydrationState, loading, error, retryHydration } = useAuth();

  const getStatusColor = (state: HydrationState): string => {
    switch (state) {
      case HydrationState.SUCCESS:
        return '#28a745';
      case HydrationState.FAILED:
        return '#dc3545';
      case HydrationState.LOADING:
        return '#ffc107';
      case HydrationState.TIMEOUT:
        return '#fd7e14';
      default:
        return '#6c757d';
    }
  };

  const getStatusText = (state: HydrationState): string => {
    switch (state) {
      case HydrationState.SUCCESS:
        return 'Sucesso';
      case HydrationState.FAILED:
        return 'Falha';
      case HydrationState.LOADING:
        return 'Carregando...';
      case HydrationState.TIMEOUT:
        return 'Timeout';
      case HydrationState.PENDING:
        return 'Aguardando';
      default:
        return 'Desconhecido';
    }
  };

  const getStatusIcon = (state: HydrationState): string => {
    switch (state) {
      case HydrationState.SUCCESS:
        return '✅';
      case HydrationState.FAILED:
        return '❌';
      case HydrationState.LOADING:
        return '⏳';
      case HydrationState.TIMEOUT:
        return '⏰';
      case HydrationState.PENDING:
        return '⏸️';
      default:
        return '❓';
    }
  };

  if (!showDetails && hydrationState === HydrationState.SUCCESS) {
    return null;
  }

  return (
    <div className={`hydration-status ${className}`}>
      <div className="status-header">
        <span className="status-icon">{getStatusIcon(hydrationState)}</span>
        <span className="status-text" style={{ color: getStatusColor(hydrationState) }}>
          Hidratação: {getStatusText(hydrationState)}
        </span>
        {loading && <span className="loading-spinner">🔄</span>}
      </div>

      {error && (
        <div className="error-message">
          <span className="error-icon">⚠️</span>
          <span className="error-text">{error}</span>
        </div>
      )}

      {(hydrationState === HydrationState.FAILED || hydrationState === HydrationState.TIMEOUT) && (
        <div className="retry-section">
          <button
            onClick={retryHydration}
            disabled={loading}
            className="retry-button"
          >
            {loading ? 'Tentando...' : 'Tentar Novamente'}
          </button>
        </div>
      )}

      {showDetails && (
        <div className="status-details">
          <div className="detail-item">
            <strong>Estado:</strong> {hydrationState}
          </div>
          <div className="detail-item">
            <strong>Loading:</strong> {loading ? 'Sim' : 'Não'}
          </div>
          <div className="detail-item">
            <strong>Erro:</strong> {error || 'Nenhum'}
          </div>
          <div className="detail-item">
            <strong>Timestamp:</strong> {new Date().toLocaleTimeString()}
          </div>
        </div>
      )}

      <style jsx>{`
        .hydration-status {
          background-color: #f8f9fa;
          border: 1px solid #dee2e6;
          border-radius: 4px;
          padding: 1rem;
          margin-bottom: 1rem;
          font-size: 0.9rem;
        }

        .status-header {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          margin-bottom: 0.5rem;
        }

        .status-icon {
          font-size: 1.2rem;
        }

        .status-text {
          font-weight: 500;
        }

        .loading-spinner {
          animation: spin 1s linear infinite;
        }

        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }

        .error-message {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          background-color: #f8d7da;
          color: #721c24;
          padding: 0.5rem;
          border-radius: 4px;
          margin-bottom: 0.5rem;
        }

        .error-icon {
          font-size: 1.1rem;
        }

        .error-text {
          font-size: 0.85rem;
        }

        .retry-section {
          margin-top: 0.5rem;
        }

        .retry-button {
          background-color: #007bff;
          color: white;
          border: none;
          padding: 0.5rem 1rem;
          border-radius: 4px;
          cursor: pointer;
          font-size: 0.85rem;
          font-weight: 500;
          transition: background-color 0.2s;
        }

        .retry-button:hover:not(:disabled) {
          background-color: #0056b3;
        }

        .retry-button:disabled {
          background-color: #6c757d;
          cursor: not-allowed;
        }

        .status-details {
          background-color: white;
          border: 1px solid #dee2e6;
          border-radius: 4px;
          padding: 0.5rem;
          margin-top: 0.5rem;
        }

        .detail-item {
          margin-bottom: 0.25rem;
          font-size: 0.8rem;
        }

        .detail-item:last-child {
          margin-bottom: 0;
        }

        .detail-item strong {
          color: #495057;
        }
      `}</style>
    </div>
  );
}

/**
 * ✅ Componente compacto para mostrar apenas o status
 */
export function HydrationStatusCompact() {
  const { hydrationState, loading } = useAuth();

  if (hydrationState === HydrationState.SUCCESS && !loading) {
    return null;
  }

  return (
    <div className="hydration-status-compact">
      <span className="status-indicator">
        {loading ? '🔄' : hydrationState === HydrationState.SUCCESS ? '✅' : '❌'}
      </span>
      <span className="status-text">
        {loading ? 'Carregando...' : hydrationState === HydrationState.SUCCESS ? 'OK' : 'Erro'}
      </span>

      <style jsx>{`
        .hydration-status-compact {
          display: flex;
          align-items: center;
          gap: 0.25rem;
          padding: 0.25rem 0.5rem;
          background-color: #f8f9fa;
          border-radius: 12px;
          font-size: 0.75rem;
          color: #6c757d;
        }

        .status-indicator {
          font-size: 0.9rem;
        }

        .status-text {
          font-weight: 500;
        }
      `}</style>
    </div>
  );
}

export default HydrationStatus;
