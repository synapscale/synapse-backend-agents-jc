#!/usr/bin/env python3
"""
Test LLM Integration - Teste completo da integração com LLMs
Verifica configuração, endpoints e funcionalidade dos provedores
"""

import asyncio
import aiohttp
import json
import sys
import os
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from synapse.core.config import get_settings
from synapse.services.llm_service import get_llm_service
from synapse.logger_config import get_logger

logger = get_logger(__name__)

async def test_llm_configuration():
    """Test LLM configuration"""
    print("\n🔧 Testing LLM Configuration...")
    
    settings = get_settings()
    
    # Check required settings
    print(f"   Default Provider: {settings.LLM_DEFAULT_PROVIDER}")
    print(f"   OpenAI API Key: {'✅ Set' if settings.OPENAI_API_KEY else '❌ Not set'}")
    print(f"   Anthropic API Key: {'✅ Set' if settings.ANTHROPIC_API_KEY else '❌ Not set'}")
    print(f"   Google API Key: {'✅ Set' if settings.GOOGLE_API_KEY else '❌ Not set'}")
    
    return settings

async def test_service_initialization():
    """Test service initialization"""
    print("\n🚀 Testing Service Initialization...")
    
    try:
        # Test service initialization
        llm_service = get_llm_service()
        if hasattr(llm_service, 'providers'):
            providers = llm_service.providers
            print(f"   LLM Service: ✅ Initialized")
            print(f"   Available Providers: {len(providers)}")
            
            for provider_id, info in providers.items():
                status = "✅" if info.get("available") else "❌"
                models_count = len(info.get("models", []))
                print(f"     - {provider_id}: {status} ({models_count} models)")
        else:
            print("   LLM Service: ❌ Not available")
            
        return True
    except Exception as e:
        print(f"   Error: {e}")
        return False

async def test_provider_health():
    """Test provider health checks"""
    print("\n💊 Testing Provider Health...")
    
    try:
        llm_service = get_llm_service()
        health = await llm_service.health_check()
        print(f"   Overall Status: {health['status']}")
        
        if 'providers' in health:
            for provider_id, info in health['providers'].items():
                status = "✅" if info.get("available") else "❌"
                models = len(info.get("models", []))
                print(f"     - {provider_id}: {status} ({models} models)")
        
        return True
    except Exception as e:
        print(f"   Error: {e}")
        return False

async def test_token_counting():
    """Test token counting functionality"""
    print("\n🔢 Testing Token Counting...")
    
    test_text = "This is a test message to count tokens. It should work with all providers."
    
    try:
        llm_service = get_llm_service()
        result = await llm_service.count_tokens(test_text)
        print(f"   Token Count: {result['token_count']}")
        print(f"   Character Count: {result['character_count']}")
        print(f"   Word Count: {result['word_count']}")
        print(f"   Method: {result['estimation_method']}")
        
        return True
    except Exception as e:
        print(f"   Error: {e}")
        return False

async def test_model_listing():
    """Test model listing"""
    print("\n📋 Testing Model Listing...")
    
    try:
        llm_service = get_llm_service()
        result = await llm_service.list_models()
        print(f"   Total Models: {result.count}")
        
        for provider_id, models in result.models.items():
            print(f"     {provider_id}: {len(models)} models")
            for model in models[:2]:  # Show first 2 models
                print(f"       - {model['id']} ({model['name']})")
                
        return True
    except Exception as e:
        print(f"   Error: {e}")
        return False

async def test_provider_listing():
    """Test provider listing"""
    print("\n🏭 Testing Provider Listing...")
    
    try:
        llm_service = get_llm_service()
        result = llm_service.get_available_providers()
        print(f"   Total Providers: {result['count']}")
        
        for provider in result['providers']:
            print(f"     - {provider['name']} ({provider['id']}): {provider['status']}")
            print(f"       Models: {provider['models_count']}")
            
        return True
    except Exception as e:
        print(f"   Error: {e}")
        return False

async def test_text_generation():
    """Test text generation (requires API keys)"""
    print("\n🤖 Testing Text Generation...")
    
    test_prompt = "Explain what artificial intelligence is in one sentence."
    
    settings = get_settings()
    
    # Test each available provider
    providers_to_test = []
    
    if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "sua_chave_openai_aqui":
        providers_to_test.append(("openai", "gpt-3.5-turbo"))
    
    if settings.ANTHROPIC_API_KEY and settings.ANTHROPIC_API_KEY != "sua_chave_anthropic_aqui":
        providers_to_test.append(("anthropic", "claude-3-haiku-20240307"))
        
    if settings.GOOGLE_API_KEY and settings.GOOGLE_API_KEY != "sua_chave_google_aqui":
        providers_to_test.append(("google", "gemini-1.5-flash"))
    
    if not providers_to_test:
        print("   ⚠️  No real API keys configured. Testing with mock response...")
        try:
            llm_service = get_llm_service()
            result = await llm_service.generate_text(
                prompt=test_prompt,
                provider="openai",
                model="gpt-3.5-turbo",
                max_tokens=100
            )
            print(f"   Mock Response: {result.content[:100]}...")
            return True
        except Exception as e:
            print(f"   Mock Error: {e}")
            return False
    
    # Test real providers
    llm_service = get_llm_service()
    for provider, model in providers_to_test:
        try:
            print(f"   Testing {provider} ({model})...")
            result = await llm_service.generate_text(
                prompt=test_prompt,
                provider=provider,
                model=model,
                max_tokens=100
            )
            print(f"     ✅ Success: {result.content[:100]}...")
            print(f"     Tokens used: {result.usage.get('total_tokens', 'unknown')}")
        except Exception as e:
            print(f"     ❌ Error: {e}")
    
    return True

