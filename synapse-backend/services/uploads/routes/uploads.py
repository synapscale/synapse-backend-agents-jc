from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, Query, Request
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
from datetime import datetime
import os
import uuid
import aiofiles
import json
from ..models.file import FileMetadata, UploadResponse
from ..utils.auth import get_current_user
from ..utils.storage import save_file, get_file_category
from ..utils.security import RateLimiter, ContentSecurityValidator, AuditLogger, require_scope

router = APIRouter(
    prefix="/uploads",
    tags=["uploads"],
    responses={
        404: {"description": "Not found"},
        400: {"description": "Bad Request"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        429: {"description": "Too Many Requests"}
    },
)

# Criar instância do rate limiter para uploads (mais restritivo)
upload_rate_limiter = RateLimiter(max_requests=30, window=60)

@router.post("/", response_model=UploadResponse)
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    description: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    current_user: dict = Depends(upload_rate_limiter),
):
    """
    Faz upload de um arquivo para o servidor.
    
    - **file**: Arquivo a ser enviado
    - **description**: Descrição opcional do arquivo
    - **tags**: Tags opcionais separadas por vírgula
    """
    # Verificar escopo de escrita explicitamente para garantir resposta 403 correta
    if "uploads:write" not in current_user.get("scopes", []):
        return JSONResponse(
            status_code=403,
            content={"detail": "Permissão negada. Escopo 'uploads:write' necessário."}
        )
    try:
        # Verificar se o arquivo está vazio - garantir que a exceção seja propagada corretamente
        content = await file.read(1)
        if not content:
            # Garantir que a resposta seja 400 Bad Request
            return JSONResponse(
                status_code=400,
                content={"detail": "Arquivo vazio"}
            )
        await file.seek(0)
        
        # Validar nome do arquivo
        original_filename = file.filename
        safe_filename = ContentSecurityValidator.validate_filename(original_filename)
        if safe_filename != original_filename:
            logger.warning(f"Nome de arquivo sanitizado: {original_filename} -> {safe_filename}")
            file.filename = safe_filename
        
        # Ler conteúdo para validação
        content = await file.read()
        file_size = len(content)
        await file.seek(0)
        
        # Verificar tipo MIME real
        mime = magic.Magic(mime=True)
        content_type = mime.from_buffer(content[:1024])
        
        # Validar tipo MIME
        if not ContentSecurityValidator.validate_mime_type(content_type):
            AuditLogger.log_security_event(
                user_id=current_user["id"],
                event_type="invalid_mime_upload",
                details=f"Tentativa de upload de arquivo com tipo MIME não permitido: {content_type}"
            )
            # Garantir que a resposta seja 400 Bad Request
            return JSONResponse(
                status_code=400,
                content={"detail": f"Tipo de arquivo não permitido: {content_type}"}
            )
        
        # Calcular hash para rastreabilidade
        file_hash = ContentSecurityValidator.compute_file_hash(content)
        
        # Verificar malware (simplificado para desenvolvimento)
        is_safe = ContentSecurityValidator.scan_for_malware(content)
        if not is_safe:
            AuditLogger.log_security_event(
                user_id=current_user["id"],
                event_type="malware_upload",
                details=f"Tentativa de upload de arquivo potencialmente malicioso: {file.filename}"
            )
            raise HTTPException(status_code=400, detail="Arquivo potencialmente malicioso detectado")
        
        # Processar tags se fornecidas
        tags_list = tags.split(",") if tags else []
        
        # Salvar o arquivo e obter metadados
        metadata = await save_file(file, current_user["id"])
        
        # Adicionar metadados extras
        metadata.metadata.update({
            "description": description,
            "tags": tags_list,
            "hash": file_hash,
            "original_filename": original_filename
        })
        
        # Atualizar o arquivo de metadados
        metadata_path = os.path.join(os.environ.get("UPLOAD_DIR", "/app/storage"), "metadata", f"{metadata.id}.json")
        async with aiofiles.open(metadata_path, "w") as f:
            await f.write(metadata.model_dump_json())
        
        # Construir URL para o arquivo
        file_url = f"/api/uploads/files/{metadata.id}"
        
        # Registrar evento de auditoria
        AuditLogger.log_access(
            user_id=current_user["id"],
            file_id=metadata.id,
            action="upload",
            success=True,
            details=f"Arquivo {metadata.filename} ({metadata.content_type}, {metadata.size} bytes) enviado com sucesso"
        )
        
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
        AuditLogger.log_access(
            user_id=current_user["id"],
            file_id="unknown",
            action="upload",
            success=False,
            details=f"Erro ao processar upload: {str(e)}"
        )
        raise HTTPException(status_code=500, detail=f"Erro ao processar upload: {str(e)}")

# Criar instância do rate limiter para listagem (menos restritivo)
list_rate_limiter = RateLimiter(max_requests=100, window=60)

