// Junta classes CSS condicionalmente (igual ao clsx/tailwind-merge)
export function cn(...classes: (string | undefined | null | false)[]): string {
  return classes.filter(Boolean).join(" ");
}
