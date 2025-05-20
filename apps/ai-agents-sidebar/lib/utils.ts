// Arquivo removido. Utilize o utilitário centralizado em packages/utils/shared-utils.ts

/**
 * Junta classes CSS condicionalmente (igual ao clsx/tailwind-merge)
 */
export function cn(...classes: (string | undefined | null | false)[]): string {
  return classes.filter(Boolean).join(" ")
}
