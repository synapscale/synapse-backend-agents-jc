from typing import List, Dict, Any, Tuple, Optional
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import logging

logger = logging.getLogger(__name__)

def vector_similarity(v1: List[float], v2: List[float]) -> float:
    """
    Calcula a similaridade de cosseno entre dois vetores
    
    Args:
        v1: Primeiro vetor
        v2: Segundo vetor
        
    Returns:
        Valor de similaridade entre 0 e 1
    """
    try:
        # Converter para arrays numpy
        v1_array = np.array(v1).reshape(1, -1)
        v2_array = np.array(v2).reshape(1, -1)
        
        # Calcular similaridade
        sim = cosine_similarity(v1_array, v2_array)[0][0]
        
        # Garantir que o resultado está entre 0 e 1
        return float(max(0.0, min(1.0, sim)))
    except Exception as e:
        logger.error(f"Erro ao calcular similaridade vetorial: {str(e)}")
        return 0.0

def search_similar_vectors(
    query_embedding: List[float],
    items: List[Any],
    min_score: float = 0.7,
    limit: int = 10,
    embedding_attr: str = "embedding"
) -> List[Tuple[Any, float]]:
    """
    Busca itens com embeddings similares ao embedding da consulta
    
    Args:
        query_embedding: Embedding da consulta
        items: Lista de objetos com atributo de embedding
        min_score: Pontuação mínima de similaridade (0-1)
        limit: Número máximo de resultados
        embedding_attr: Nome do atributo que contém o embedding
        
    Returns:
        Lista de tuplas (item, score) ordenada por similaridade
    """
    try:
        results = []
        
        for item in items:
            # Obter embedding do item
            item_embedding = getattr(item, embedding_attr, None)
            
            # Pular itens sem embedding
            if not item_embedding:
                continue
            
            # Calcular similaridade
            score = vector_similarity(query_embedding, item_embedding)
            
            # Adicionar à lista se atingir pontuação mínima
            if score >= min_score:
                results.append((item, score))
        
        # Ordenar por similaridade (decrescente)
        results.sort(key=lambda x: x[1], reverse=True)
        
        # Limitar número de resultados
        return results[:limit]
        
    except Exception as e:
        logger.error(f"Erro na busca vetorial: {str(e)}")
        return []

def batch_similarity_matrix(embeddings: List[List[float]]) -> np.ndarray:
    """
    Calcula matriz de similaridade para um conjunto de embeddings
    
    Args:
        embeddings: Lista de embeddings
        
    Returns:
        Matriz numpy com valores de similaridade
    """
    try:
        # Converter para array numpy
        embeddings_array = np.array(embeddings)
        
        # Calcular matriz de similaridade
        similarity_matrix = cosine_similarity(embeddings_array)
        
        return similarity_matrix
        
    except Exception as e:
        logger.error(f"Erro ao calcular matriz de similaridade: {str(e)}")
        # Retornar matriz vazia em caso de erro
        return np.array([])
