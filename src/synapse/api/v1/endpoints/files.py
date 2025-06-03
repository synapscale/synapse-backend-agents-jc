"""Endpoints para gerenciamento de arquivos.

Este módulo implementa os endpoints da API para upload, download,
listagem e gerenciamento de arquivos.
"""

import logging
from typing import List, Optional
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from src.synapse.constants import FILE_CATEGORIES
from src.synapse.api.deps import get_current_user
from src.synapse.database import get_db
from src.synapse.exceptions import file_validation_exception
from src.synapse.middlewares.rate_limiting import rate_limit
from src.synapse.schemas.file import (
    FileDownloadResponse,
    FileListResponse,
    FileResponse,
    FileUploadResponse,
)
from src.synapse.services.file_service import FileService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    category: str = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
    _rate_limit=Depends(rate_limit),
):
    """
    Realiza o upload de um arquivo para o servidor.
    
    ## Função
    Este endpoint permite enviar arquivos para o servidor, categorizando-os 
    para facilitar a organização e recuperação posterior.
    
    ## Quando Usar
    - Quando precisar armazenar arquivos no servidor
    - Para enviar documentos, imagens ou outros tipos de arquivos
    - Quando precisar associar arquivos a categorias específicas
    
    ## Parâmetros Importantes
    - **category**: Categoria do arquivo (ex: "imagem", "documento", "audio")
    - **file**: O arquivo a ser enviado
    
    ## Resultado Esperado
    Retorna um objeto JSON contendo:
    - ID único do arquivo enviado
    - Nome original do arquivo
    - Tamanho em bytes
    - Tipo MIME
    - URL para download
    - Timestamp de upload
    - Categoria associada
    
    ## Exemplo de Uso
    ```python
    import requests
    
    url = "https://api.synapscale.com/api/v1/files/upload"
    headers = {"Authorization": "Bearer seu_token"}
    
    # Preparar o arquivo e categoria
    files = {"file": open("documento.pdf", "rb")}
    data = {"category": "documento"}
    
    response = requests.post(url, files=files, data=data, headers=headers)
    print(f"Arquivo enviado com ID: {response.json()['id']}")
    ```
    """
    if category not in FILE_CATEGORIES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Categoria inválida"
        )

    file_service = FileService(db)
    return await file_service.upload_file(file, category, current_user.id)


