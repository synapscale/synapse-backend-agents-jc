#!/usr/bin/env python
"""
Teste de integração do Memory Bank com o SynapScale Backend
"""
import os
import sys
import logging
import asyncio
from typing import Dict, Any, List

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("memory-bank-test")

async def test_memory_bank():
    """
    Testa a integração do Memory Bank com o SynapScale Backend
    """
    try:
        # Verificar se o Memory Bank está instalado
        try:
            import memory_bank
            logger.info("Memory Bank está instalado")
        except ImportError:
            logger.error("Memory Bank não está instalado. Execute ./install_memory_bank.sh primeiro.")
            return False
        
        # Verificar se o Memory Bank está habilitado
        from memory_bank.integration import is_memory_bank_enabled
        if not is_memory_bank_enabled():
            logger.error("Memory Bank não está habilitado. Configure a variável de ambiente ENABLE_MEMORY_BANK=true.")
            return False
        
        logger.info("Memory Bank está habilitado")
        
        # Importar serviços do Memory Bank
        from memory_bank.services import CollectionService, MemoryService
        
        # Criar uma sessão de banco de dados
        from synapse.database import get_db
        db = await anext(get_db())
        
        # Criar um usuário de teste
        from synapse.models.user import User
        user = User(
            email="test@example.com",
            full_name="Test User",
            is_active=True
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
        logger.info(f"Usuário de teste criado: {user.id}")
        
        # Criar uma coleção de teste
        collection_service = CollectionService(db)
        collection = await collection_service.create({
            "name": "Coleção de Teste",
            "description": "Coleção para teste de integração",
            "user_id": user.id,
            "is_active": True,
            "metadata": {"test": True}
        })
        
        logger.info(f"Coleção de teste criada: {collection.id}")
        
        # Adicionar memórias à coleção
        memory_service = MemoryService(db)
        memories = []
        
        for i in range(5):
            memory = await memory_service.create({
                "collection_id": collection.id,
                "content": f"Memória de teste {i+1}. Esta é uma memória para testar a integração do Memory Bank.",
                "user_id": user.id,
                "metadata": {"index": i},
                "is_active": True
            })
            memories.append(memory)
            logger.info(f"Memória {i+1} criada: {memory.id}")
        
        # Buscar memórias por similaridade
        query = "Teste de integração do Memory Bank"
        results = await memory_service.search({
            "query": query,
            "user_id": user.id,
            "collection_id": collection.id,
            "limit": 3,
            "threshold": 0.5
        })
        
        logger.info(f"Busca por '{query}' retornou {len(results)} resultados")
        for i, result in enumerate(results):
            logger.info(f"Resultado {i+1}: {result.content}")
        
        # Limpar dados de teste
        for memory in memories:
            await memory_service.delete(memory.id)
        
        await collection_service.delete(collection.id)
        
        await db.delete(user)
        await db.commit()
        
        logger.info("Dados de teste limpos com sucesso")
        
        return True
        
    except Exception as e:
        logger.error(f"Erro ao testar Memory Bank: {e}")
        return False

if __name__ == "__main__":
    # Configurar variáveis de ambiente para o teste
    os.environ["ENABLE_MEMORY_BANK"] = "true"
    
    try:
        # Executar o teste
        success = asyncio.run(test_memory_bank())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("Teste cancelado pelo usuário")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Erro não tratado: {e}")
        sys.exit(1)
