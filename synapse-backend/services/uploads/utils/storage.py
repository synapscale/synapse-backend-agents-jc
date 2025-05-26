import os
import uuid
import magic
import aiofiles
from fastapi import UploadFile, HTTPException
from ..models.file import FileMetadata

# Configurações do serviço
UPLOAD_DIR = os.environ.get("UPLOAD_DIR", "/app/storage")
MAX_FILE_SIZE = int(os.environ.get("MAX_FILE_SIZE", 10 * 1024 * 1024))  # 10MB por padrão
ALLOWED_EXTENSIONS = {
    "image": ["jpg", "jpeg", "png", "gif", "webp", "svg"],
    "document": ["pdf", "doc", "docx", "txt", "md", "csv", "xls", "xlsx"],
    "audio": ["mp3", "wav", "ogg"],
    "video": ["mp4", "webm", "avi"],
    "archive": ["zip", "tar", "gz", "rar"]
}

def get_file_category(content_type: str, filename: str) -> str:
    """Determina a categoria do arquivo com base no tipo MIME e extensão."""
    ext = filename.split(".")[-1].lower() if "." in filename else ""
    
    if content_type.startswith("image/"):
        return "image"
    elif content_type.startswith("audio/"):
        return "audio"
    elif content_type.startswith("video/"):
        return "video"
    elif content_type.startswith("application/pdf") or ext == "pdf":
        return "document"
    elif any(ext in ALLOWED_EXTENSIONS[cat] for cat in ALLOWED_EXTENSIONS):
        for cat, exts in ALLOWED_EXTENSIONS.items():
            if ext in exts:
                return cat
    
    return "other"

async def save_file(file: UploadFile, user_id: str) -> FileMetadata:
    """Salva o arquivo no sistema de arquivos e retorna os metadados."""
    # Verificar tamanho do arquivo
    file_size = 0
    content = b""
    
    # Ler o arquivo em chunks para verificar o tamanho
    chunk_size = 1024 * 1024  # 1MB
    while True:
        chunk = await file.read(chunk_size)
        if not chunk:
            break
        content += chunk
        file_size += len(chunk)
        
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"Arquivo muito grande. Tamanho máximo permitido: {MAX_FILE_SIZE} bytes"
            )
    
    # Resetar o cursor do arquivo
    await file.seek(0)
    
    # Verificar o tipo MIME real do arquivo
    mime = magic.Magic(mime=True)
    content_type = mime.from_buffer(content[:1024])
    
    # Gerar ID único para o arquivo
    file_id = str(uuid.uuid4())
    
    # Determinar a categoria do arquivo
    category = get_file_category(content_type, file.filename)
    
    # Criar diretório para a categoria se não existir
    category_dir = os.path.join(UPLOAD_DIR, category)
    os.makedirs(category_dir, exist_ok=True)
    
    # Gerar nome de arquivo seguro
    safe_filename = f"{file_id}_{file.filename.replace(' ', '_')}"
    file_path = os.path.join(category_dir, safe_filename)
    
    # Salvar o arquivo
    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)
    
    # Criar e retornar metadados
    relative_path = os.path.join(category, safe_filename)
    metadata = FileMetadata(
        id=file_id,
        filename=file.filename,
        content_type=content_type,
        size=file_size,
        path=relative_path,
        category=category,
        user_id=user_id,
        metadata={}
    )
    
    # Salvar metadados em um arquivo JSON
    metadata_path = os.path.join(UPLOAD_DIR, "metadata", f"{file_id}.json")
    os.makedirs(os.path.dirname(metadata_path), exist_ok=True)
    
    async with aiofiles.open(metadata_path, "w") as f:
        await f.write(metadata.model_dump_json())
    
    return metadata
