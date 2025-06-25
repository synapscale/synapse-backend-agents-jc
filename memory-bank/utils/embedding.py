from typing import Tuple, List, Dict, Any, Optional
import numpy as np
import json
import logging
from synapse.core.config_new import settings

logger = logging.getLogger(__name__)

async def get_embedding(text: str, model: str = None) -> Tuple[List[float], str]:
    """
    Gera embedding para um texto usando o modelo especificado ou o padrão
    
    Args:
        text: Texto para gerar embedding
        model: Modelo específico a ser usado (opcional)
        
    Returns:
        Tuple contendo o embedding (lista de floats) e o nome do modelo usado
    """
    try:
        # Determinar modelo a ser usado
        embedding_model = model or settings.DEFAULT_EMBEDDING_MODEL or "text-embedding-3-small"
        
        # Usar o serviço unificado de LLM para gerar embedding
        from synapse.core.llm.unified_service import UnifiedLLMService
        llm_service = UnifiedLLMService()
        
        # Truncar texto se necessário (limite típico de 8192 tokens)
        max_chars = 32000  # Aproximação conservadora
        if len(text) > max_chars:
            text = text[:max_chars]
        
        # Gerar embedding
        embedding_result = await llm_service.generate_embedding(
            text=text,
            model=embedding_model
        )
        
        # Extrair embedding do resultado
        embedding = embedding_result.get("embedding", [])
        
        # Verificar se o embedding foi gerado corretamente
        if not embedding or not isinstance(embedding, list):
            logger.warning(f"Embedding inválido gerado para texto: {text[:100]}...")
            # Fallback para embedding aleatório (apenas para desenvolvimento)
            embedding = [float(x) for x in np.random.randn(1536)]
            embedding_model = "fallback-random"
        
        return embedding, embedding_model
        
    except Exception as e:
        logger.error(f"Erro ao gerar embedding: {str(e)}")
        # Fallback para embedding aleatório
        embedding = [float(x) for x in np.random.randn(1536)]
        return embedding, "fallback-error"
