import io

"""Utilitários de segurança para validação e sanitização."""

import io
import os
import re
import subprocess
from typing import Dict, List, Optional, Tuple

import magic
from PIL import Image

# Configurações de segurança
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
ALLOWED_MIME_TYPES = {
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


class MalwareDetector:
    """Classe para detecção de malware usando ClamAV."""

    def __init__(self, enabled: bool = True):
        """Inicializa o detector de malware."""
        self.enabled = enabled

    async def scan_file(self, file_path: str) -> Tuple[bool, str]:
        """Escaneia arquivo em busca de malware."""
        if not self.enabled:
            return True, "Escaneamento desabilitado"

        try:
            result = subprocess.run(
                ["clamscan", "--no-summary", file_path],
                capture_output=True,
                text=True,
                timeout=30,
            )
            is_clean = result.returncode == 0
            message = "Arquivo limpo" if is_clean else "Malware detectado"
            return is_clean, message
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return True, "Scanner não disponível"


async def validate_file_safety(
    content: bytes, filename: str, mime_type: str, category: str = "document"
) -> bool:
    """Verifica se um arquivo é seguro baseado em várias validações."""
    # Validar tamanho
    if not validate_file_size(len(content)):
        return False

    # Validar tipo MIME
    if not validate_mime_type(mime_type, category):
        return False

    # Detectar tipo real do arquivo
    real_type = detect_file_type(content)
    if not real_type:
        return False

    # Validar estrutura se for imagem
    if category == "image" and not validate_image_structure(content):
        return False

    # Detectar executáveis disfarçados
    if detect_disguised_executable(content, filename):
        return False

    return True


def validate_mime_type(mime_type: str, category: str = "document") -> bool:
    """Valida se o tipo MIME é permitido."""
    allowed_types = ALLOWED_MIME_TYPES.get(category, [])
    return mime_type in allowed_types


def validate_file_size(size: int, max_size: int = MAX_FILE_SIZE) -> bool:
    """Verifica se o tamanho do arquivo está dentro dos limites."""
    return 0 < size <= max_size


def detect_file_type(content: bytes) -> Optional[str]:
    """Detecta tipo de arquivo baseado no conteúdo."""
    try:
        return magic.from_buffer(content, mime=True)
    except Exception:
        return None


def validate_image_structure(content: bytes) -> bool:
    """Valida estrutura de arquivo de imagem."""
    try:
        with Image.open(io.BytesIO(content)) as img:
            img.verify()
        return True
    except Exception:
        return False


def detect_disguised_executable(content: bytes, filename: str) -> bool:
    """Detecta tentativas de executáveis disfarçados."""
    # Verificar assinaturas de executáveis
    exe_signatures = [
        b"MZ",  # PE executables
        b"\x7fELF",  # ELF executables
        b"\xca\xfe\xba\xbe",  # Mach-O executables
    ]

    for signature in exe_signatures:
        if content.startswith(signature):
            return True

    return False


def sanitize_filename(filename: str) -> str:
    """Sanitiza nome do arquivo removendo caracteres perigosos."""
    # Remover caracteres perigosos
    filename = re.sub(r'[<>:"/\|?*]', "", filename)

    # Remover caracteres de controle
    filename = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", filename)

    # Limitar tamanho
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[: 255 - len(ext)] + ext

    return filename


def extract_safe_metadata(file_path: str) -> Dict[str, str]:
    """Extrai metadados seguros do arquivo."""
    metadata = {}

    try:
        stat = os.stat(file_path)
        metadata.update(
            {
                "size": str(stat.st_size),
                "created": str(stat.st_ctime),
                "modified": str(stat.st_mtime),
            }
        )
    except Exception:
        pass

    return metadata


def get_dangerous_extensions() -> List[str]:
    """Lista de extensões de arquivos perigosos."""
    return [
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


class SecurityValidator:
    """Validador de segurança principal."""

    def __init__(self):
        """Inicializa o validador."""
        self.malware_detector = MalwareDetector()

    async def validate_file_safety(
        self, content: bytes, filename: str, mime_type: str
    ) -> bool:
        """Valida segurança completa do arquivo."""
        return await validate_file_safety(content, filename, mime_type)


def get_storage_info() -> Dict[str, int]:
    """Obtém informações sobre uso de armazenamento."""
    try:
        statvfs = os.statvfs("./storage")
        total = statvfs.f_frsize * statvfs.f_blocks
        free = statvfs.f_frsize * statvfs.f_available
        used = total - free

        return {
            "total": total,
            "used": used,
            "free": free,
            "usage_percentage": int((used / total) * 100) if total > 0 else 0,
        }
    except Exception:
        return {"total": 0, "used": 0, "free": 0, "usage_percentage": 0}
