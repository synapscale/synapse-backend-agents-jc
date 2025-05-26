from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form, Header, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from typing import List, Optional, Dict, Any
from datetime import datetime
import os
import uuid
import aiofiles
import magic
import json
from pydantic import BaseModel, Field
import logging
from services.uploads.utils.security import RateLimiter, ContentSecurityValidator, AuditLogger, create_audit_middleware, require_scope

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicialização da aplicação
app = FastAPI(
    title="SynapScale Uploads Service",
    description="Serviço de gerenciamento de uploads para a plataforma SynapScale",
    version="0.1.0"
)

# Configuração de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ.get("ALLOWED_ORIGINS", "*").split(","),  # Em produção, especificar origens permitidas
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

# Adicionar middleware de auditoria
app.middleware("http")(create_audit_middleware())

# Configuração de autenticação
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Configurações do serviço
UPLOAD_DIR = os.environ.get("UPLOAD_DIR", "/tmp/uploads")
MAX_FILE_SIZE = int(os.environ.get("MAX_FILE_SIZE", 10 * 1024 * 1024))  # 10MB por padrão
ALLOWED_EXTENSIONS = {
    "image": ["jpg", "jpeg", "png", "gif", "webp", "svg"],
    "document": ["pdf", "doc", "docx", "txt", "md", "csv", "xls", "xlsx"],
    "audio": ["mp3", "wav", "ogg"],
    "video": ["mp4", "webm", "avi"],
    "archive": ["zip", "tar", "gz", "rar"]
}

# Modelos de dados
class FileMetadata(BaseModel):
    id: str = Field(..., description="ID único do arquivo")
    filename: str = Field(..., description="Nome original do arquivo")
    content_type: str = Field(..., description="Tipo MIME do arquivo")
    size: int = Field(..., description="Tamanho do arquivo em bytes")
    path: str = Field(..., description="Caminho relativo do arquivo no storage")
    category: str = Field(..., description="Categoria do arquivo (image, document, etc.)")
    user_id: str = Field(..., description="ID do usuário que fez o upload")
    created_at: datetime = Field(default_factory=datetime.now, description="Data de criação")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadados adicionais")

class UploadResponse(BaseModel):
    file_id: str = Field(..., description="ID único do arquivo")
    filename: str = Field(..., description="Nome original do arquivo")
    content_type: str = Field(..., description="Tipo MIME do arquivo")
    size: int = Field(..., description="Tamanho do arquivo em bytes")
    url: str = Field(..., description="URL para acessar o arquivo")
    category: str = Field(..., description="Categoria do arquivo")
    created_at: datetime = Field(..., description="Data de criação")

# Funções auxiliares
from services.uploads.utils.auth import get_current_user

def get_file_category(content_type: str, filename: str) -> str:
    """Determina a categoria do arquivo com base no tipo MIME e extensão."""
    ext = filename.split(".")[-1].lower() if "." in filename else ""

    # Priorizar extensão permitida
    for cat, exts in ALLOWED_EXTENSIONS.items():
        if ext in exts:
            return cat

    if content_type.startswith("image/"):
        return "image"
    elif content_type.startswith("audio/"):
        return "audio"
    elif content_type.startswith("video/"):
        return "video"
    elif content_type.startswith("application/pdf"):
        return "document"

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
        created_at=datetime.now(),
        metadata={}
    )
    
    # Salvar metadados em um arquivo JSON
    metadata_path = os.path.join(UPLOAD_DIR, "metadata", f"{file_id}.json")
    os.makedirs(os.path.dirname(metadata_path), exist_ok=True)
    
    async with aiofiles.open(metadata_path, "w") as f:
        await f.write(metadata.model_dump_json())
    
    return metadata

# Rotas
@app.get("/health")
async def health_check():
    """Verifica a saúde do serviço."""
    return {"status": "ok", "service": "uploads"}

