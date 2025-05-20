// Tipos compartilhados para todo o ecossistema
// Implemente aqui tipos globais e use nos apps

// Exemplo de exportação de tipo compartilhado
export type BaseComponentProps = {
  className?: string;
  style?: React.CSSProperties;
  id?: string;
  disabled?: boolean;
  [key: string]: any;
};

export type StatusType = 'success' | 'error' | 'warning' | 'info';

export type DisableableProps = { disabled?: boolean };
// ...adicione outros tipos compartilhados conforme necessário...
