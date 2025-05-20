// Tipos compartilhados para agentes
export type AgentType = {
  id: string;
  name: string;
  description?: string;
  status?: "active" | "draft" | "archived";
  model?: string;
  createdAt?: string;
  updatedAt?: string;
  type?: string;
};
