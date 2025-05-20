export function formValidation(values: Record<string, any>) {
  // Exemplo simples de validação
  return Object.values(values).every((v) => v !== undefined && v !== null && v !== "");
}