async def test_chat_completion():
    """Test chat completion"""
    print("\n💬 Testing Chat Completion...")
    
    messages = [
        {"role": "user", "content": "What is Python programming language?"}
    ]
    
    try:
        llm_service = get_llm_service()
        result = await llm_service.chat_completion(
            messages=messages,
            max_tokens=100
        )
        print(f"   Response: {result.content[:100]}...")
        return True
    except Exception as e:
        print(f"   Error: {e}")
        return False

async def test_api_endpoints():
    """Test API endpoints (requires running server)"""
    print("\n🌐 Testing API Endpoints...")
    
    base_url = "http://localhost:8000"
    
    # Test health endpoint first
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{base_url}/health") as response:
                if response.status == 200:
                    print("   ✅ Server is running")
                else:
                    print("   ❌ Server not accessible")
                    return False
    except Exception as e:
        print(f"   ❌ Server not running: {e}")
        return False
    
    # Test LLM endpoints
    endpoints_to_test = [
        ("/api/v1/llm/providers", "GET", None),
        ("/api/v1/llm/models", "GET", None),
        ("/api/v1/llm/count-tokens?text=Hello world", "POST", None),
    ]
    
    for endpoint, method, data in endpoints_to_test:
        try:
            print(f"   Testing {method} {endpoint}")
            async with aiohttp.ClientSession() as session:
                if method == "GET":
                    async with session.get(f"{base_url}{endpoint}") as response:
                        status = "✅" if response.status == 200 else f"❌ {response.status}"
                        print(f"     {status}")
                elif method == "POST":
                    async with session.post(f"{base_url}{endpoint}", json=data) as response:
                        status = "✅" if response.status == 200 else f"❌ {response.status}"
                        print(f"     {status}")
        except Exception as e:
            print(f"     ❌ Error: {e}")
    
    return True

async def main():
    """Main test function"""
    print("🔥 SynapScale LLM Integration Test")
    print("=" * 50)
    
    settings = await test_llm_configuration()
    
    if not settings:
        print("❌ Configuration test failed")
        return
        
    # Check if API keys are configured
    has_real_keys = any([
        settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "sua_chave_openai_aqui",
        settings.ANTHROPIC_API_KEY and settings.ANTHROPIC_API_KEY != "sua_chave_anthropic_aqui", 
        settings.GOOGLE_API_KEY and settings.GOOGLE_API_KEY != "sua_chave_google_aqui"
    ])
    
    if not has_real_keys:
        print("\n⚠️  No real API keys configured. Set these in .env:")
        print("   - OPENAI_API_KEY=sua_chave_openai")
        print("   - ANTHROPIC_API_KEY=sua_chave_anthropic")
        print("   - GOOGLE_API_KEY=sua_chave_google")
    
    # Run tests
    tests = [
        test_service_initialization,
        test_provider_health,
        test_token_counting,
        test_model_listing,
        test_provider_listing,
        test_text_generation,
        test_chat_completion,
        # test_api_endpoints,  # Requires running server
    ]
    
    results = []
    for test_func in tests:
        try:
            result = await test_func()
            results.append(result)
        except Exception as e:
            print(f"   ❌ Test failed: {e}")
            results.append(False)
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 50)
    passed = sum(results)
    total = len(results)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed. Check configuration and API keys.")
    
    print("\n🔧 Configuration Status:")
    providers_status = {
        "OpenAI": bool(settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "sua_chave_openai_aqui"),
        "Anthropic": bool(settings.ANTHROPIC_API_KEY and settings.ANTHROPIC_API_KEY != "sua_chave_anthropic_aqui"),
        "Google": bool(settings.GOOGLE_API_KEY and settings.GOOGLE_API_KEY != "sua_chave_google_aqui"),
    }
    
    for provider, configured in providers_status.items():
        status = "✅ Configured" if configured else "❌ Not configured"
        print(f"   {provider}: {status}")

if __name__ == "__main__":
    asyncio.run(main()) 