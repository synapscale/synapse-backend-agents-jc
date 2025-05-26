from fastapi import Request, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional, List, Callable
import time
import os
import logging
import re
import hashlib
from datetime import datetime, timedelta
import jwt
from services.uploads.utils.auth import get_current_user

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurações de segurança
SECRET_KEY = os.environ.get("SECRET_KEY", "your-secret-key-for-development-only")
ALGORITHM = "HS256"
RATE_LIMIT_WINDOW = int(os.environ.get("RATE_LIMIT_WINDOW", 60))  # 60 segundos
RATE_LIMIT_MAX_REQUESTS = int(os.environ.get("RATE_LIMIT_MAX_REQUESTS", 100))  # 100 requisições por janela
ALLOWED_MIME_TYPES = {
    "image": ["image/jpeg", "image/png", "image/gif", "image/webp", "image/svg+xml"],
    "document": [
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/markdown",
        "text/csv",
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "text/x-csv"
    ],
    "audio": ["audio/mpeg", "audio/wav", "audio/ogg"],
    "video": ["video/mp4", "video/webm", "video/avi"],
    "archive": ["application/zip", "application/x-tar", "application/gzip", "application/x-rar-compressed"]
}

# Dicionário para armazenar informações de rate limiting
# Em produção, isso deve ser armazenado em Redis ou similar
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
    
    async def __call__(self, request: Request, current_user: Dict[str, Any] = Depends(get_current_user)):
        user_id = current_user.get("id", "anonymous")
        # Permitir simulação de IP em testes e uso real
        client_ip = request.headers.get("x-forwarded-for") or request.client.host
        key = f"{client_ip}:{user_id}"

        now = time.time()
        if key not in rate_limit_store or now - rate_limit_store[key]["start"] > self.window:
            rate_limit_store[key] = {
                "start": now,
                "count": 0
            }
        rate_limit_store[key]["count"] += 1
        if rate_limit_store[key]["count"] > self.max_requests:
            logger.warning(f"Rate limit excedido para {key}. Requisições: {rate_limit_store[key]['count']}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Muitas requisições. Tente novamente mais tarde."
            )
        return current_user

class ContentSecurityValidator:
    """
    Valida a segurança do conteúdo de arquivos.
    """
    @staticmethod
    def validate_filename(filename: str) -> str:
        """
        Valida e sanitiza o nome do arquivo.
        """
        # Remover caracteres potencialmente perigosos
        sanitized = re.sub(r'[^\w\-\.]', '_', filename)
        
        # Garantir que o nome não comece com ponto (arquivos ocultos)
        if sanitized.startswith('.'):
            sanitized = f"file_{sanitized}"
        
        return sanitized
    
    @staticmethod
    def validate_mime_type(mime_type: str, allowed_categories: Optional[List[str]] = None) -> bool:
        """
        Valida se o tipo MIME é permitido.
        """
        if allowed_categories:
            # Verificar apenas nas categorias especificadas
            allowed_mimes = []
            for category in allowed_categories:
                if category in ALLOWED_MIME_TYPES:
                    allowed_mimes.extend(ALLOWED_MIME_TYPES[category])
            
            return mime_type in allowed_mimes
        else:
            # Verificar em todas as categorias
            return any(mime_type in mimes for mimes in ALLOWED_MIME_TYPES.values())
    
    @staticmethod
    def compute_file_hash(content: bytes) -> str:
        """
        Calcula o hash SHA-256 do conteúdo do arquivo.
        """
        return hashlib.sha256(content).hexdigest()
    
    @staticmethod
    def scan_for_malware(content: bytes) -> bool:
        """
        Verifica se o conteúdo contém malware.
        
        Em produção, isso deve integrar com um serviço de antivírus.
        Para desenvolvimento, retornamos True (seguro).
        """
        # Implementação simplificada para desenvolvimento
        # Em produção, integrar com ClamAV, VirusTotal, etc.
        return True

class AuditLogger:
    """
    Registra eventos de auditoria para operações sensíveis.
    """
    @staticmethod
    def log_access(user_id: str, file_id: str, action: str, success: bool, details: Optional[str] = None):
        """
        Registra um evento de acesso a arquivo.
        """
        event = {
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "file_id": file_id,
            "action": action,
            "success": success,
            "details": details
        }
        
        # Em produção, enviar para sistema de log centralizado
        logger.info(f"AUDIT: {event}")
    
    @staticmethod
    def log_security_event(user_id: str, event_type: str, details: Optional[str] = None):
        """
        Registra um evento de segurança.
        """
        event = {
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "event_type": event_type,
            "details": details
        }
        
        # Em produção, enviar para sistema de log centralizado
        logger.warning(f"SECURITY: {event}")

def create_audit_middleware():
    """
    Cria um middleware para auditoria de requisições.
    """
    async def audit_middleware(request: Request, call_next):
        # Extrair informações da requisição
        path = request.url.path
        method = request.method
        client_ip = request.client.host
        
        # Registrar início da requisição
        start_time = time.time()
        
        # Processar a requisição
        try:
            response = await call_next(request)
            
            # Registrar requisição bem-sucedida
            process_time = time.time() - start_time
            logger.info(f"Request: {method} {path} - Status: {response.status_code} - IP: {client_ip} - Time: {process_time:.4f}s")
            
            return response
        except Exception as e:
            # Registrar erro
            process_time = time.time() - start_time
            logger.error(f"Request: {method} {path} - Error: {str(e)} - IP: {client_ip} - Time: {process_time:.4f}s")
            raise
    
    return audit_middleware

def require_scope(required_scope: str):
    """
    Dependência que verifica se o usuário tem o escopo necessário.
    """
    async def _require_scope(current_user: Dict[str, Any] = Depends(get_current_user)):
        scopes = current_user.get("scopes", [])
        if required_scope not in scopes:
            # Registrar tentativa de acesso não autorizado
            AuditLogger.log_security_event(
                user_id=current_user.get("id", "unknown"),
                event_type="unauthorized_scope_access",
                details=f"Tentativa de acesso sem escopo necessário: {required_scope}"
            )
            
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permissão negada. Escopo '{required_scope}' necessário."
            )
        return current_user
    
    return _require_scope

def validate_content_security(validator_func: Callable):
    """
    Decorator para validar a segurança do conteúdo.
    """
    async def wrapper(*args, **kwargs):
        # Executar validação
        is_valid, message = await validator_func(*args, **kwargs)
        
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=message
            )
        
        # Continuar com a função original
        return await validator_func(*args, **kwargs)
    
    return wrapper
