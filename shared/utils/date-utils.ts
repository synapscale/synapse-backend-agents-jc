// Funções utilitárias compartilhadas
// Implemente aqui utils reutilizáveis e use nos apps

// Exemplo de função utilitária para manipulação de datas
export const formatDate = (date: string | Date): string => {
  const d = typeof date === "string" ? new Date(date) : date;
  return d.toISOString().split('T')[0];
};
