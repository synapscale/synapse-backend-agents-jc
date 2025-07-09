/**
 * LoadingSpinner - Componente reutilizável para loading
 * Usado em ProtectedRoute e outros componentes
 */

'use client';

interface LoadingSpinnerProps {
  size?: 'small' | 'medium' | 'large';
  color?: string;
  message?: string;
  className?: string;
}

export function LoadingSpinner({
  size = 'medium',
  color = '#007bff',
  message,
  className = ''
}: LoadingSpinnerProps) {
  const sizeMap = {
    small: '20px',
    medium: '40px',
    large: '60px'
  };

  const spinnerSize = sizeMap[size];

  return (
    <div className={`loading-spinner ${className}`}>
      <div className="spinner" style={{ width: spinnerSize, height: spinnerSize, borderColor: `${color}30`, borderTopColor: color }}>
      </div>
      {message && <p className="loading-message">{message}</p>}
      
      <style jsx>{`
        .loading-spinner {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          gap: 1rem;
        }

        .spinner {
          border: 4px solid;
          border-radius: 50%;
          animation: spin 1s linear infinite;
        }

        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }

        .loading-message {
          color: #666;
          margin: 0;
          font-size: 0.9rem;
        }
      `}</style>
    </div>
  );
}

/**
 * ✅ Componente de página de loading
 */
export function LoadingPage({ message = 'Carregando...' }: { message?: string }) {
  return (
    <div className="loading-page">
      <LoadingSpinner size="large" message={message} />
      
      <style jsx>{`
        .loading-page {
          display: flex;
          align-items: center;
          justify-content: center;
          min-height: 100vh;
          background-color: #f8f9fa;
        }
      `}</style>
    </div>
  );
}

/**
 * ✅ Componente de loading inline
 */
export function InlineLoading({ message = 'Carregando...' }: { message?: string }) {
  return (
    <div className="inline-loading">
      <LoadingSpinner size="small" />
      <span>{message}</span>
      
      <style jsx>{`
        .inline-loading {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          padding: 0.5rem 0;
        }
      `}</style>
    </div>
  );
}

export default LoadingSpinner;
