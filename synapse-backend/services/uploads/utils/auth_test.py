"""
Módulo de teste isolado para autenticação e autorização usando pytest-asyncio
"""
import pytest
import jwt
import asyncio
from datetime import datetime, timedelta
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.testclient import TestClient
from typing import Dict, Any, Optional

# Configurações de teste
SECRET_KEY = "test_secret_key"
ALGORITHM = "HS256"

# Criar uma aplicação FastAPI de teste
app = FastAPI()

# Esquema de segurança para extrair o token do cabeçalho Authorization
security = HTTPBearer()

# Função para criar tokens JWT de teste
def create_test_token(user_id="test_user", username="testuser", scopes=None, role="user", expires_delta=None):
    """Cria um token JWT de teste."""
    if scopes is None:
        scopes = ["uploads:read", "uploads:write"]
    
    payload = {
        "sub": user_id,
        "username": username,
        "role": role,
        "scopes": scopes
    }
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=30)
    
    payload["exp"] = expire
    
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

# Implementação simplificada da função get_current_user para testes
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Valida o token JWT e retorna informações do usuário."""
    try:
        token = credentials.credentials
        # Decodificar o token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Credenciais inválidas")
        
        return {
            "id": user_id,
            "username": payload.get("username", "unknown"),
            "role": payload.get("role", "user"),
            "scopes": payload.get("scopes", [])
        }
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Erro de autenticação: {str(e)}")

# Implementação da função require_scope para testes
def require_scope(required_scope: str):
    """Verifica se o usuário tem o escopo necessário."""
    async def _require_scope(current_user: Dict[str, Any] = Depends(get_current_user)):
        if required_scope not in current_user.get("scopes", []):
            raise HTTPException(
                status_code=403,
                detail=f"Permissão negada. Escopo '{required_scope}' necessário."
            )
        return current_user
    return _require_scope

# Rota de teste para verificar escopo de leitura
@app.get("/test-read")
async def test_read_endpoint(current_user: Dict[str, Any] = Depends(require_scope("uploads:read"))):
    return {"message": "Acesso de leitura permitido", "user": current_user}

# Rota de teste para verificar escopo de escrita
@app.get("/test-write")
async def test_write_endpoint(current_user: Dict[str, Any] = Depends(require_scope("uploads:write"))):
    return {"message": "Acesso de escrita permitido", "user": current_user}

# Rota de teste para verificar escopo inexistente
@app.get("/test-admin")
async def test_admin_endpoint(current_user: Dict[str, Any] = Depends(require_scope("admin"))):
    return {"message": "Acesso de administrador permitido", "user": current_user}

# Cliente de teste
client = TestClient(app)

# Testes
def test_valid_token_with_read_scope():
    """Testa acesso com token válido e escopo de leitura."""
    token = create_test_token(scopes=["uploads:read"])
    headers = {"Authorization": f"Bearer {token}"}
    
    # Deve permitir acesso à rota de leitura
    response = client.get("/test-read", headers=headers)
    assert response.status_code == 200
    assert "Acesso de leitura permitido" in response.json()["message"]
    
    # Deve negar acesso à rota de escrita
    response = client.get("/test-write", headers=headers)
    assert response.status_code == 403
    assert "Permissão negada" in response.json()["detail"]
    assert "uploads:write" in response.json()["detail"]

def test_valid_token_with_write_scope():
    """Testa acesso com token válido e escopo de escrita."""
    token = create_test_token(scopes=["uploads:write"])
    headers = {"Authorization": f"Bearer {token}"}
    
    # Deve negar acesso à rota de leitura
    response = client.get("/test-read", headers=headers)
    assert response.status_code == 403
    assert "Permissão negada" in response.json()["detail"]
    
    # Deve permitir acesso à rota de escrita
    response = client.get("/test-write", headers=headers)
    assert response.status_code == 200
    assert "Acesso de escrita permitido" in response.json()["message"]

def test_valid_token_with_both_scopes():
    """Testa acesso com token válido e ambos os escopos."""
    token = create_test_token(scopes=["uploads:read", "uploads:write"])
    headers = {"Authorization": f"Bearer {token}"}
    
    # Deve permitir acesso à rota de leitura
    response = client.get("/test-read", headers=headers)
    assert response.status_code == 200
    
    # Deve permitir acesso à rota de escrita
    response = client.get("/test-write", headers=headers)
    assert response.status_code == 200

def test_invalid_token():
    """Testa acesso com token inválido."""
    headers = {"Authorization": "Bearer invalid_token"}
    
    # Deve negar acesso a qualquer rota
    response = client.get("/test-read", headers=headers)
    assert response.status_code == 401
    assert "Credenciais inválidas" in response.json()["detail"]

def test_missing_token():
    """Testa acesso sem token."""
    # Deve negar acesso a qualquer rota
    response = client.get("/test-read")
    assert response.status_code == 403  # Erro de autenticação (token obrigatório)

def test_expired_token():
    """Testa acesso com token expirado."""
    # Criar token que expirou há 1 hora
    token = create_test_token(expires_delta=timedelta(hours=-1))
    headers = {"Authorization": f"Bearer {token}"}
    
    # Deve negar acesso a qualquer rota
    response = client.get("/test-read", headers=headers)
    assert response.status_code == 401
    assert "Credenciais inválidas" in response.json()["detail"]

def test_nonexistent_scope():
    """Testa acesso a rota com escopo inexistente."""
    token = create_test_token(scopes=["uploads:read", "uploads:write"])
    headers = {"Authorization": f"Bearer {token}"}
    
    # Deve negar acesso à rota de administrador
    response = client.get("/test-admin", headers=headers)
    assert response.status_code == 403
    assert "Permissão negada" in response.json()["detail"]
    assert "admin" in response.json()["detail"]

if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
