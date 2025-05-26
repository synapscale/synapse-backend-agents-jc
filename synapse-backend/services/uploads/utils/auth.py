from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from typing import Dict, Any
import os
import jwt
from datetime import datetime, timedelta

# Configuração de autenticação
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Configurações de segurança
SECRET_KEY = os.environ.get("SECRET_KEY", "your-secret-key-for-development-only")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Valida o token JWT e retorna informações do usuário.
    
    Em produção, esta função deve validar o token com o serviço de autenticação.
    Para desenvolvimento, decodificamos o token localmente.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decodificar o token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        
        # Em produção, verificar se o usuário existe no banco de dados
        # Para desenvolvimento, retornamos as informações do token
        return {
            "id": user_id,
            "username": payload.get("username", "unknown"),
            "role": payload.get("role", "user"),
            "scopes": payload.get("scopes", [])
        }
    except jwt.PyJWTError:
        raise credentials_exception

def verify_admin_access(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Verifica se o usuário tem acesso de administrador.
    """
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permissão negada. Acesso de administrador necessário."
        )
    return current_user

def verify_scope(required_scope: str):
    """
    Cria um dependência que verifica se o usuário tem o escopo necessário.
    """
    def _verify_scope(current_user: Dict[str, Any] = Depends(get_current_user)):
        if required_scope not in current_user.get("scopes", []):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permissão negada. Escopo '{required_scope}' necessário."
            )
        return current_user
    
    return _verify_scope

def create_access_token(data: dict, expires_delta: timedelta = None):
    """
    Cria um token JWT com as informações do usuário.
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt
