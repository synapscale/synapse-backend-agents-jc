"""Utilitários para gerenciamento de armazenamento."""

import hashlib
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict

import aiofiles


class StorageManager:
    """Gerenciador de armazenamento de arquivos."""

    def __init__(self, base_path: str = "./storage"):
        """Inicializa o gerenciador de armazenamento."""
        self.base_path = Path(base_path)
        self.ensure_directories()

    def ensure_directories(self):
        """Garante que os diretórios necessários existem."""
        categories = ["image", "video", "audio", "document", "archive", "metadata"]
        for category in categories:
            (self.base_path / category).mkdir(parents=True, exist_ok=True)

    async def save_file(
        self, content: bytes, filename: str, category: str, user_id: str
    ) -> Dict[str, str]:
        """Salva arquivo no sistema de armazenamento."""
        # Gerar nome único
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_hash = hashlib.md5(content).hexdigest()[:8]
        stored_name = f"{user_id}_{timestamp}_{file_hash}_{filename}"

        # Caminho completo
        file_path = self.base_path / category / stored_name

        # Salvar arquivo
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(content)

        return {
            "stored_name": stored_name,
            "file_path": str(file_path),
            "checksum": hashlib.md5(content).hexdigest(),
        }


def get_file_category(mime_type: str) -> str:
    """Determina a categoria do arquivo baseada no tipo MIME."""
    if mime_type.startswith("image/"):
        return "image"
    elif mime_type.startswith("video/"):
        return "video"
    elif mime_type.startswith("audio/"):
        return "audio"
    elif mime_type in ["application/zip", "application/x-rar-compressed"]:
        return "archive"
    else:
        return "document"


def get_storage_usage() -> Dict[str, int]:
    """Retorna informações de uso do armazenamento."""
    try:
        total, used, free = shutil.disk_usage("./storage")
        return {
            "total": total,
            "used": used,
            "free": free,
            "usage_percentage": int((used / total) * 100) if total > 0 else 0,
        }
    except Exception:
        return {"total": 0, "used": 0, "free": 0, "usage_percentage": 0}
