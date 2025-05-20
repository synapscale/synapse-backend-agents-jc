// Função para obter o ícone do provedor
export function getProviderIcon(provider: string) {
  switch (provider) {
    case "openai":
      return "i"
    case "deepseek":
      return <img src="/deepseek-logo-inspired.png" alt="DeepSeek" className="w-4 h-4" />
    case "qwen":
      return <img src="/placeholder-ct6n6.png" alt="Qwen" className="w-4 h-4" />
    case "google":
      return <img src="/google-g-logo.png" alt="Google" className="w-4 h-4" />
    case "anthropic":
      return <img src="/anthropic-logo.png" alt="Anthropic" className="w-4 h-4" />
    case "xai":
      return <img src="/placeholder-akjv1.png" alt="xAI" className="w-4 h-4" />
    case "meta":
      return <img src="/abstract-infinity-logo.png" alt="Meta" className="w-4 h-4" />
    default:
      return "i"
  }
}

// Nomes de exibição para os provedores
export const providerNames: Record<string, string> = {
  openai: "OpenAI",
  deepseek: "DeepSeek",
  qwen: "Qwen",
  google: "Google",
  anthropic: "Anthropic",
  xai: "xAI",
  meta: "Meta",
}
