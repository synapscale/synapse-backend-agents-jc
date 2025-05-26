"""
Módulo de teste isolado para rate limiting
"""
import pytest
import time
import asyncio
from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from typing import Dict, Any, Optional, List

# Criar uma aplicação FastAPI de teste
app = FastAPI()

# Configurações de teste
RATE_LIMIT_WINDOW = 60  # segundos
RATE_LIMIT_MAX_REQUESTS = 5  # requisições por janela

# Dicionário para armazenar informações de rate limiting
rate_limit_store = {}

class RateLimiter:
    """
    Implementa rate limiting baseado em IP e usuário.
    """
    # Atributos de classe para permitir modificação nos testes
    max_requests = RATE_LIMIT_MAX_REQUESTS
    window = RATE_LIMIT_WINDOW
    
    def __init__(self, max_requests: int = None, window: int = None):
        # Permitir sobrescrever os valores padrão na instância
        if max_requests is not None:
            self.max_requests = max_requests
        if window is not None:
            self.window = window
    
    async def __call__(self, request: Request, user_id: str = "test_user"):
        # Para testes, usar um IP fixo para garantir consistência
        # Em produção, seria request.client.host
        client_ip = "127.0.0.1"
        key = f"{client_ip}:{user_id}"
        
        # Obter timestamp atual
        now = time.time()
        
        # Inicializar ou limpar entradas antigas
        if key not in rate_limit_store or now - rate_limit_store[key]["start"] > self.window:
            rate_limit_store[key] = {
                "start": now,
                "count": 0
            }
        
        # Incrementar contador
        rate_limit_store[key]["count"] += 1
        
        # Verificar se excedeu o limite
        if rate_limit_store[key]["count"] > self.max_requests:
            # Calcular tempo restante para reset
            reset_time = rate_limit_store[key]["start"] + self.window - now
            
            # Lançar HTTPException para garantir que o FastAPI propague o erro corretamente
            from fastapi import HTTPException
            raise HTTPException(
                status_code=429,
                detail=f"Muitas requisições. Tente novamente em {int(reset_time)} segundos.",
                headers={"Retry-After": str(int(reset_time))}
            )
        
        # Continuar com a requisição
        return {"id": user_id, "ip": client_ip, "request_count": rate_limit_store[key]["count"]}

# Instância do rate limiter para testes
test_rate_limiter = RateLimiter(max_requests=3, window=10)

# Rota de teste para rate limiting
@app.get("/test-rate-limit")
async def test_rate_limit_endpoint(user_info = Depends(test_rate_limiter)):
    # Se o rate limiter retornar JSONResponse, FastAPI o propagará automaticamente
    # Caso contrário, retornar sucesso
    return {"message": "Requisição permitida", "user_info": user_info}

# Cliente de teste
client = TestClient(app)

# Testes
def test_rate_limiting_basic():
    """Testa funcionamento básico do rate limiting."""
    # Limpar store para garantir estado inicial
    rate_limit_store.clear()
    
    # As primeiras 3 requisições devem ser permitidas
    for i in range(3):
        response = client.get("/test-rate-limit")
        assert response.status_code == 200
        assert "Requisição permitida" in response.json()["message"]
        assert response.json()["user_info"]["request_count"] == i + 1
    
    # A quarta requisição deve ser bloqueada
    response = client.get("/test-rate-limit")
    assert response.status_code == 429
    assert "Muitas requisições" in response.json()["detail"]
    assert "Retry-After" in response.headers

def test_rate_limiting_different_users():
    """Testa rate limiting para diferentes usuários."""
    # Limpar store para garantir estado inicial
    rate_limit_store.clear()
    
    # Criar uma rota específica para este teste
    @app.get("/test-rate-limit-users")
    async def test_rate_limit_users(request: Request, user_id: str):
        limiter = RateLimiter(max_requests=2, window=10)
        result = await limiter(request, user_id=user_id)
        if isinstance(result, JSONResponse):
            return result
        return {"message": "Requisição permitida", "user_info": result}
    
    # Usuário 1: primeiras 2 requisições permitidas
    for i in range(2):
        response = client.get("/test-rate-limit-users?user_id=user1")
        assert response.status_code == 200
    
    # Usuário 1: terceira requisição bloqueada
    response = client.get("/test-rate-limit-users?user_id=user1")
    assert response.status_code == 429
    
    # Usuário 2: primeiras 2 requisições permitidas (independente do usuário 1)
    for i in range(2):
        response = client.get("/test-rate-limit-users?user_id=user2")
        assert response.status_code == 200
    
    # Usuário 2: terceira requisição bloqueada
    response = client.get("/test-rate-limit-users?user_id=user2")
    assert response.status_code == 429

def test_rate_limiting_window_reset():
    """Testa reset da janela de rate limiting após o tempo especificado."""
    # Limpar store para garantir estado inicial
    rate_limit_store.clear()
    
    # Criar uma rota com janela curta para teste
    @app.get("/test-rate-limit-reset")
    async def test_rate_limit_reset(request: Request):
        # Janela de apenas 1 segundo para facilitar o teste
        limiter = RateLimiter(max_requests=1, window=1)
        result = await limiter(request)
        if isinstance(result, JSONResponse):
            return result
        return {"message": "Requisição permitida", "user_info": result}
    
    # Primeira requisição permitida
    response = client.get("/test-rate-limit-reset")
    assert response.status_code == 200
    
    # Segunda requisição bloqueada (excedeu o limite)
    response = client.get("/test-rate-limit-reset")
    assert response.status_code == 429
    
    # Esperar a janela expirar (2 segundos para garantir)
    time.sleep(2)
    
    # Após a janela expirar, a próxima requisição deve ser permitida
    response = client.get("/test-rate-limit-reset")
    assert response.status_code == 200

def test_rate_limiting_headers():
    """Testa cabeçalhos de resposta do rate limiting."""
    # Limpar store para garantir estado inicial
    rate_limit_store.clear()
    
    # Consumir o limite
    for i in range(3):
        client.get("/test-rate-limit")
    
    # Verificar cabeçalhos na resposta de erro
    response = client.get("/test-rate-limit")
    assert response.status_code == 429
    assert "Retry-After" in response.headers
    assert int(response.headers["Retry-After"]) > 0

if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
