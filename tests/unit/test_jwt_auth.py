"""
Testes unitários para o módulo de autenticação JWT.

Este módulo contém testes unitários para o módulo de autenticação JWT,
garantindo que a geração, decodificação e verificação de tokens funcionem corretamente.
"""

import pytest
import jwt
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from src.synapse.core.auth.jwt import create_access_token, decode_token, verify_token
from src.synapse.config import settings


@pytest.fixture
def mock_user_data():
    """Mock para dados do usuário."""
    return {
        "sub": "user123",
        "name": "Test User",
        "email": "test@example.com",
        "role": "user"
    }


def test_create_access_token(mock_user_data):
    """Testa a criação de token de acesso."""
    # Configurar tempo fixo para teste
    fixed_time = datetime(2025, 1, 1, 12, 0, 0)
    
    with patch("synapse.core.auth.jwt.datetime") as mock_datetime:
        mock_datetime.utcnow.return_value = fixed_time
        
        # Criar token com expiração padrão
        token = create_access_token(data=mock_user_data)
        
        # Decodificar token para verificar conteúdo
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=["HS256"]
        )
        
        # Verificar dados do usuário
        assert payload["sub"] == mock_user_data["sub"]
        assert payload["name"] == mock_user_data["name"]
        assert payload["email"] == mock_user_data["email"]
        assert payload["role"] == mock_user_data["role"]
        
        # Verificar expiração (padrão: 30 minutos)
        expected_exp = int((fixed_time + timedelta(minutes=30)).timestamp())
        assert payload["exp"] == expected_exp
        
        # Verificar data de emissão
        assert payload["iat"] == int(fixed_time.timestamp())


def test_create_access_token_custom_expiry(mock_user_data):
    """Testa a criação de token de acesso com expiração personalizada."""
    # Configurar tempo fixo para teste
    fixed_time = datetime(2025, 1, 1, 12, 0, 0)
    
    with patch("synapse.core.auth.jwt.datetime") as mock_datetime:
        mock_datetime.utcnow.return_value = fixed_time
        
        # Criar token com expiração personalizada (2 horas)
        token = create_access_token(
            data=mock_user_data,
            expires_delta=timedelta(hours=2)
        )
        
        # Decodificar token para verificar conteúdo
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=["HS256"]
        )
        
        # Verificar expiração personalizada
        expected_exp = int((fixed_time + timedelta(hours=2)).timestamp())
        assert payload["exp"] == expected_exp


def test_decode_token_valid():
    """Testa a decodificação de um token válido."""
    # Criar um token válido
    payload = {"sub": "user123", "exp": datetime.utcnow().timestamp() + 3600}
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    
    # Decodificar o token
    decoded = decode_token(token)
    
    # Verificar conteúdo
    assert decoded["sub"] == "user123"


def test_decode_token_expired():
    """Testa a decodificação de um token expirado."""
    # Criar um token expirado
    payload = {"sub": "user123", "exp": datetime.utcnow().timestamp() - 3600}
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    
    # Tentar decodificar o token expirado
    with pytest.raises(jwt.ExpiredSignatureError):
        decode_token(token)


def test_decode_token_invalid():
    """Testa a decodificação de um token inválido."""
    # Criar um token com assinatura inválida
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyMTIzIn0.INVALID_SIGNATURE"
    
    # Tentar decodificar o token inválido
    with pytest.raises(jwt.InvalidTokenError):
        decode_token(token)


def test_verify_token_valid():
    """Testa a verificação de um token válido."""
    # Criar um token válido
    payload = {"sub": "user123", "exp": datetime.utcnow().timestamp() + 3600}
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    
    # Verificar o token
    result = verify_token(token)
    
    # Verificar resultado
    assert result is True


def test_verify_token_expired():
    """Testa a verificação de um token expirado."""
    # Criar um token expirado
    payload = {"sub": "user123", "exp": datetime.utcnow().timestamp() - 3600}
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    
    # Verificar o token expirado
    result = verify_token(token)
    
    # Verificar resultado
    assert result is False


def test_verify_token_invalid():
    """Testa a verificação de um token inválido."""
    # Criar um token com assinatura inválida
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyMTIzIn0.INVALID_SIGNATURE"
    
    # Verificar o token inválido
    result = verify_token(token)
    
    # Verificar resultado
    assert result is False
