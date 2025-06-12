"""Constantes utilizadas no SynapScale Backend."""

from enum import Enum
from typing import Dict, List, Set

# Categorias de arquivos suportadas
FILE_CATEGORIES = {
    "image": ["jpg", "jpeg", "png", "gif", "bmp", "svg", "webp"],
    "video": ["mp4", "avi", "mkv", "mov", "wmv", "flv", "webm"],
    "audio": ["mp3", "wav", "ogg", "m4a", "flac", "aac"],
    "document": ["pdf", "doc", "docx", "txt", "rtf", "odt"],
    "archive": ["zip", "rar", "7z", "tar", "gz", "bz2"],
}

# Tamanhos máximos por categoria (em bytes)
MAX_FILE_SIZES = {
    "image": 10 * 1024 * 1024,  # 10MB
    "video": 500 * 1024 * 1024,  # 500MB
    "audio": 50 * 1024 * 1024,  # 50MB
    "document": 25 * 1024 * 1024,  # 25MB
    "archive": 100 * 1024 * 1024,  # 100MB
}

# Tipos MIME permitidos
ALLOWED_MIME_TYPES: Dict[str, List[str]] = {
    "image": [
        "image/jpeg",
        "image/png",
        "image/gif",
        "image/bmp",
        "image/webp",
        "image/svg+xml",
    ],
    "video": [
        "video/mp4",
        "video/avi",
        "video/mov",
        "video/wmv",
        "video/flv",
        "video/webm",
    ],
    "audio": [
        "audio/mp3",
        "audio/wav",
        "audio/ogg",
        "audio/flac",
        "audio/aac",
        "audio/m4a",
    ],
    "document": [
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/plain",
        "text/csv",
        "application/rtf",
    ],
    "archive": [
        "application/zip",
        "application/x-rar-compressed",
        "application/x-tar",
        "application/gzip",
    ],
}

# Extensões de arquivo perigosas
DANGEROUS_EXTENSIONS = [
    ".exe",
    ".bat",
    ".cmd",
    ".com",
    ".pif",
    ".scr",
    ".vbs",
    ".js",
    ".jar",
    ".app",
    ".deb",
    ".pkg",
    ".dmg",
    ".msi",
]

# Assinaturas de executáveis para detecção
EXECUTABLE_SIGNATURES = [
    b"MZ",  # PE executables
    b"\x7fELF",  # ELF executables
    b"\xca\xfe\xba\xbe",  # Mach-O executables
]

# Configurações de rate limiting
RATE_LIMITS = {"uploads_per_minute": 10, "requests_per_minute": 100, "burst_limit": 20}

# Configurações de segurança
SECURITY_CONFIG = {
    "jwt_algorithm": "HS256",
    "access_token_expire_minutes": 30,
    "refresh_token_expire_days": 7,
}


# Status de processamento de arquivos
class FileStatus(str, Enum):
    """Status de processamento de arquivos."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    DELETED = "deleted"


# Status de processamento de arquivos (dict version para compatibilidade)
FILE_PROCESSING_STATUSES = {
    "PENDING": "pending",
    "PROCESSING": "processing",
    "COMPLETED": "completed",
    "FAILED": "failed",
}

# Códigos de erro HTTP personalizados
HTTP_ERRORS = {
    "FILE_TOO_LARGE": "O arquivo excede o tamanho máximo permitido",
    "INVALID_FILE_TYPE": "Tipo de arquivo não permitido",
    "INVALID_CATEGORY": "Categoria de arquivo inválida",
    "SECURITY_VALIDATION_FAILED": "O arquivo não passou nas validações de segurança",
    "STORAGE_ERROR": "Erro ao armazenar o arquivo",
    "FILE_NOT_FOUND": "Arquivo não encontrado",
    "PERMISSION_DENIED": "Permissão negada para acessar este arquivo",
    "RATE_LIMIT_EXCEEDED": "Limite de requisições excedido. Tente novamente mais tarde",
}

# Configurações de paginação padrão
DEFAULT_PAGE_SIZE = 10
MAX_PAGE_SIZE = 100