@router.get("/", response_model=List[UploadResponse])
async def list_uploads(
    request: Request,
    category: Optional[str] = Query(None, description="Filtrar por categoria"),
    limit: int = Query(100, description="Número máximo de arquivos a retornar"),
    offset: int = Query(0, description="Índice inicial para paginação"),
    current_user: dict = Depends(list_rate_limiter),
    _: dict = Depends(require_scope("uploads:read"))
):
    """
    Lista os arquivos enviados pelo usuário atual.
    
    - **category**: Filtrar por categoria (image, document, audio, video, archive)
    - **limit**: Número máximo de arquivos a retornar
    - **offset**: Índice inicial para paginação
    """
    try:
        # Diretório de metadados
        metadata_dir = os.path.join(os.environ.get("UPLOAD_DIR", "/app/storage"), "metadata")
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
        raise HTTPException(status_code=500, detail=f"Erro ao listar uploads: {str(e)}")

@router.get("/{file_id}", response_model=UploadResponse)
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
        metadata_path = os.path.join(os.environ.get("UPLOAD_DIR", "/app/storage"), "metadata", f"{file_id}.json")
        
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
        raise HTTPException(status_code=500, detail=f"Erro ao obter informações do arquivo: {str(e)}")

@router.delete("/{file_id}")
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
        metadata_path = os.path.join(os.environ.get("UPLOAD_DIR", "/app/storage"), "metadata", f"{file_id}.json")
        
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
            file_path = os.path.join(os.environ.get("UPLOAD_DIR", "/app/storage"), metadata_dict["path"])
            
            # Excluir o arquivo físico
            if os.path.exists(file_path):
                os.remove(file_path)
            
            # Excluir o arquivo de metadados
            os.remove(metadata_path)
            
            return {"message": "Arquivo excluído com sucesso"}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao excluir arquivo: {str(e)}")

@router.post("/{file_id}/share")
async def share_file(
    file_id: str,
    user_ids: List[str] = Form(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Compartilha um arquivo com outros usuários.
    
    - **file_id**: ID único do arquivo
    - **user_ids**: Lista de IDs de usuários com quem compartilhar
    """
    try:
        # Caminho do arquivo de metadados
        metadata_path = os.path.join(os.environ.get("UPLOAD_DIR", "/app/storage"), "metadata", f"{file_id}.json")
        
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
            
            # Atualizar metadados com informações de compartilhamento
            if "shared_with" not in metadata_dict["metadata"]:
                metadata_dict["metadata"]["shared_with"] = []
            
            # Adicionar novos usuários à lista de compartilhamento
            for user_id in user_ids:
                if user_id not in metadata_dict["metadata"]["shared_with"]:
                    metadata_dict["metadata"]["shared_with"].append(user_id)
            
            # Salvar metadados atualizados
            async with aiofiles.open(metadata_path, "w") as f:
                await f.write(json.dumps(metadata_dict))
            
            return {"message": "Arquivo compartilhado com sucesso", "shared_with": metadata_dict["metadata"]["shared_with"]}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao compartilhar arquivo: {str(e)}")

@router.post("/{file_id}/unshare")
async def unshare_file(
    file_id: str,
    user_ids: List[str] = Form(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Remove o compartilhamento de um arquivo com outros usuários.
    
    - **file_id**: ID único do arquivo
    - **user_ids**: Lista de IDs de usuários para remover o compartilhamento
    """
    try:
        # Caminho do arquivo de metadados
        metadata_path = os.path.join(os.environ.get("UPLOAD_DIR", "/app/storage"), "metadata", f"{file_id}.json")
        
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
            
            # Verificar se há informações de compartilhamento
            if "shared_with" not in metadata_dict["metadata"]:
                return {"message": "Arquivo não está compartilhado", "shared_with": []}
            
            # Remover usuários da lista de compartilhamento
            for user_id in user_ids:
                if user_id in metadata_dict["metadata"]["shared_with"]:
                    metadata_dict["metadata"]["shared_with"].remove(user_id)
            
            # Salvar metadados atualizados
            async with aiofiles.open(metadata_path, "w") as f:
                await f.write(json.dumps(metadata_dict))
            
            return {"message": "Compartilhamento removido com sucesso", "shared_with": metadata_dict["metadata"]["shared_with"]}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao remover compartilhamento: {str(e)}")

@router.get("/shared/with-me", response_model=List[UploadResponse])
async def list_shared_with_me(
    limit: int = Query(100, description="Número máximo de arquivos a retornar"),
    offset: int = Query(0, description="Índice inicial para paginação"),
    current_user: dict = Depends(get_current_user)
):
    """
    Lista os arquivos compartilhados com o usuário atual.
    
    - **limit**: Número máximo de arquivos a retornar
    - **offset**: Índice inicial para paginação
    """
    try:
        # Diretório de metadados
        metadata_dir = os.path.join(os.environ.get("UPLOAD_DIR", "/app/storage"), "metadata")
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
                
                # Verificar se o arquivo está compartilhado com o usuário atual
                if "metadata" in metadata_dict and "shared_with" in metadata_dict["metadata"]:
                    if current_user["id"] in metadata_dict["metadata"]["shared_with"]:
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
        raise HTTPException(status_code=500, detail=f"Erro ao listar arquivos compartilhados: {str(e)}")
