#!/usr/bin/env python3
"""
Test SynapScale LLM Endpoints - Versão Corrigida
Testa todos os endpoints LLM com sistema de user_variables para API keys
"""

import asyncio
import aiohttp
import json
import sys
import os
import time
from pathlib import Path
from typing import Dict, Any, Optional

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Configurar variáveis de ambiente para teste
os.environ.setdefault("ENVIRONMENT", "development")
os.environ.setdefault("DEBUG", "true")

from synapse.services.llm_service import get_llm_service
from synapse.logger_config import get_logger

logger = get_logger(__name__)


# Cores para output
class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    BOLD = "\033[1m"
    END = "\033[0m"


def print_header(title):
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*60}")
    print(f"{title}")
    print(f"{'='*60}{Colors.END}")


def print_success(message):
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")


def print_error(message):
    print(f"{Colors.RED}❌ {message}{Colors.END}")


def print_warning(message):
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.END}")


def print_info(message):
    print(f"{Colors.BLUE}ℹ️  {message}{Colors.END}")


async def test_service_initialization():
    """Testa inicialização dos serviços"""
    print_header("TESTE DE INICIALIZAÇÃO DOS SERVIÇOS")

    services_tested = 0
    services_working = 0

    # Teste 1: Unified Service
    try:
        print_info("Testando Unified Service...")
        llm_service = get_llm_service()
        if hasattr(llm_service, "get_available_providers"):
            providers = llm_service.get_available_providers()
            if providers and "count" in providers:
                print_success(f"Unified Service OK - {providers['count']} provedores")
                services_working += 1
            else:
                print_error("Unified Service retornou dados inválidos")
        services_tested += 1
    except Exception as e:
        print_error(f"Unified Service falhou: {e}")
        services_tested += 1

    # Teste 2: Main LLM Service
    try:
        print_info("Testando Main LLM Service...")
        llm_service = get_llm_service()
        if hasattr(llm_service, "providers"):
            available_providers = len(
                [p for p in llm_service.providers.values() if p.get("available")]
            )
            total_providers = len(llm_service.providers)
            print_success(
                f"Main LLM Service OK - {available_providers}/{total_providers} provedores disponíveis"
            )

            # Mostrar detalhes dos provedores
            for provider_id, info in llm_service.providers.items():
                status = "✅" if info.get("available") else "❌"
                models_count = len(info.get("models", []))
                print(f"      {provider_id}: {status} ({models_count} modelos)")

            services_working += 1
        services_tested += 1
    except Exception as e:
        print_error(f"Main LLM Service falhou: {e}")
        services_tested += 1

    # Teste 3: Serviço padrão atual
    try:
        print_info("Testando serviço padrão atual...")
        llm_service = get_llm_service()
        current_service_type = type(llm_service).__name__
        print_success(f"Serviço padrão: {current_service_type}")
        services_working += 1
        services_tested += 1
    except Exception as e:
        print_error(f"Serviço padrão falhou: {e}")
        services_tested += 1

    print_info(f"Resultado: {services_working}/{services_tested} serviços funcionando")
    return services_working == services_tested


async def test_individual_providers():
    """Testa provedores individuais"""
    print_header("TESTE DE PROVEDORES INDIVIDUAIS")

    providers_to_test = [
        ("openai", "gpt-3.5-turbo"),
        ("anthropic", "claude-3-haiku-20240307"),
        ("google", "gemini-1.5-flash"),
    ]

    success_count = 0

    for provider, model in providers_to_test:
        print_info(f"Testando {provider} com modelo {model}")

        try:
            llm_service = get_llm_service()
            response = await llm_service.generate_text(
                prompt="Responda apenas 'OK'",
                provider=provider,
                model=model,
                max_tokens=10,
            )

            if hasattr(response, "content") and response.content:
                print_success(f"{provider}: {response.content[:50]}...")
                success_count += 1
            else:
                print_warning(f"{provider}: Resposta vazia")

        except Exception as e:
            print_error(f"{provider}: {str(e)}")

    return success_count