@router.get("/", response_model=FileListResponse)
async def list_files(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    category: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Lista os arquivos do usuário com paginação e filtro por categoria.
    
    ## Função
    Este endpoint retorna uma lista paginada dos arquivos do usuário atual,
    com opção de filtrar por categoria específica.
    
    ## Quando Usar
    - Para visualizar todos os arquivos enviados pelo usuário
    - Quando precisar listar arquivos de uma categoria específica
    - Para implementar uma interface de gerenciamento de arquivos
    
    ## Parâmetros Importantes
    - **page**: Número da página para paginação (começa em 1)
    - **size**: Quantidade de itens por página (entre 1 e 100)
    - **category**: Filtrar por categoria específica (opcional)
    
    ## Resultado Esperado
    Retorna um objeto JSON contendo:
    - Lista de arquivos com seus metadados
    - Informações de paginação (página atual, total de páginas)
    - Total de arquivos encontrados
    
    ## Exemplo de Uso
    ```python
    import requests
    
    url = "https://api.synapscale.com/api/v1/files/"
    headers = {"Authorization": "Bearer seu_token"}
    
    # Listar todos os arquivos (primeira página, 10 itens por página)
    response = requests.get(url, headers=headers)
    
    # Ou filtrar por categoria e página específica
    params = {"category": "imagem", "page": 2, "size": 20}
    response = requests.get(url, params=params, headers=headers)
    
    for file in response.json()["items"]:
        print(f"{file['filename']} - {file['category']} - {file['size']} bytes")
    ```
    """
    file_service = FileService(db)
    return await file_service.list_user_files(current_user.id, page, size, category)


@router.get("/{file_id}", response_model=FileResponse)
async def get_file(
    file_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Obtém informações detalhadas sobre um arquivo específico.
    
    ## Função
    Este endpoint retorna metadados detalhados sobre um arquivo específico,
    identificado pelo seu ID único.
    
    ## Quando Usar
    - Quando precisar verificar detalhes de um arquivo específico
    - Para obter metadados como tamanho, tipo e data de upload
    - Antes de fazer o download, para verificar se é o arquivo correto
    
    ## Parâmetros Importantes
    - **file_id**: ID único do arquivo (UUID)
    
    ## Resultado Esperado
    Retorna um objeto JSON contendo:
    - ID do arquivo
    - Nome original do arquivo
    - Tamanho em bytes
    - Tipo MIME
    - URL para download
    - Timestamp de upload
    - Categoria associada
    
    ## Exemplo de Uso
    ```python
    import requests
    
    file_id = "550e8400-e29b-41d4-a716-446655440000"  # Exemplo de UUID
    url = f"https://api.synapscale.com/api/v1/files/{file_id}"
    headers = {"Authorization": "Bearer seu_token"}
    
    response = requests.get(url, headers=headers)
    file_info = response.json()
    
    print(f"Nome: {file_info['filename']}")
    print(f"Tipo: {file_info['mime_type']}")
    print(f"Tamanho: {file_info['size']} bytes")
    print(f"URL de download: {file_info['download_url']}")
    ```
    """
    file_service = FileService(db)
    return await file_service.get_file(file_id, current_user.id)


@router.get("/{file_id}/download", response_model=FileDownloadResponse)
async def download_file(
    file_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Gera um link de download para um arquivo específico.
    
    ## Função
    Este endpoint gera um URL temporário para download direto de um arquivo,
    identificado pelo seu ID único.
    
    ## Quando Usar
    - Quando precisar baixar um arquivo específico
    - Para compartilhar um link de download temporário
    - Para implementar funcionalidade de download em uma interface
    
    ## Parâmetros Importantes
    - **file_id**: ID único do arquivo (UUID)
    
    ## Resultado Esperado
    Retorna um objeto JSON contendo:
    - URL de download direto para o arquivo
    - Tempo de expiração do link (se aplicável)
    - Informações básicas do arquivo (nome, tipo, tamanho)
    
    ## Exemplo de Uso
    ```python
    import requests
    import webbrowser
    
    file_id = "550e8400-e29b-41d4-a716-446655440000"  # Exemplo de UUID
    url = f"https://api.synapscale.com/api/v1/files/{file_id}/download"
    headers = {"Authorization": "Bearer seu_token"}
    
    response = requests.get(url, headers=headers)
    download_url = response.json()["download_url"]
    
    # Abrir o link de download no navegador
    webbrowser.open(download_url)
    
    # Ou baixar diretamente
    file_content = requests.get(download_url).content
    with open(response.json()["filename"], "wb") as f:
        f.write(file_content)
    ```
    """
    file_service = FileService(db)
    return await file_service.download_file(file_id, current_user.id)


@router.delete("/{file_id}")
async def delete_file(
    file_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Remove permanentemente um arquivo do servidor.
    
    ## Função
    Este endpoint exclui um arquivo específico do servidor, identificado pelo seu ID único.
    A operação é permanente e não pode ser desfeita.
    
    ## Quando Usar
    - Quando precisar remover arquivos desnecessários
    - Para liberar espaço de armazenamento
    - Para implementar funcionalidade de exclusão em uma interface de gerenciamento
    
    ## Parâmetros Importantes
    - **file_id**: ID único do arquivo (UUID)
    
    ## Resultado Esperado
    Retorna um objeto JSON contendo:
    - Mensagem de confirmação da exclusão
    
    ## Exemplo de Uso
    ```python
    import requests
    
    file_id = "550e8400-e29b-41d4-a716-446655440000"  # Exemplo de UUID
    url = f"https://api.synapscale.com/api/v1/files/{file_id}"
    headers = {"Authorization": "Bearer seu_token"}
    
    response = requests.delete(url, headers=headers)
    
    if response.status_code == 200:
        print("Arquivo excluído com sucesso!")
    else:
        print(f"Erro ao excluir arquivo: {response.json()['detail']}")
    ```
    """
    file_service = FileService(db)
    await file_service.delete_file(file_id, current_user.id)
    return {"message": "Arquivo deletado com sucesso"}
