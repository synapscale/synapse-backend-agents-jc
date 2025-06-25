#!/usr/bin/env python3
"""
Script para popular TODOS os modelos LLM disponíveis no banco de dados
Versão completa e atualizada com todos os provedores e modelos (Dezembro 2024)
Criado por José - um desenvolvedor Full Stack
"""

import os
import sys
from pathlib import Path

# Adicionar src ao path
BASE_DIR = Path(__file__).parent.parent
sys.path.append(str(BASE_DIR / "src"))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from synapse.database import get_db
from synapse.models.llm import LLM
from synapse.core.config import settings


def populate_complete_llms():
    """Popula TODOS os LLMs disponíveis no banco de dados"""
    
    # Conectar ao banco
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        print("🚀 Iniciando população completa de LLMs...")
        
        # Limpar LLMs existentes se solicitado
        existing_count = db.query(LLM).count()
        if existing_count > 0:
            print(f"⚠️  Encontrados {existing_count} LLMs existentes.")
            response = input("Deseja substituir todos? (s/N): ").lower()
            if response == 's':
                db.query(LLM).delete()
                db.commit()
                print("🗑️  LLMs existentes removidos.")
            else:
                print("✅ Mantendo LLMs existentes. Adicionando apenas novos.")
        
        # TODOS os LLMs disponíveis (Dezembro 2024)
        llms_data = [
            # ========================================
            # OPENAI - Modelos mais recentes
            # ========================================
            {
                "name": "gpt-4o",
                "provider": "openai",
                "model_version": "2024-11-20",
                "cost_per_token_input": 0.0000025,
                "cost_per_token_output": 0.00001,
                "max_tokens_supported": 16384,
                "supports_function_calling": True,
                "supports_vision": True,
                "supports_streaming": True,
                "context_window": 128000,
                "llm_metadata": {
                    "description": "GPT-4o - Modelo mais avançado da OpenAI com visão",
                    "release_date": "2024-11-20",
                    "capabilities": ["text", "vision", "function_calling", "reasoning"],
                    "best_for": ["Análise complexa", "Visão computacional", "Raciocínio avançado"]
                }
            },
            {
                "name": "gpt-4o-mini",
                "provider": "openai",
                "model_version": "2024-07-18",
                "cost_per_token_input": 0.00000015,
                "cost_per_token_output": 0.0000006,
                "max_tokens_supported": 16384,
                "supports_function_calling": True,
                "supports_vision": True,
                "supports_streaming": True,
                "context_window": 128000,
                "llm_metadata": {
                    "description": "GPT-4o Mini - Versão rápida e econômica do GPT-4o",
                    "release_date": "2024-07-18",
                    "capabilities": ["text", "vision", "function_calling"],
                    "best_for": ["Tarefas rápidas", "Alto volume", "Custo-benefício"]
                }
            },
            {
                "name": "gpt-4-turbo",
                "provider": "openai",
                "model_version": "2024-04-09",
                "cost_per_token_input": 0.00001,
                "cost_per_token_output": 0.00003,
                "max_tokens_supported": 4096,
                "supports_function_calling": True,
                "supports_vision": True,
                "supports_streaming": True,
                "context_window": 128000,
                "llm_metadata": {
                    "description": "GPT-4 Turbo - Versão otimizada do GPT-4",
                    "release_date": "2024-04-09",
                    "capabilities": ["text", "vision", "function_calling"],
                    "best_for": ["Análise de documentos", "Programação", "Criação de conteúdo"]
                }
            },
            {
                "name": "gpt-4",
                "provider": "openai",
                "model_version": "2024-02-01",
                "cost_per_token_input": 0.00003,
                "cost_per_token_output": 0.00006,
                "max_tokens_supported": 8192,
                "supports_function_calling": True,
                "supports_vision": False,
                "supports_streaming": True,
                "context_window": 8192,
                "llm_metadata": {
                    "description": "GPT-4 - Modelo clássico de alta qualidade",
                    "release_date": "2023-03-14",
                    "capabilities": ["text", "function_calling", "reasoning"],
                    "best_for": ["Tarefas complexas", "Análise profunda", "Criatividade"]
                }
            },
            {
                "name": "gpt-3.5-turbo",
                "provider": "openai",
                "model_version": "2024-01-25",
                "cost_per_token_input": 0.0000005,
                "cost_per_token_output": 0.0000015,
                "max_tokens_supported": 4096,
                "supports_function_calling": True,
                "supports_vision": False,
                "supports_streaming": True,
                "context_window": 16385,
                "llm_metadata": {
                    "description": "GPT-3.5 Turbo - Modelo rápido e econômico",
                    "release_date": "2022-11-30",
                    "capabilities": ["text", "function_calling"],
                    "best_for": ["Chat", "Tarefas simples", "Alto volume"]
                }
            },
            {
                "name": "gpt-3.5-turbo-instruct",
                "provider": "openai",
                "model_version": "2023-09-01",
                "cost_per_token_input": 0.0000015,
                "cost_per_token_output": 0.000002,
                "max_tokens_supported": 4096,
                "supports_function_calling": False,
                "supports_vision": False,
                "supports_streaming": True,
                "context_window": 4096,
                "llm_metadata": {
                    "description": "GPT-3.5 Turbo Instruct - Modelo de completação",
                    "release_date": "2023-09-01",
                    "capabilities": ["text"],
                    "best_for": ["Completação de texto", "Geração criativa"]
                }
            },

            # ========================================
            # ANTHROPIC CLAUDE - Família Claude 3.5 e 3
            # ========================================
            {
                "name": "claude-3-5-sonnet-20241022",
                "provider": "anthropic",
                "model_version": "20241022",
                "cost_per_token_input": 0.000003,
                "cost_per_token_output": 0.000015,
                "max_tokens_supported": 8192,
                "supports_function_calling": True,
                "supports_vision": True,
                "supports_streaming": True,
                "context_window": 200000,
                "llm_metadata": {
                    "description": "Claude 3.5 Sonnet - Modelo mais avançado da Anthropic",
                    "release_date": "2024-10-22",
                    "capabilities": ["text", "vision", "function_calling", "reasoning", "code"],
                    "best_for": ["Análise complexa", "Programação", "Raciocínio avançado"]
                }
            },
            {
                "name": "claude-3-5-haiku-20241022",
                "provider": "anthropic",
                "model_version": "20241022",
                "cost_per_token_input": 0.00000025,
                "cost_per_token_output": 0.00000125,
                "max_tokens_supported": 8192,
                "supports_function_calling": True,
                "supports_vision": True,
                "supports_streaming": True,
                "context_window": 200000,
                "llm_metadata": {
                    "description": "Claude 3.5 Haiku - Modelo rápido e eficiente",
                    "release_date": "2024-10-22",
                    "capabilities": ["text", "vision", "function_calling"],
                    "best_for": ["Respostas rápidas", "Alto volume", "Tarefas simples"]
                }
            },
            {
                "name": "claude-3-opus-20240229",
                "provider": "anthropic",
                "model_version": "20240229",
                "cost_per_token_input": 0.000015,
                "cost_per_token_output": 0.000075,
                "max_tokens_supported": 4096,
                "supports_function_calling": True,
                "supports_vision": True,
                "supports_streaming": True,
                "context_window": 200000,
                "llm_metadata": {
                    "description": "Claude 3 Opus - Modelo premium para tarefas complexas",
                    "release_date": "2024-02-29",
                    "capabilities": ["text", "vision", "function_calling", "reasoning"],
                    "best_for": ["Análise profunda", "Criatividade", "Tarefas complexas"]
                }
            },
            {
                "name": "claude-3-sonnet-20240229",
                "provider": "anthropic",
                "model_version": "20240229",
                "cost_per_token_input": 0.000003,
                "cost_per_token_output": 0.000015,
                "max_tokens_supported": 4096,
                "supports_function_calling": True,
                "supports_vision": True,
                "supports_streaming": True,
                "context_window": 200000,
                "llm_metadata": {
                    "description": "Claude 3 Sonnet - Equilíbrio entre performance e custo",
                    "release_date": "2024-02-29",
                    "capabilities": ["text", "vision", "function_calling"],
                    "best_for": ["Uso geral", "Análise de documentos", "Programação"]
                }
            },
            {
                "name": "claude-3-haiku-20240307",
                "provider": "anthropic",
                "model_version": "20240307",
                "cost_per_token_input": 0.00000025,
                "cost_per_token_output": 0.00000125,
                "max_tokens_supported": 4096,
                "supports_function_calling": True,
                "supports_vision": True,
                "supports_streaming": True,
                "context_window": 200000,
                "llm_metadata": {
                    "description": "Claude 3 Haiku - Modelo rápido e econômico",
                    "release_date": "2024-03-07",
                    "capabilities": ["text", "vision", "function_calling"],
                    "best_for": ["Respostas rápidas", "Chat", "Tarefas simples"]
                }
            },

            # ========================================
            # GOOGLE GEMINI - Família Gemini 2.0 e 1.5
            # ========================================
            {
                "name": "gemini-2.0-flash-exp",
                "provider": "google",
                "model_version": "experimental",
                "cost_per_token_input": 0.0000001,
                "cost_per_token_output": 0.0000004,
                "max_tokens_supported": 8192,
                "supports_function_calling": True,
                "supports_vision": True,
                "supports_streaming": True,
                "context_window": 1000000,
                "llm_metadata": {
                    "description": "Gemini 2.0 Flash - Modelo experimental mais avançado",
                    "release_date": "2024-12-11",
                    "capabilities": ["text", "vision", "function_calling", "reasoning", "multimodal"],
                    "best_for": ["Tarefas multimodais", "Experimentação", "Análise avançada"]
                }
            },
            {
                "name": "gemini-1.5-pro",
                "provider": "google",
                "model_version": "latest",
                "cost_per_token_input": 0.0000035,
                "cost_per_token_output": 0.0000105,
                "max_tokens_supported": 8192,
                "supports_function_calling": True,
                "supports_vision": True,
                "supports_streaming": True,
                "context_window": 2000000,
                "llm_metadata": {
                    "description": "Gemini 1.5 Pro - Modelo avançado com contexto extenso",
                    "release_date": "2024-02-15",
                    "capabilities": ["text", "vision", "function_calling", "reasoning"],
                    "best_for": ["Análise de documentos longos", "Contexto extenso", "Multimodal"]
                }
            },
            {
                "name": "gemini-1.5-flash",
                "provider": "google",
                "model_version": "latest",
                "cost_per_token_input": 0.000000075,
                "cost_per_token_output": 0.0000003,
                "max_tokens_supported": 8192,
                "supports_function_calling": True,
                "supports_vision": True,
                "supports_streaming": True,
                "context_window": 1000000,
                "llm_metadata": {
                    "description": "Gemini 1.5 Flash - Modelo rápido e eficiente",
                    "release_date": "2024-05-14",
                    "capabilities": ["text", "vision", "function_calling"],
                    "best_for": ["Respostas rápidas", "Alto volume", "Custo-benefício"]
                }
            },
            {
                "name": "gemini-1.5-flash-8b",
                "provider": "google",
                "model_version": "latest",
                "cost_per_token_input": 0.0000000375,
                "cost_per_token_output": 0.00000015,
                "max_tokens_supported": 8192,
                "supports_function_calling": True,
                "supports_vision": False,
                "supports_streaming": True,
                "context_window": 1000000,
                "llm_metadata": {
                    "description": "Gemini 1.5 Flash 8B - Modelo ultra-rápido e econômico",
                    "release_date": "2024-10-03",
                    "capabilities": ["text", "function_calling"],
                    "best_for": ["Alto volume", "Tarefas simples", "Máximo custo-benefício"]
                }
            },
            {
                "name": "gemini-1.0-pro",
                "provider": "google",
                "model_version": "latest",
                "cost_per_token_input": 0.0000005,
                "cost_per_token_output": 0.0000015,
                "max_tokens_supported": 8192,
                "supports_function_calling": True,
                "supports_vision": False,
                "supports_streaming": True,
                "context_window": 32768,
                "llm_metadata": {
                    "description": "Gemini 1.0 Pro - Modelo clássico do Google",
                    "release_date": "2023-12-06",
                    "capabilities": ["text", "function_calling"],
                    "best_for": ["Uso geral", "Chat", "Análise de texto"]
                }
            },

            # ========================================
            # GROK (xAI) - Modelos Grok
            # ========================================
            {
                "name": "grok-2-1212",
                "provider": "grok",
                "model_version": "1212",
                "cost_per_token_input": 0.000002,
                "cost_per_token_output": 0.00001,
                "max_tokens_supported": 8192,
                "supports_function_calling": True,
                "supports_vision": True,
                "supports_streaming": True,
                "context_window": 131072,
                "llm_metadata": {
                    "description": "Grok 2 - Modelo mais recente da xAI com humor",
                    "release_date": "2024-12-12",
                    "capabilities": ["text", "vision", "function_calling", "humor"],
                    "best_for": ["Conversas casuais", "Análise com humor", "Criatividade"]
                }
            },
            {
                "name": "grok-2-vision-1212",
                "provider": "grok",
                "model_version": "1212",
                "cost_per_token_input": 0.000002,
                "cost_per_token_output": 0.00001,
                "max_tokens_supported": 8192,
                "supports_function_calling": True,
                "supports_vision": True,
                "supports_streaming": True,
                "context_window": 131072,
                "llm_metadata": {
                    "description": "Grok 2 Vision - Versão com capacidades visuais",
                    "release_date": "2024-12-12",
                    "capabilities": ["text", "vision", "function_calling", "humor"],
                    "best_for": ["Análise de imagens", "Multimodal", "Criatividade visual"]
                }
            },
            {
                "name": "grok-beta",
                "provider": "grok",
                "model_version": "beta",
                "cost_per_token_input": 0.000005,
                "cost_per_token_output": 0.000015,
                "max_tokens_supported": 4096,
                "supports_function_calling": False,
                "supports_vision": False,
                "supports_streaming": True,
                "context_window": 131072,
                "llm_metadata": {
                    "description": "Grok Beta - Versão experimental",
                    "release_date": "2024-08-13",
                    "capabilities": ["text", "humor"],
                    "best_for": ["Experimentação", "Conversas casuais"]
                }
            },

            # ========================================
            # DEEPSEEK - Modelos especializados
            # ========================================
            {
                "name": "deepseek-chat",
                "provider": "deepseek",
                "model_version": "latest",
                "cost_per_token_input": 0.00000014,
                "cost_per_token_output": 0.00000028,
                "max_tokens_supported": 4096,
                "supports_function_calling": True,
                "supports_vision": False,
                "supports_streaming": True,
                "context_window": 32768,
                "llm_metadata": {
                    "description": "DeepSeek Chat - Modelo conversacional econômico",
                    "release_date": "2024-01-01",
                    "capabilities": ["text", "function_calling"],
                    "best_for": ["Chat", "Conversas", "Custo baixo"]
                }
            },
            {
                "name": "deepseek-coder",
                "provider": "deepseek",
                "model_version": "latest",
                "cost_per_token_input": 0.00000014,
                "cost_per_token_output": 0.00000028,
                "max_tokens_supported": 4096,
                "supports_function_calling": True,
                "supports_vision": False,
                "supports_streaming": True,
                "context_window": 32768,
                "llm_metadata": {
                    "description": "DeepSeek Coder - Especializado em programação",
                    "release_date": "2024-01-01",
                    "capabilities": ["text", "function_calling", "code"],
                    "best_for": ["Programação", "Debug", "Análise de código"]
                }
            },
            {
                "name": "deepseek-reasoner",
                "provider": "deepseek",
                "model_version": "latest",
                "cost_per_token_input": 0.00000055,
                "cost_per_token_output": 0.0000022,
                "max_tokens_supported": 8192,
                "supports_function_calling": True,
                "supports_vision": False,
                "supports_streaming": True,
                "context_window": 65536,
                "llm_metadata": {
                    "description": "DeepSeek Reasoner - Especializado em raciocínio",
                    "release_date": "2024-11-28",
                    "capabilities": ["text", "function_calling", "reasoning"],
                    "best_for": ["Raciocínio lógico", "Matemática", "Análise complexa"]
                }
            },

            # ========================================
            # META LLAMA - Família Llama 3.x
            # ========================================
            {
                "name": "llama-3.3-70b-instruct",
                "provider": "llama",
                "model_version": "3.3",
                "cost_per_token_input": 0.00000059,
                "cost_per_token_output": 0.00000079,
                "max_tokens_supported": 8192,
                "supports_function_calling": True,
                "supports_vision": False,
                "supports_streaming": True,
                "context_window": 131072,
                "llm_metadata": {
                    "description": "Llama 3.3 70B Instruct - Modelo mais recente da Meta",
                    "release_date": "2024-12-06",
                    "capabilities": ["text", "function_calling", "reasoning"],
                    "best_for": ["Instruções complexas", "Raciocínio", "Open source"]
                }
            },
            {
                "name": "llama-3.2-90b-vision-instruct",
                "provider": "llama",
                "model_version": "3.2",
                "cost_per_token_input": 0.0000009,
                "cost_per_token_output": 0.0000009,
                "max_tokens_supported": 8192,
                "supports_function_calling": True,
                "supports_vision": True,
                "supports_streaming": True,
                "context_window": 131072,
                "llm_metadata": {
                    "description": "Llama 3.2 90B Vision - Modelo multimodal",
                    "release_date": "2024-09-25",
                    "capabilities": ["text", "vision", "function_calling"],
                    "best_for": ["Análise visual", "Multimodal", "Open source"]
                }
            },
            {
                "name": "llama-3.2-11b-vision-instruct",
                "provider": "llama",
                "model_version": "3.2",
                "cost_per_token_input": 0.00000018,
                "cost_per_token_output": 0.00000018,
                "max_tokens_supported": 8192,
                "supports_function_calling": True,
                "supports_vision": True,
                "supports_streaming": True,
                "context_window": 131072,
                "llm_metadata": {
                    "description": "Llama 3.2 11B Vision - Modelo compacto com visão",
                    "release_date": "2024-09-25",
                    "capabilities": ["text", "vision", "function_calling"],
                    "best_for": ["Visão computacional", "Eficiência", "Open source"]
                }
            },
            {
                "name": "llama-3.1-405b-instruct",
                "provider": "llama",
                "model_version": "3.1",
                "cost_per_token_input": 0.000002,
                "cost_per_token_output": 0.000002,
                "max_tokens_supported": 4096,
                "supports_function_calling": True,
                "supports_vision": False,
                "supports_streaming": True,
                "context_window": 131072,
                "llm_metadata": {
                    "description": "Llama 3.1 405B - Maior modelo da Meta",
                    "release_date": "2024-07-23",
                    "capabilities": ["text", "function_calling", "reasoning"],
                    "best_for": ["Tarefas complexas", "Raciocínio avançado", "Open source"]
                }
            },
            {
                "name": "llama-3.1-70b-instruct",
                "provider": "llama",
                "model_version": "3.1",
                "cost_per_token_input": 0.00000059,
                "cost_per_token_output": 0.00000079,
                "max_tokens_supported": 8192,
                "supports_function_calling": True,
                "supports_vision": False,
                "supports_streaming": True,
                "context_window": 131072,
                "llm_metadata": {
                    "description": "Llama 3.1 70B - Modelo equilibrado",
                    "release_date": "2024-07-23",
                    "capabilities": ["text", "function_calling"],
                    "best_for": ["Uso geral", "Custo-benefício", "Open source"]
                }
            },
            {
                "name": "llama-3.1-8b-instruct",
                "provider": "llama",
                "model_version": "3.1",
                "cost_per_token_input": 0.00000018,
                "cost_per_token_output": 0.00000018,
                "max_tokens_supported": 8192,
                "supports_function_calling": True,
                "supports_vision": False,
                "supports_streaming": True,
                "context_window": 131072,
                "llm_metadata": {
                    "description": "Llama 3.1 8B - Modelo compacto e rápido",
                    "release_date": "2024-07-23",
                    "capabilities": ["text", "function_calling"],
                    "best_for": ["Tarefas simples", "Velocidade", "Open source"]
                }
            },

            # ========================================
            # MISTRAL AI - Modelos Mistral
            # ========================================
            {
                "name": "mistral-large-2411",
                "provider": "mistral",
                "model_version": "2411",
                "cost_per_token_input": 0.000002,
                "cost_per_token_output": 0.000006,
                "max_tokens_supported": 8192,
                "supports_function_calling": True,
                "supports_vision": False,
                "supports_streaming": True,
                "context_window": 128000,
                "llm_metadata": {
                    "description": "Mistral Large - Modelo premium da Mistral AI",
                    "release_date": "2024-11-01",
                    "capabilities": ["text", "function_calling", "reasoning"],
                    "best_for": ["Tarefas complexas", "Multilíngue", "Raciocínio"]
                }
            },
            {
                "name": "mistral-small-2409",
                "provider": "mistral",
                "model_version": "2409",
                "cost_per_token_input": 0.0000002,
                "cost_per_token_output": 0.0000006,
                "max_tokens_supported": 8192,
                "supports_function_calling": True,
                "supports_vision": False,
                "supports_streaming": True,
                "context_window": 128000,
                "llm_metadata": {
                    "description": "Mistral Small - Modelo eficiente e econômico",
                    "release_date": "2024-09-01",
                    "capabilities": ["text", "function_calling"],
                    "best_for": ["Uso geral", "Custo-benefício", "Multilíngue"]
                }
            },
            {
                "name": "pixtral-12b-2409",
                "provider": "mistral",
                "model_version": "2409",
                "cost_per_token_input": 0.00000015,
                "cost_per_token_output": 0.00000015,
                "max_tokens_supported": 8192,
                "supports_function_calling": True,
                "supports_vision": True,
                "supports_streaming": True,
                "context_window": 128000,
                "llm_metadata": {
                    "description": "Pixtral 12B - Modelo multimodal da Mistral",
                    "release_date": "2024-09-01",
                    "capabilities": ["text", "vision", "function_calling"],
                    "best_for": ["Análise visual", "Multimodal", "Eficiência"]
                }
            },

            # ========================================
            # COHERE - Modelos Command
            # ========================================
            {
                "name": "command-r-plus-08-2024",
                "provider": "cohere",
                "model_version": "08-2024",
                "cost_per_token_input": 0.0000025,
                "cost_per_token_output": 0.00001,
                "max_tokens_supported": 4096,
                "supports_function_calling": True,
                "supports_vision": False,
                "supports_streaming": True,
                "context_window": 128000,
                "llm_metadata": {
                    "description": "Command R+ - Modelo premium da Cohere",
                    "release_date": "2024-08-01",
                    "capabilities": ["text", "function_calling", "reasoning"],
                    "best_for": ["RAG", "Busca", "Análise de documentos"]
                }
            },
            {
                "name": "command-r-08-2024",
                "provider": "cohere",
                "model_version": "08-2024",
                "cost_per_token_input": 0.00000015,
                "cost_per_token_output": 0.0000006,
                "max_tokens_supported": 4096,
                "supports_function_calling": True,
                "supports_vision": False,
                "supports_streaming": True,
                "context_window": 128000,
                "llm_metadata": {
                    "description": "Command R - Modelo básico da Cohere",
                    "release_date": "2024-08-01",
                    "capabilities": ["text", "function_calling"],
                    "best_for": ["RAG", "Busca", "Análise de documentos"]
                }
            },

            # ========================================
            # OPENAI - Modelos adicionais e finetuned
            # ========================================
            {
                "name": "gpt-4",
                "provider": "openai",
                "model_version": "2023-03-14",
                "cost_per_token_input": 0.00003,
                "cost_per_token_output": 0.00006,
                "max_tokens_supported": 8192,
                "supports_function_calling": True,
                "supports_vision": False,
                "supports_streaming": True,
                "context_window": 8192,
                "llm_metadata": {
                    "description": "GPT-4 - Modelo clássico OpenAI",
                    "release_date": "2023-03-14",
                    "capabilities": ["text", "function_calling"],
                    "best_for": ["Tarefas complexas", "Análise profunda"]
                }
            },
            {
                "name": "gpt-3.5-turbo-16k",
                "provider": "openai",
                "model_version": "2023-06-13",
                "cost_per_token_input": 0.000003,
                "cost_per_token_output": 0.000004,
                "max_tokens_supported": 16384,
                "supports_function_calling": True,
                "supports_vision": False,
                "supports_streaming": True,
                "context_window": 16384,
                "llm_metadata": {
                    "description": "GPT-3.5 Turbo 16k - Contexto expandido",
                    "release_date": "2023-06-13",
                    "capabilities": ["text", "function_calling"],
                    "best_for": ["Documentos longos", "Chat"]
                }
            },

            # ========================================
            # ANTHROPIC - Modelos Claude 2.x, 1.x
            # ========================================
            {
                "name": "claude-2.1",
                "provider": "anthropic",
                "model_version": "2023-11-21",
                "cost_per_token_input": 0.000008,
                "cost_per_token_output": 0.000024,
                "max_tokens_supported": 200000,
                "supports_function_calling": False,
                "supports_vision": False,
                "supports_streaming": True,
                "context_window": 200000,
                "llm_metadata": {
                    "description": "Claude 2.1 - Modelo intermediário da Anthropic",
                    "release_date": "2023-11-21",
                    "capabilities": ["text"],
                    "best_for": ["Análise de texto", "Documentos longos"]
                }
            },
            {
                "name": "claude-2.0",
                "provider": "anthropic",
                "model_version": "2023-07-11",
                "cost_per_token_input": 0.000008,
                "cost_per_token_output": 0.000024,
                "max_tokens_supported": 100000,
                "supports_function_calling": False,
                "supports_vision": False,
                "supports_streaming": True,
                "context_window": 100000,
                "llm_metadata": {
                    "description": "Claude 2.0 - Modelo anterior da Anthropic",
                    "release_date": "2023-07-11",
                    "capabilities": ["text"],
                    "best_for": ["Documentos longos", "Chat"]
                }
            },

            # ========================================
            # GOOGLE - Gemini Ultra, Nano, Pro, Flash
            # ========================================
            {
                "name": "gemini-1.0-ultra",
                "provider": "google",
                "model_version": "2024-01-01",
                "cost_per_token_input": 0.00001,
                "cost_per_token_output": 0.00003,
                "max_tokens_supported": 32768,
                "supports_function_calling": True,
                "supports_vision": True,
                "supports_streaming": True,
                "context_window": 32768,
                "llm_metadata": {
                    "description": "Gemini 1.0 Ultra - Modelo premium Google",
                    "release_date": "2024-01-01",
                    "capabilities": ["text", "vision", "function_calling"],
                    "best_for": ["Tarefas avançadas", "Multimodal"]
                }
            },
            {
                "name": "gemini-1.0-nano",
                "provider": "google",
                "model_version": "2024-01-01",
                "cost_per_token_input": 0.0000001,
                "cost_per_token_output": 0.0000004,
                "max_tokens_supported": 8192,
                "supports_function_calling": False,
                "supports_vision": False,
                "supports_streaming": True,
                "context_window": 8192,
                "llm_metadata": {
                    "description": "Gemini 1.0 Nano - Modelo leve Google",
                    "release_date": "2024-01-01",
                    "capabilities": ["text"],
                    "best_for": ["Dispositivos móveis", "Edge"]
                }
            },

            # ========================================
            # META - Llama 2.x, CodeLlama, Llama Guard
            # ========================================
            {
                "name": "llama-2-70b-chat",
                "provider": "llama",
                "model_version": "2.0",
                "cost_per_token_input": 0.0000005,
                "cost_per_token_output": 0.0000005,
                "max_tokens_supported": 4096,
                "supports_function_calling": False,
                "supports_vision": False,
                "supports_streaming": True,
                "context_window": 4096,
                "llm_metadata": {
                    "description": "Llama 2 70B Chat - Modelo open source Meta",
                    "release_date": "2023-07-18",
                    "capabilities": ["text"],
                    "best_for": ["Chat", "Open source"]
                }
            },
            {
                "name": "codellama-70b-instruct",
                "provider": "llama",
                "model_version": "2.0",
                "cost_per_token_input": 0.0000006,
                "cost_per_token_output": 0.0000006,
                "max_tokens_supported": 4096,
                "supports_function_calling": True,
                "supports_vision": False,
                "supports_streaming": True,
                "context_window": 4096,
                "llm_metadata": {
                    "description": "CodeLlama 70B Instruct - Modelo de código Meta",
                    "release_date": "2023-08-24",
                    "capabilities": ["text", "code", "function_calling"],
                    "best_for": ["Programação", "Open source"]
                }
            },

            # ========================================
            # MISTRAL - Codestral, LeChat, Tiny, etc
            # ========================================
            {
                "name": "codestral-22b",
                "provider": "mistral",
                "model_version": "2024-06-01",
                "cost_per_token_input": 0.000001,
                "cost_per_token_output": 0.000001,
                "max_tokens_supported": 32000,
                "supports_function_calling": True,
                "supports_vision": False,
                "supports_streaming": True,
                "context_window": 32000,
                "llm_metadata": {
                    "description": "Codestral 22B - Modelo de código Mistral",
                    "release_date": "2024-06-01",
                    "capabilities": ["text", "code", "function_calling"],
                    "best_for": ["Programação", "Raciocínio"]
                }
            },
            {
                "name": "lechat-7b",
                "provider": "mistral",
                "model_version": "2024-05-01",
                "cost_per_token_input": 0.0000002,
                "cost_per_token_output": 0.0000002,
                "max_tokens_supported": 8192,
                "supports_function_calling": True,
                "supports_vision": False,
                "supports_streaming": True,
                "context_window": 8192,
                "llm_metadata": {
                    "description": "LeChat 7B - Chatbot open source Mistral",
                    "release_date": "2024-05-01",
                    "capabilities": ["text", "function_calling"],
                    "best_for": ["Chat", "Open source"]
                }
            },

            # ========================================
            # COHERE - Embed, Command, etc
            # ========================================
            {
                "name": "embed-multilingual-v3.0",
                "provider": "cohere",
                "model_version": "2024-06-01",
                "cost_per_token_input": 0.0000001,
                "cost_per_token_output": 0.0000001,
                "max_tokens_supported": 4096,
                "supports_function_calling": False,
                "supports_vision": False,
                "supports_streaming": True,
                "context_window": 4096,
                "llm_metadata": {
                    "description": "Cohere Embed Multilingual v3.0",
                    "release_date": "2024-06-01",
                    "capabilities": ["text", "embedding"],
                    "best_for": ["Embeddings", "Multilíngue"]
                }
            },

            # ========================================
            # AWS BEDROCK - Amazon Titan, Jurassic, Claude Bedrock
            # ========================================
            {
                "name": "amazon-titan-text-express-v1",
                "provider": "aws-bedrock",
                "model_version": "2024-01-01",
                "cost_per_token_input": 0.000001,
                "cost_per_token_output": 0.000001,
                "max_tokens_supported": 8192,
                "supports_function_calling": True,
                "supports_vision": False,
                "supports_streaming": True,
                "context_window": 8192,
                "llm_metadata": {
                    "description": "Amazon Titan Text Express v1",
                    "release_date": "2024-01-01",
                    "capabilities": ["text", "function_calling"],
                    "best_for": ["AWS Bedrock", "Enterprise"]
                }
            },

            # ========================================
            # AZURE OPENAI - Modelos exclusivos Azure
            # ========================================
            {
                "name": "gpt-4-azure",
                "provider": "azure-openai",
                "model_version": "2024-01-01",
                "cost_per_token_input": 0.00003,
                "cost_per_token_output": 0.00006,
                "max_tokens_supported": 8192,
                "supports_function_calling": True,
                "supports_vision": False,
                "supports_streaming": True,
                "context_window": 8192,
                "llm_metadata": {
                    "description": "GPT-4 Azure - Modelo exclusivo Azure OpenAI",
                    "release_date": "2024-01-01",
                    "capabilities": ["text", "function_calling"],
                    "best_for": ["Azure", "Enterprise"]
                }
            },

            # ========================================
            # OLLAMA/LOCALAI - Modelos open source populares
            # ========================================
            {
                "name": "phi-3-mini",
                "provider": "ollama",
                "model_version": "2024-05-01",
                "cost_per_token_input": 0.0,
                "cost_per_token_output": 0.0,
                "max_tokens_supported": 128000,
                "supports_function_calling": True,
                "supports_vision": False,
                "supports_streaming": True,
                "context_window": 128000,
                "llm_metadata": {
                    "description": "Phi-3 Mini - Modelo open source Microsoft",
                    "release_date": "2024-05-01",
                    "capabilities": ["text", "function_calling"],
                    "best_for": ["Open source", "Edge"]
                }
            },
            {
                "name": "dbrx-instruct",
                "provider": "ollama",
                "model_version": "2024-04-01",
                "cost_per_token_input": 0.0,
                "cost_per_token_output": 0.0,
                "max_tokens_supported": 128000,
                "supports_function_calling": True,
                "supports_vision": False,
                "supports_streaming": True,
                "context_window": 128000,
                "llm_metadata": {
                    "description": "DBRX Instruct - Modelo open source Databricks",
                    "release_date": "2024-04-01",
                    "capabilities": ["text", "function_calling"],
                    "best_for": ["Open source", "Enterprise"]
                }
            },

            # ========================================
            # HUGGINGFACE - Falcon, Bloom, MPT, etc
            # ========================================
            {
                "name": "falcon-180b",
                "provider": "huggingface",
                "model_version": "2023-09-01",
                "cost_per_token_input": 0.0,
                "cost_per_token_output": 0.0,
                "max_tokens_supported": 8192,
                "supports_function_calling": False,
                "supports_vision": False,
                "supports_streaming": True,
                "context_window": 8192,
                "llm_metadata": {
                    "description": "Falcon 180B - Modelo open source HuggingFace",
                    "release_date": "2023-09-01",
                    "capabilities": ["text"],
                    "best_for": ["Open source", "Pesquisa"]
                }
            },

            # ========================================
            # GROQ, PERPLEXITY, TOGETHER, OPENROUTER, ETC
            # ========================================
            {
                "name": "mixtral-8x22b",
                "provider": "groq",
                "model_version": "2024-06-01",
                "cost_per_token_input": 0.000001,
                "cost_per_token_output": 0.000001,
                "max_tokens_supported": 128000,
                "supports_function_calling": True,
                "supports_vision": False,
                "supports_streaming": True,
                "context_window": 128000,
                "llm_metadata": {
                    "description": "Mixtral 8x22B - Modelo Groq",
                    "release_date": "2024-06-01",
                    "capabilities": ["text", "function_calling"],
                    "best_for": ["API pública", "Performance"]
                }
            },

            # ========================================
            # MODELOS REGIONAIS/EXPERIMENTAIS
            # ========================================
            {
                "name": "yi-34b-chat",
                "provider": "yi",
                "model_version": "2024-05-01",
                "cost_per_token_input": 0.0,
                "cost_per_token_output": 0.0,
                "max_tokens_supported": 128000,
                "supports_function_calling": True,
                "supports_vision": False,
                "supports_streaming": True,
                "context_window": 128000,
                "llm_metadata": {
                    "description": "Yi 34B Chat - Modelo regional avançado",
                    "release_date": "2024-05-01",
                    "capabilities": ["text", "function_calling"],
                    "best_for": ["Chinês", "Pesquisa"]
                }
            },
            {
                "name": "qwen-72b-chat",
                "provider": "qwen",
                "model_version": "2024-05-01",
                "cost_per_token_input": 0.0,
                "cost_per_token_output": 0.0,
                "max_tokens_supported": 128000,
                "supports_function_calling": True,
                "supports_vision": True,
                "supports_streaming": True,
                "context_window": 128000,
                "llm_metadata": {
                    "description": "Qwen 72B Chat - Modelo regional multimodal",
                    "release_date": "2024-05-01",
                    "capabilities": ["text", "vision", "function_calling"],
                    "best_for": ["Chinês", "Multimodal"]
                }
            },
        ]

        # Atualização inteligente: update se existe, insert se não existe
        created, updated = 0, 0
        for model_data in llms_data:
            existing = db.query(LLM).filter(
                LLM.provider == model_data["provider"],
                LLM.name == model_data["name"],
                LLM.model_version == model_data["model_version"]
            ).first()
            if existing:
                # Atualizar apenas campos relevantes
                for field, value in model_data.items():
                    if field not in ["id", "created_at"]:
                        setattr(existing, field, value)
                updated += 1
            else:
                model = LLM(**model_data)
                db.add(model)
                created += 1
        db.commit()
        print(f"✅ LLMs inseridos: {created} | atualizados: {updated}")

    except Exception as e:
        print(f"❌ Erro ao popular LLMs: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    populate_complete_llms()