@app.post("/uploads", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    description: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    current_user: dict = Depends(get_current_user),
    _: dict = Depends(require_scope("uploads:write")),
    rate_limiter: Any = Depends(RateLimiter)
):
    """
    Faz upload de um arquivo para o servidor.
    
    - **file**: Arquivo a ser enviado
    - **description**: Descrição opcional do arquivo
    - **tags**: Tags opcionais separadas por vírgula
    """
    try:
        # Verificar se o arquivo está vazio
        if await file.read(1) == b'':
            raise HTTPException(status_code=400, detail="Arquivo vazio")
        await file.seek(0)

        # Ler conteúdo para validação de tipo MIME
        content = await file.read()
        await file.seek(0)
        mime = magic.Magic(mime=True)
        content_type = mime.from_buffer(content[:1024])

        # Validar tipo MIME: só aceita imagens, documentos, áudio, vídeo, arquivos compactados
        if not ContentSecurityValidator.validate_mime_type(content_type, ["image", "document", "audio", "video", "archive"]):
            raise HTTPException(status_code=400, detail="Tipo de arquivo não permitido")

        # Processar tags se fornecidas
        tags_list = tags.split(",") if tags else []

        # Salvar o arquivo e obter metadados
        metadata = await save_file(file, current_user["id"])

        # Adicionar metadados extras
        if description or tags_list:
            metadata.metadata.update({
                "description": description,
                "tags": tags_list
            })
            # Atualizar o arquivo de metadados
            metadata_path = os.path.join(UPLOAD_DIR, "metadata", f"{metadata.id}.json")
            async with aiofiles.open(metadata_path, "w") as f:
                await f.write(metadata.model_dump_json())

        # Construir URL para o arquivo
        file_url = f"/api/uploads/files/{metadata.id}"

        # Retornar resposta
        return UploadResponse(
            file_id=metadata.id,
            filename=metadata.filename,
            content_type=metadata.content_type,
            size=metadata.size,
            url=file_url,
            category=metadata.category,
            created_at=metadata.created_at
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao processar upload: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao processar upload: {str(e)}")

@app.get("/uploads", response_model=List[UploadResponse])
async def list_uploads(
    category: Optional[str] = Query(None, description="Filtrar por categoria"),
    limit: int = Query(100, description="Número máximo de arquivos a retornar"),
    offset: int = Query(0, description="Índice inicial para paginação"),
    current_user: dict = Depends(get_current_user)
):
    """
    Lista os arquivos enviados pelo usuário atual.
    
    - **category**: Filtrar por categoria (image, document, audio, video, archive)
    - **limit**: Número máximo de arquivos a retornar
    - **offset**: Índice inicial para paginação
    """
    try:
        # Diretório de metadados
        metadata_dir = os.path.join(UPLOAD_DIR, "metadata")
        os.makedirs(metadata_dir, exist_ok=True)
        
        # Lista para armazenar os resultados
        results = []
        
        # Iterar sobre os arquivos de metadados
        for filename in os.listdir(metadata_dir):
            if not filename.endswith(".json"):
                continue
            
            # Ler o arquivo de metadados
            file_path = os.path.join(metadata_dir, filename)
            async with aiofiles.open(file_path, "r") as f:
                content = await f.read()
                metadata_dict = json.loads(content)
                
                # Verificar se o arquivo pertence ao usuário atual
                if metadata_dict["user_id"] != current_user["id"]:
                    continue
                
                # Aplicar filtro de categoria se fornecido
                if category and metadata_dict["category"] != category:
                    continue
                
                # Construir URL para o arquivo
                file_url = f"/api/uploads/files/{metadata_dict['id']}"
                
                # Adicionar à lista de resultados
                results.append(UploadResponse(
                    file_id=metadata_dict["id"],
                    filename=metadata_dict["filename"],
                    content_type=metadata_dict["content_type"],
                    size=metadata_dict["size"],
                    url=file_url,
                    category=metadata_dict["category"],
                    created_at=datetime.fromisoformat(metadata_dict["created_at"])
                ))
        
        # Aplicar paginação
        paginated_results = results[offset:offset + limit]
        
        return paginated_results
    
    except Exception as e:
        logger.error(f"Erro ao listar uploads: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao listar uploads: {str(e)}")

@app.get("/uploads/{file_id}", response_model=UploadResponse)
async def get_upload(
    file_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Obtém informações sobre um arquivo específico.
    
    - **file_id**: ID único do arquivo
    """
    try:
        # Caminho do arquivo de metadados
        metadata_path = os.path.join(UPLOAD_DIR, "metadata", f"{file_id}.json")
        
        # Verificar se o arquivo existe
        if not os.path.exists(metadata_path):
            raise HTTPException(status_code=404, detail="Arquivo não encontrado")
        
        # Ler o arquivo de metadados
        async with aiofiles.open(metadata_path, "r") as f:
            content = await f.read()
            metadata_dict = json.loads(content)
            
            # Verificar se o arquivo pertence ao usuário atual
            if metadata_dict["user_id"] != current_user["id"]:
                raise HTTPException(status_code=403, detail="Acesso negado")
            
            # Construir URL para o arquivo
            file_url = f"/api/uploads/files/{metadata_dict['id']}"
            
            # Retornar resposta
            return UploadResponse(
                file_id=metadata_dict["id"],
                filename=metadata_dict["filename"],
                content_type=metadata_dict["content_type"],
                size=metadata_dict["size"],
                url=file_url,
                category=metadata_dict["category"],
                created_at=datetime.fromisoformat(metadata_dict["created_at"])
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter informações do arquivo: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao obter informações do arquivo: {str(e)}")

@app.delete("/uploads/{file_id}")
async def delete_upload(
    file_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Exclui um arquivo específico.
    
    - **file_id**: ID único do arquivo
    """
    try:
        # Caminho do arquivo de metadados
        metadata_path = os.path.join(UPLOAD_DIR, "metadata", f"{file_id}.json")
        
        # Verificar se o arquivo existe
        if not os.path.exists(metadata_path):
            raise HTTPException(status_code=404, detail="Arquivo não encontrado")
        
        # Ler o arquivo de metadados
        async with aiofiles.open(metadata_path, "r") as f:
            content = await f.read()
            metadata_dict = json.loads(content)
            
            # Verificar se o arquivo pertence ao usuário atual
            if metadata_dict["user_id"] != current_user["id"]:
                raise HTTPException(status_code=403, detail="Acesso negado")
            
            # Caminho do arquivo físico
            file_path = os.path.join(UPLOAD_DIR, metadata_dict["path"])
            
            # Excluir o arquivo físico
            if os.path.exists(file_path):
                os.remove(file_path)
            
            # Excluir o arquivo de metadados
            os.remove(metadata_path)
            
            return {"message": "Arquivo excluído com sucesso"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao excluir arquivo: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao excluir arquivo: {str(e)}")

# Inicialização
@app.on_event("startup")
async def startup_event():
    """Executa ações na inicialização do serviço."""
    # Criar diretórios necessários
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    os.makedirs(os.path.join(UPLOAD_DIR, "metadata"), exist_ok=True)
    for category in ALLOWED_EXTENSIONS.keys():
        os.makedirs(os.path.join(UPLOAD_DIR, category), exist_ok=True)
    
    logger.info(f"Serviço de uploads iniciado. Diretório de uploads: {UPLOAD_DIR}")

# Ponto de entrada para execução direta
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)
