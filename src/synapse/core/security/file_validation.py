"""Utilitários para validação e segurança de arquivos.

Este módulo contém funções para validação, sanitização e verificação
de segurança de arquivos enviados pelos usuários.
"""

import io
import logging
import os
import re
from typing import Dict, List, Optional, Tuple

from PIL import Image

from src.synapse.config import settings
from src.synapse.constants import (
    ALLOWED_MIME_TYPES,
    DANGEROUS_EXTENSIONS,
    EXECUTABLE_SIGNATURES,
)
from src.synapse.exceptions import FileValidationError, file_validation_exception

# Logger
logger = logging.getLogger(__name__)


class SecurityValidator:
    """Validador de segurança para arquivos."""

    def __init__(self, max_file_size: int = settings.MAX_UPLOAD_SIZE):
        """Inicializa o validador de segurança.

        Args:
            max_file_size: Tamanho máximo de arquivo em bytes
        """
        self.max_file_size = max_file_size
        logger.info(
            f"Inicializando validador de segurança com tamanho máximo: {max_file_size} bytes"
        )

    async def validate_file_safety(
        self,
        content: bytes,
        filename: str,
        mime_type: str,
        category: Optional[str] = None,
    ) -> bool:
        """Verifica se um arquivo é seguro baseado em várias validações.

        Args:
            content: Conteúdo do arquivo em bytes
            filename: Nome original do arquivo
            mime_type: Tipo MIME do arquivo
            category: Categoria do arquivo (opcional)

        Returns:
            True se o arquivo for seguro, False caso contrário

        Raises:
            FileValidationError: Se o arquivo não passar nas validações
        """
        try:
            # Validar tamanho
            if not self._validate_file_size(len(content)):
                logger.warning(f"Arquivo {filename} rejeitado: tamanho excede o limite")
                raise FileValidationError(
                    f"O arquivo excede o tamanho máximo de {self.max_file_size/1024/1024:.1f}MB"
                )

            # Determinar categoria se não fornecida
            if not category:
                category = self._get_file_category(mime_type)

            # Validar tipo MIME
            if not self._validate_mime_type(mime_type, category):
                logger.warning(
                    f"Arquivo {filename} rejeitado: tipo MIME não permitido: {mime_type}"
                )
                raise FileValidationError(f"Tipo de arquivo não permitido: {mime_type}")

            # Validar extensão
            if self._has_dangerous_extension(filename):
                logger.warning(f"Arquivo {filename} rejeitado: extensão perigosa")
                raise FileValidationError("Extensão de arquivo não permitida")

            # Detectar executáveis disfarçados
            if self._detect_disguised_executable(content):
                logger.warning(
                    f"Arquivo {filename} rejeitado: executável disfarçado detectado"
                )
                raise FileValidationError("Arquivo executável detectado")

            # Validar estrutura se for imagem
            if category == "image" and not self._validate_image_structure(content):
                logger.warning(
                    f"Arquivo {filename} rejeitado: estrutura de imagem inválida"
                )
                raise FileValidationError("Estrutura de imagem inválida")

            logger.info(f"Arquivo {filename} validado com sucesso")
            return True

        except FileValidationError:
            # Repassar exceções de validação
            raise
        except Exception as e:
            # Capturar outras exceções
            logger.error(f"Erro ao validar arquivo {filename}: {str(e)}")
            raise FileValidationError(f"Erro ao validar arquivo: {str(e)}")

    def _validate_file_size(self, size: int) -> bool:
        """Verifica se o tamanho do arquivo está dentro dos limites.

        Args:
            size: Tamanho do arquivo em bytes

        Returns:
            True se o tamanho for válido, False caso contrário
        """
        return 0 < size <= self.max_file_size

    def _validate_mime_type(self, mime_type: str, category: str) -> bool:
        """Valida se o tipo MIME é permitido para a categoria.

        Args:
            mime_type: Tipo MIME do arquivo
            category: Categoria do arquivo

        Returns:
            True se o tipo MIME for permitido, False caso contrário
        """
        allowed_types = ALLOWED_MIME_TYPES.get(category, [])
        return mime_type in allowed_types

    def _get_file_category(self, mime_type: str) -> str:
        """Determina a categoria do arquivo baseada no tipo MIME.

        Args:
            mime_type: Tipo MIME do arquivo

        Returns:
            Categoria do arquivo (image, video, audio, document, archive)
        """
        if mime_type.startswith("image/"):
            return "image"
        elif mime_type.startswith("video/"):
            return "video"
        elif mime_type.startswith("audio/"):
            return "audio"
        elif mime_type in [
            "application/zip",
            "application/x-rar-compressed",
            "application/x-tar",
            "application/gzip",
        ]:
            return "archive"
        else:
            return "document"

    def _has_dangerous_extension(self, filename: str) -> bool:
        """Verifica se o arquivo tem uma extensão perigosa.

        Args:
            filename: Nome do arquivo

        Returns:
            True se a extensão for perigosa, False caso contrário
        """
        _, ext = os.path.splitext(filename.lower())
        return ext in DANGEROUS_EXTENSIONS

    def _detect_disguised_executable(self, content: bytes) -> bool:
        """Detecta tentativas de executáveis disfarçados.

        Args:
            content: Conteúdo do arquivo em bytes

        Returns:
            True se for detectado um executável, False caso contrário
        """
        # Verificar assinaturas de executáveis
        for signature in EXECUTABLE_SIGNATURES:
            if content.startswith(signature):
                return True

        return False

    def _validate_image_structure(self, content: bytes) -> bool:
        """Valida estrutura de arquivo de imagem.

        Args:
            content: Conteúdo do arquivo em bytes

        Returns:
            True se a estrutura for válida, False caso contrário
        """
        try:
            with Image.open(io.BytesIO(content)) as img:
                img.verify()
            return True
        except Exception as e:
            logger.warning(f"Validação de estrutura de imagem falhou: {str(e)}")
            return False


def sanitize_filename(filename: str) -> str:
    """Sanitiza nome do arquivo removendo caracteres perigosos.

    Args:
        filename: Nome original do arquivo

    Returns:
        Nome sanitizado
    """
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
    """Extrai metadados seguros do arquivo.

    Args:
        file_path: Caminho do arquivo

    Returns:
        Dicionário com metadados
    """
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
    except Exception as e:
        logger.error(f"Erro ao extrair metadados do arquivo {file_path}: {str(e)}")

    return metadata
