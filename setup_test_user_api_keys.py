#!/usr/bin/env python3
"""
Script para configurar um usuário de teste com API keys no banco de dados
Demonstra como o sistema funciona com API keys reais armazenadas no banco
"""

import asyncio
import sys
import os
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from sqlalchemy.orm import Session
from synapse.database import get_db_session
from synapse.services.llm_service import get_llm_service
from synapse.models.user import User
from synapse.models.user_variable import UserVariable
from synapse.logger_config import get_logger

logger = get_logger(__name__)

# API Keys de teste válidas (substitua pelas suas chaves reais se desejar testar com APIs reais)
TEST_API_KEYS = {
    "openai": "sk-test-openai-key-substitua-pela-sua-chave-real",
    "anthropic": "sk-ant-test-anthropic-key-substitua-pela-sua-chave-real", 
    "google": "test-google-key-substitua-pela-sua-chave-real",
    "grok": "test-grok-key-substitua-pela-sua-chave-real",
    "deepseek": "test-deepseek-key-substitua-pela-sua-chave-real",
    "llama": "test-llama-key-substitua-pela-sua-chave-real"
}

def create_test_user(db: Session) -> User:
    """Cria um usuário de teste se não existir"""
    try:
        # Verificar se já existe
        test_user = db.query(User).filter(User.email == "test@synapscale.com").first()
        
        if test_user:
            print(f"✅ Usuário de teste já existe: {test_user.email} (ID: {test_user.id})")
            return test_user
        
        # Criar novo usuário
        test_user = User(
            username="test_user",
            email="test@synapscale.com",
            full_name="Test User",
            is_active=True
        )
        test_user.set_password("test123")  # Senha simples para teste
        
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        
        print(f"✅ Usuário de teste criado: {test_user.email} (ID: {test_user.id})")
        return test_user
        
    except Exception as e:
        db.rollback()
        print(f"❌ Erro ao criar usuário de teste: {e}")
        raise

def setup_user_api_keys(db: Session, user: User):
    """Configura as API keys do usuário no banco"""
    try:
        print(f"\n🔧 Configurando API keys para usuário {user.email}...")
        
        llm_service = get_llm_service()
        success_count = 0
        
        for provider, api_key in TEST_API_KEYS.items():
            try:
                success = llm_service.create_or_update_user_api_key(
                    db=db,
                    user_id=user.id,  # UUID direto
                    provider=provider,
                    api_key=api_key
                )
                
                if success:
                    print(f"   ✅ {provider}: API key configurada")
                    success_count += 1
                else:
                    print(f"   ❌ {provider}: Falha ao configurar API key")
                    
            except Exception as e:
                print(f"   ❌ {provider}: Erro - {e}")
        
        print(f"\n✅ {success_count}/{len(TEST_API_KEYS)} API keys configuradas com sucesso")
        return success_count == len(TEST_API_KEYS)
        
    except Exception as e:
        print(f"❌ Erro geral ao configurar API keys: {e}")
        return False

def list_user_api_keys(db: Session, user: User):
    """Lista as API keys configuradas do usuário"""
    try:
        print(f"\n📋 API keys configuradas para {user.email}:")
        
        llm_service = get_llm_service()
        api_keys = llm_service.list_user_api_keys(db, user.id)
        
        if not api_keys:
            print("   Nenhuma API key configurada")
            return
        
        for key_info in api_keys:
            provider = key_info['provider_name']
            value = key_info['value']
            is_active = key_info['is_active']
            
            # Mascarar a chave para exibição
            if len(value) > 8:
                masked_value = value[:4] + "*" * (len(value) - 8) + value[-4:]
            else:
                masked_value = "*" * len(value)
            
            status = "✅" if is_active else "❌"
            print(f"   {status} {provider}: {masked_value}")
            
    except Exception as e:
        print(f"❌ Erro ao listar API keys: {e}")

async def test_user_llm_generation(db: Session, user: User):
    """Testa geração de texto usando as API keys do usuário"""
    try:
        print(f"\n🧪 Testando geração de texto com API keys do usuário {user.email}...")
        
        llm_service = get_llm_service()
        test_cases = [
            ("openai", "gpt-3.5-turbo", "Responda apenas 'OpenAI OK'"),
            ("anthropic", "claude-3-haiku-20240307", "Responda apenas 'Anthropic OK'"),
            ("google", "gemini-1.5-flash", "Responda apenas 'Google OK'")
        ]
        
        success_count = 0
        
        for provider, model, prompt in test_cases:
            try:
                print(f"   Testando {provider}...")
                
                response = await llm_service.generate_text_for_user(
                    prompt=prompt,
                    user_id=user.id,
                    db=db,
                    provider=provider,
                    model=model,
                    max_tokens=50
                )
                
                if hasattr(response, 'content') and response.content:
                    print(f"   ✅ {provider}: {response.content[:50]}...")
                    success_count += 1
                else:
                    print(f"   ❌ {provider}: Resposta vazia")
                    
            except Exception as e:
                print(f"   ❌ {provider}: {str(e)[:100]}...")
        
        print(f"\n✅ {success_count}/{len(test_cases)} provedores funcionaram com API keys do usuário")
        return success_count > 0
        
    except Exception as e:
        print(f"❌ Erro geral no teste: {e}")
        return False

def main():
    """Função principal"""
    print("🚀 CONFIGURAÇÃO DE USUÁRIO DE TESTE COM API KEYS")
    print("=" * 60)
    
    try:
        # Obter sessão do banco
        db = next(get_db_session())
        
        try:
            # 1. Criar usuário de teste
            print("\n1️⃣ Criando usuário de teste...")
            user = create_test_user(db)
            
            # 2. Configurar API keys
            print("\n2️⃣ Configurando API keys...")
            setup_success = setup_user_api_keys(db, user)
            
            # 3. Listar API keys configuradas
            print("\n3️⃣ Verificando configuração...")
            list_user_api_keys(db, user)
            
            # 4. Testar geração com API keys do usuário
            print("\n4️⃣ Testando funcionalidade...")
            test_success = asyncio.run(test_user_llm_generation(db, user))
            
            # Resumo
            print("\n" + "=" * 60)
            print("📊 RESUMO DA CONFIGURAÇÃO")
            print("=" * 60)
            print(f"👤 Usuário: {user.email} (ID: {user.id})")
            print(f"🔑 API Keys: {'✅ Configuradas' if setup_success else '❌ Problemas'}")
            print(f"🧪 Testes: {'✅ Funcionando' if test_success else '❌ Com problemas'}")
            
            if setup_success and test_success:
                print("\n🎉 CONFIGURAÇÃO CONCLUÍDA COM SUCESSO!")
                print("\nAgora você pode:")
                print("- Usar este usuário para testes de API")
                print("- Executar testes com API keys reais do banco") 
                print("- Fazer login com: test@synapscale.com / test123")
            else:
                print("\n⚠️  Configuração parcial ou com problemas")
                print("Verifique os logs acima para detalhes")
                
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Erro fatal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 