"""Gerenciador de armazenamento de arquivos.

Este módulo implementa o gerenciamento de armazenamento de arquivos,
com suporte a diferentes provedores (local, S3, etc).
"""

import hashlib
import logging
import os
import shutil
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Protocol, Union

import aiofiles

from src.synapse.config import settings
from src.synapse.exceptions import StorageError

# Logger
logger = logging.getLogger(__name__)


class StorageProvider(Protocol):
    """Protocolo para provedores de armazenamento."""

    async def save_file(
        self, content: bytes, filename: str, category: str, user_id: str
    ) -> Dict[str, str]:
        """Salva um arquivo no armazenamento.

        Args:
            content: Conteúdo do arquivo em bytes
            filename: Nome original do arquivo
            category: Categoria do arquivo
            user_id: ID do usuário que está fazendo upload

        Returns:
            Dicionário com informações do arquivo salvo

        Raises:
            StorageError: Se houver erro ao salvar o arquivo
        """
        ...

    async def get_file(self, category: str, stored_name: str) -> Optional[bytes]:
        """Recupera o conteúdo de um arquivo.

        Args:
            category: Categoria do arquivo
            stored_name: Nome do arquivo no armazenamento

        Returns:
            Conteúdo do arquivo em bytes ou None se não encontrado

        Raises:
            StorageError: Se houver erro ao ler o arquivo
        """
        ...

    async def delete_file(self, category: str, stored_name: str) -> bool:
        """Remove um arquivo do armazenamento.

        Args:
            category: Categoria do arquivo
            stored_name: Nome do arquivo no armazenamento

        Returns:
            True se o arquivo foi removido com sucesso, False se não existia

        Raises:
            StorageError: Se houver erro ao remover o arquivo
        """
        ...

    async def generate_download_url(self, category: str, stored_name: str) -> str:
        """Gera URL para download do arquivo.

        Args:
            category: Categoria do arquivo
            stored_name: Nome do arquivo no armazenamento

        Returns:
            URL para download do arquivo

        Raises:
            StorageError: Se houver erro ao gerar a URL
        """
        ...


class LocalStorageProvider:
    """Provedor de armazenamento local em disco."""

    def __init__(self, base_path: str = settings.STORAGE_BASE_PATH):
        """Inicializa o provedor de armazenamento local.

        Args:
            base_path: Caminho base para armazenamento de arquivos
        """
        self.base_path = Path(base_path)
        self._ensure_directories()
        logger.info(f"Provedor de armazenamento local inicializado: {base_path}")

    def _ensure_directories(self) -> None:
        """Garante que os diretórios necessários existem."""
        categories = ["image", "video", "audio", "document", "archive", "metadata"]
        for category in categories:
            (self.base_path / category).mkdir(parents=True, exist_ok=True)

    async def save_file(
        self, content: bytes, filename: str, category: str, user_id: str
    ) -> Dict[str, str]:
        """Salva arquivo no sistema de armazenamento local.

        Args:
            content: Conteúdo do arquivo em bytes
            filename: Nome original do arquivo
            category: Categoria do arquivo
            user_id: ID do usuário que está fazendo upload

        Returns:
            Dicionário com informações do arquivo salvo

        Raises:
            StorageError: Se houver erro ao salvar o arquivo
        """
        # Verificar espaço disponível
        if not self._check_available_space(len(content)):
            logger.error(f"Espaço insuficiente para salvar arquivo: {filename}")
            raise StorageError("Espaço de armazenamento insuficiente")

        # Gerar nome único
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_hash = hashlib.md5(content).hexdigest()[:8]
        stored_name = f"{user_id}_{timestamp}_{file_hash}_{filename}"

        # Caminho completo
        file_path = self.base_path / category / stored_name

        # Salvar arquivo
        try:
            async with aiofiles.open(file_path, "wb") as f:
                await f.write(content)

            logger.info(f"Arquivo salvo com sucesso: {file_path}")

            return {
                "stored_name": stored_name,
                "file_path": str(file_path),
                "checksum": hashlib.md5(content).hexdigest(),
            }
        except Exception as e:
            logger.error(f"Erro ao salvar arquivo: {str(e)}")
            raise StorageError(f"Erro ao salvar arquivo: {str(e)}") from e

    async def get_file(self, category: str, stored_name: str) -> Optional[bytes]:
        """Recupera o conteúdo de um arquivo.

        Args:
            category: Categoria do arquivo
            stored_name: Nome do arquivo no armazenamento

        Returns:
            Conteúdo do arquivo em bytes ou None se não encontrado

        Raises:
            StorageError: Se houver erro ao ler o arquivo
        """
        file_path = self.base_path / category / stored_name

        if not file_path.exists():
            logger.warning(f"Arquivo não encontrado: {file_path}")
            return None

        try:
            async with aiofiles.open(file_path, "rb") as f:
                content = await f.read()

            logger.info(f"Arquivo lido com sucesso: {file_path}")
            return content
        except Exception as e:
            logger.error(f"Erro ao ler arquivo: {str(e)}")
            raise StorageError(f"Erro ao ler arquivo: {str(e)}") from e

    async def delete_file(self, category: str, stored_name: str) -> bool:
        """Remove um arquivo do armazenamento.

        Args:
            category: Categoria do arquivo
            stored_name: Nome do arquivo no armazenamento

        Returns:
            True se o arquivo foi removido com sucesso, False se não existia

        Raises:
            StorageError: Se houver erro ao remover o arquivo
        """
        file_path = self.base_path / category / stored_name

        if not file_path.exists():
            logger.warning(f"Tentativa de remover arquivo inexistente: {file_path}")
            return False

        try:
            os.remove(file_path)
            logger.info(f"Arquivo removido com sucesso: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Erro ao remover arquivo: {str(e)}")
            raise StorageError(f"Erro ao remover arquivo: {str(e)}") from e

    async def generate_download_url(self, category: str, stored_name: str) -> str:
        """Gera URL para download do arquivo.

        Em uma implementação real, isso poderia gerar URLs assinadas para S3 ou
        outro serviço de armazenamento. Nesta implementação simplificada,
        retornamos uma URL local.

        Args:
            category: Categoria do arquivo
            stored_name: Nome do arquivo no armazenamento

        Returns:
            URL para download do arquivo

        Raises:
            StorageError: Se houver erro ao gerar a URL
        """
        # Verificar se o arquivo existe
        file_path = self.base_path / category / stored_name
        if not file_path.exists():
            logger.warning(
                f"Tentativa de gerar URL para arquivo inexistente: {file_path}"
            )
            raise StorageError("Arquivo não encontrado")

        # Em produção, isso seria uma URL assinada para S3 ou similar
        # Para esta implementação, usamos uma URL local com token
        token = uuid.uuid4().hex
        base_url = os.environ.get("API_BASE_URL", "http://localhost:8001")
        url = f"{base_url}/download/{category}/{stored_name}?token={token}"

        logger.info(f"URL de download gerada: {url}")
        return url

    def _check_available_space(self, required_size: int) -> bool:
        """Verifica se há espaço disponível para salvar o arquivo.

        Args:
            required_size: Tamanho necessário em bytes

        Returns:
            True se há espaço suficiente, False caso contrário
        """
        try:
            total, used, free = shutil.disk_usage(str(self.base_path))
            # Adicionar margem de segurança (10%)
            safe_free = int(free * 0.9)
            has_space = required_size < safe_free

            if not has_space:
                logger.warning(
                    f"Espaço insuficiente: necessário={required_size}, "
                    f"disponível={free}, seguro={safe_free}"
                )

            return has_space
        except Exception as e:
            logger.error(f"Erro ao verificar espaço disponível: {str(e)}")
            # Em caso de erro, assumir que há espaço
            return True


