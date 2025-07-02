#!/usr/bin/env python3
"""
Script simples para testar o endpoint LLM models sem autenticação
"""

import asyncio
import aiohttp
import json

BASE_URL = "http://localhost:8000"


async def test_llm_models_simple():
    """Testa o endpoint /api/v1/llm/models sem autenticação"""

    async with aiohttp.ClientSession() as session:
        print("🤖 Testando endpoint /api/v1/llm/models...")

        async with session.get(f"{BASE_URL}/api/v1/llm/models") as response:
            print(f"Status: {response.status}")

            if response.status == 200:
                data = await response.json()
                print("✅ Sucesso!")
                print(f"Número de provedores: {data.get('count', 0)}")

                # Mostrar apenas um resumo dos modelos por provedor
                models = data.get("models", {})
                for provider, provider_models in models.items():
                    print(f"  {provider}: {len(provider_models)} modelos")

                return True
            else:
                print(f"❌ Falha: {response.status}")
                try:
                    error_data = await response.json()
                    print(
                        f"Erro: {json.dumps(error_data, indent=2, ensure_ascii=False)}"
                    )
                except:
                    error_text = await response.text()
                    print(f"Erro: {error_text}")
                return False


async def main():
    """Função principal"""
    print("🧪 Testando endpoint LLM models simples\n")

    success = await test_llm_models_simple()

    if success:
        print("\n🎉 Teste passou!")
        return 0
    else:
        print("\n💥 Teste falhou!")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