async def test_model_listing():
    """Testa a listagem de modelos"""
    print_header("TESTE DE LISTAGEM DE MODELOS")

    try:
        print_info("Listando todos os modelos...")
        llm_service = get_llm_service()
        models_response = await llm_service.list_models()

        # Verificar se é um objeto com atributo models ou um dict
        if hasattr(models_response, "models"):
            models = models_response.models
            total_count = models_response.count
        elif isinstance(models_response, dict) and "models" in models_response:
            models = models_response["models"]
            total_count = models_response.get("count", 0)
        else:
            print_error("Formato de resposta inválido")
            return False

        total_models = 0

        for provider_name, provider_models in models.items():
            model_count = len(provider_models)
            total_models += model_count
            print_success(f"{provider_name}: {model_count} modelos")

            # Mostrar alguns modelos
            for i, model in enumerate(provider_models[:3]):  # Primeiros 3 modelos
                if hasattr(model, "name"):
                    model_name = model.name
                    context = getattr(model, "context_window", "N/A")
                elif isinstance(model, dict):
                    model_name = model.get("name", model.get("id", "N/A"))
                    context = model.get("context_window", "N/A")
                else:
                    model_name = str(model)
                    context = "N/A"

                print(f"      - {model_name} (contexto: {context})")

        print_success(
            f"Total: {total_models} modelos disponíveis (esperado: {total_count})"
        )
        return True

    except Exception as e:
        print_error(f"Erro ao listar modelos: {e}")
        import traceback

        print_error(f"Traceback: {traceback.format_exc()}")
        return False


async def test_token_counting():
    """Testa a contagem de tokens"""
    print_header("TESTE DE CONTAGEM DE TOKENS")

    test_texts = [
        "Hello, world!",
        "Este é um texto em português para testar a contagem de tokens.",
        "This is a longer text that should have more tokens. We want to test how the tokenizer handles different lengths and languages.",
    ]

    success_count = 0

    for i, text in enumerate(test_texts, 1):
        print_info(f"Teste {i}: '{text[:50]}...'")

        try:
            llm_service = get_llm_service()
            result = await llm_service.count_tokens(text=text)

            if isinstance(result, dict) and "token_count" in result:
                token_count = result["token_count"]
                char_count = len(text)
                print_success(f"Tokens: {token_count}, Chars: {char_count}")
                success_count += 1
            else:
                print_error("Resposta de contagem inválida")

        except Exception as e:
            print_error(f"Erro na contagem: {e}")

    return success_count == len(test_texts)


async def test_chat_completion():
    """Testa chat completion"""
    print_header("TESTE DE CHAT COMPLETION")

    test_messages = [
        [{"role": "user", "content": "What is Python?"}],
        [
            {"role": "user", "content": "Hello!"},
            {"role": "assistant", "content": "Hi there! How can I help you?"},
            {"role": "user", "content": "Tell me about AI"},
        ],
    ]

    success_count = 0

    for i, messages in enumerate(test_messages, 1):
        print_info(f"Teste de chat {i} com {len(messages)} mensagens")

        try:
            llm_service = get_llm_service()
            response = await llm_service.chat_completion(
                messages=messages, max_tokens=100
            )

            if hasattr(response, "content") and response.content:
                print_success(f"Chat completion OK")
                print(f"   Resposta: {response.content[:100]}...")
                success_count += 1
            else:
                print_warning("Resposta de chat vazia")

        except Exception as e:
            print_error(f"Erro no chat: {e}")

    return success_count == len(test_messages)


async def test_error_handling():
    """Testa o tratamento de erros"""
    print_header("TESTE DE TRATAMENTO DE ERROS")

    error_tests = [
        {
            "name": "Prompt vazio",
            "params": {"prompt": "", "provider": "openai"},
            "should_fail": True,
        },
        {
            "name": "Provedor inválido",
            "params": {"prompt": "Hello", "provider": "invalid_provider"},
            "should_fail": False,  # Deveria fazer fallback para mock
        },
        {
            "name": "Modelo inválido",
            "params": {
                "prompt": "Hello",
                "provider": "openai",
                "model": "invalid_model",
            },
            "should_fail": False,  # Deveria usar modelo padrão
        },
        {
            "name": "Parâmetros válidos",
            "params": {"prompt": "Hello", "max_tokens": 10},
            "should_fail": False,
        },
    ]

    success_count = 0

    for test in error_tests:
        print_info(f"Teste: {test['name']}")

        try:
            llm_service = get_llm_service()
            response = await llm_service.generate_text(**test["params"])

            if test["should_fail"]:
                print_warning(f"Deveria ter falhado mas funcionou")
            else:
                print_success(f"Funcionou como esperado")
                success_count += 1

        except Exception as e:
            if test["should_fail"]:
                print_success(f"Falhou como esperado: {str(e)[:50]}")
                success_count += 1
            else:
                print_error(f"Não deveria ter falhado: {e}")

    return success_count == len(error_tests)


