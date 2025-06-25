from typing import Tuple, List, Dict, Any, Optional
import numpy as np
import json
import logging
from synapse.core.config import settings

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
        
        # TODO: Implementar geração de embedding real via OpenAI/outros provedores
        # Por enquanto, usar fallback para embedding determinístico baseado no hash do texto
        logger.info(f"Gerando embedding para texto de {len(text)} caracteres usando modelo {embedding_model}")
        
        # Truncar texto se necessário
        max_chars = 32000
        if len(text) > max_chars:
            text = text[:max_chars]
        
        # Gerar embedding determinístico baseado no hash do texto
        import hashlib
        text_hash = hashlib.md5(text.encode()).hexdigest()
        
        # Converter hash em embedding de 1536 dimensões (padrão OpenAI)
        embedding = []
        for i in range(1536):
            # Usar caracteres do hash de forma cíclica para gerar valores determinísticos
            char_index = i % len(text_hash)
            # Converter caractere hex para valor entre -1 e 1
            hex_val = int(text_hash[char_index], 16)
            normalized_val = (hex_val - 7.5) / 7.5  # Normalizar para [-1, 1]
            embedding.append(float(normalized_val))
        
        logger.info(f"Embedding gerado com {len(embedding)} dimensões usando método determinístico")
        return embedding, f"{embedding_model}-deterministic"
        
    except Exception as e:
        logger.error(f"Erro ao gerar embedding: {str(e)}")
        # Fallback para embedding aleatório
        embedding = [float(x) for x in np.random.randn(1536)]
        return embedding, "fallback-error"