class StorageManager:
    """Gerenciador de armazenamento que abstrai diferentes provedores."""

    def __init__(self):
        """Inicializa o gerenciador de armazenamento com o provedor configurado."""
        self.provider = self._get_provider()
        logger.info(
            f"Gerenciador de armazenamento inicializado com provedor: {settings.STORAGE_PROVIDER}"
        )

    def _get_provider(self) -> StorageProvider:
        """Obtém o provedor de armazenamento configurado.

        Returns:
            Instância do provedor de armazenamento
        """
        provider_type = settings.STORAGE_PROVIDER.lower()

        if provider_type == "local":
            return LocalStorageProvider()
        # Implementar outros provedores conforme necessário
        # elif provider_type == "s3":
        #     return S3StorageProvider()
        else:
            logger.warning(f"Provedor desconhecido: {provider_type}, usando local")
            return LocalStorageProvider()

    async def save_file(
        self, content: bytes, filename: str, category: str, user_id: str
    ) -> Dict[str, str]:
        """Salva arquivo no sistema de armazenamento.

        Args:
            content: Conteúdo do arquivo em bytes
            filename: Nome original do arquivo
            category: Categoria do arquivo
            user_id: ID do usuário que está fazendo upload

        Returns:
            Dicionário com informações do arquivo salvo

        Raises:
            StorageError: Se houver erro ao salvar o arquivo
        """
        return await self.provider.save_file(content, filename, category, user_id)

    async def get_file(self, category: str, stored_name: str) -> Optional[bytes]:
        """Recupera o conteúdo de um arquivo.

        Args:
            category: Categoria do arquivo
            stored_name: Nome do arquivo no armazenamento

        Returns:
            Conteúdo do arquivo em bytes ou None se não encontrado

        Raises:
            StorageError: Se houver erro ao ler o arquivo
        """
        return await self.provider.get_file(category, stored_name)

    async def delete_file(self, category: str, stored_name: str) -> bool:
        """Remove um arquivo do armazenamento.

        Args:
            category: Categoria do arquivo
            stored_name: Nome do arquivo no armazenamento

        Returns:
            True se o arquivo foi removido com sucesso, False se não existia

        Raises:
            StorageError: Se houver erro ao remover o arquivo
        """
        return await self.provider.delete_file(category, stored_name)

    async def generate_download_url(self, category: str, stored_name: str) -> str:
        """Gera URL para download do arquivo.

        Args:
            category: Categoria do arquivo
            stored_name: Nome do arquivo no armazenamento

        Returns:
            URL para download do arquivo

        Raises:
            StorageError: Se houver erro ao gerar a URL
        """
        return await self.provider.generate_download_url(category, stored_name)


def get_storage_usage() -> Dict[str, int]:
    """Retorna informações de uso do armazenamento.

    Returns:
        Dicionário com informações de uso do armazenamento
    """
    try:
        total, used, free = shutil.disk_usage(settings.STORAGE_BASE_PATH)
        return {
            "total": total,
            "used": used,
            "free": free,
            "usage_percentage": int((used / total) * 100) if total > 0 else 0,
        }
    except Exception as e:
        logger.error(f"Erro ao obter informações de uso do armazenamento: {str(e)}")
        return {"total": 0, "used": 0, "free": 0, "usage_percentage": 0}