async def test_performance():
    """Testa performance básica"""
    print_header("TESTE DE PERFORMANCE")

    print_info("Testando latência de resposta...")

    start_time = time.time()

    try:
        llm_service = get_llm_service()
        response = await llm_service.generate_text(
            prompt="Respond with just 'OK'", max_tokens=5
        )

        end_time = time.time()
        latency = end_time - start_time

        print_success(f"Latência: {latency:.2f}s")

        if latency < 10:  # Menos de 10 segundos é aceitável
            print_success("Performance aceitável")
            return True
        else:
            print_warning("Performance lenta")
            return False

    except Exception as e:
        print_error(f"Erro no teste de performance: {e}")
        return False


async def test_provider_health():
    """Testa health check dos provedores"""
    print_header("TESTE DE HEALTH CHECK")

    try:
        llm_service = get_llm_service()
        health = await llm_service.health_check()

        if isinstance(health, dict):
            print_success(f"Status geral: {health.get('status', 'unknown')}")

            if "providers" in health:
                for provider_id, info in health["providers"].items():
                    status = "✅" if info.get("available") else "❌"
                    models = len(info.get("models", []))
                    print(f"   {provider_id}: {status} ({models} modelos)")

            return True
        else:
            print_error("Resposta de health check inválida")
            return False

    except Exception as e:
        print_error(f"Erro no health check: {e}")
        return False


async def test_api_endpoints():
    """Testa endpoints da API via HTTP (opcional - se servidor estiver rodando)"""
    print_header("TESTE DOS ENDPOINTS HTTP (OPCIONAL)")

    base_url = "http://localhost:8000"

    # Verificar se servidor está rodando
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{base_url}/health", timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                if response.status == 200:
                    print_success("Servidor está rodando")
                else:
                    print_warning(f"Servidor responde mas com status {response.status}")
                    return False
    except Exception as e:
        print_warning(f"Servidor não está rodando: {e}")
        return False

    endpoints_to_test = [
        ("GET", "/api/v1/llm/providers", None, "Listar provedores"),
    ]

    success_count = 0

    try:
        async with aiohttp.ClientSession() as session:

            # Testar cada endpoint
            for method, endpoint, data, description in endpoints_to_test:
                print_info(f"Testando {method} {endpoint} - {description}")

                try:
                    if method == "GET":
                        async with session.get(f"{base_url}{endpoint}") as response:
                            if response.status == 200:
                                print_success(f"OK (status: {response.status})")
                                success_count += 1
                            elif response.status == 401:
                                print_warning(
                                    f"Precisa autenticação (status: {response.status})"
                                )
                                success_count += 1  # Esperado sem auth
                            else:
                                print_warning(f"Status: {response.status}")

                except Exception as e:
                    print_error(f"Erro: {e}")

    except Exception as e:
        print_error(f"Erro na sessão HTTP: {e}")

    return success_count == len(endpoints_to_test)


async def generate_test_report():
    """Gera relatório final dos testes"""
    print_header("RELATÓRIO FINAL DOS TESTES")

    tests = [
        ("Inicialização dos Serviços", test_service_initialization),
        ("Provedores Individuais", test_individual_providers),
        ("Listagem de Modelos", test_model_listing),
        ("Contagem de Tokens", test_token_counting),
        ("Chat Completion", test_chat_completion),
        ("Tratamento de Erros", test_error_handling),
        ("Performance", test_performance),
        ("Health Check", test_provider_health),
        ("Endpoints HTTP", test_api_endpoints),
    ]

    results = {}
    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n{Colors.YELLOW}Executando: {test_name}...{Colors.END}")
        try:
            result = await test_func()
            results[test_name] = result
            if result:
                passed += 1
        except Exception as e:
            print_error(f"Teste '{test_name}' falhou com exceção: {e}")
            results[test_name] = False

    # Relatório final
    print_header("RESUMO DOS RESULTADOS")

    for test_name, result in results.items():
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{status} - {test_name}")

    success_rate = (passed / total) * 100
    print(
        f"\n{Colors.BOLD}Taxa de Sucesso: {success_rate:.1f}% ({passed}/{total} testes){Colors.END}"
    )

    if success_rate >= 80:
        print_success("Sistema funcionando bem!")
    elif success_rate >= 60:
        print_warning("Sistema parcialmente funcional")
    else:
        print_error("Sistema precisa de correções")

    return results


async def main():
    """Função principal"""
    print_header("SYNAPSCALE LLM ENDPOINTS - TESTE COMPLETO")
    print_info("Versão corrigida com suporte a user_variables")

    try:
        results = await generate_test_report()
        return results
    except Exception as e:
        print_error(f"Erro geral nos testes: {e}")
        return {}


if __name__ == "__main__":
    asyncio.run(main())
