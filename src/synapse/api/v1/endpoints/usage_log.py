import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional
from synapse.database import get_db
from synapse.models.usage_log import UsageLog
from synapse.models.user import User
from synapse.api.deps import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/", summary="Registrar log de uso")
def create_usage_log(
    log: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Cria um novo log de uso no sistema"""
    try:
        logger.info(f"Criando log de uso para usuário {current_user.id}")

        # Validate log data
        if not log or not isinstance(log, dict):
            logger.warning(
                f"Dados de log inválidos para usuário {current_user.id}: {log}"
            )
            raise HTTPException(
                status_code=400, detail="Dados do log de uso são obrigatórios"
            )

        try:
            # Create usage log entry
            usage_log = UsageLog(**log)
            db.add(usage_log)
            db.commit()
            db.refresh(usage_log)

            # Convert to dict safely
            try:
                result = usage_log.to_dict()
                logger.info(
                    f"Log de uso criado com sucesso para usuário {current_user.id}"
                )
                return result
            except Exception as conversion_error:
                logger.error(
                    f"Erro ao converter log de uso para dict: {str(conversion_error)}"
                )
                # Return basic dict structure as fallback
                return {
                    "id": str(usage_log.id) if hasattr(usage_log, "id") else None,
                    "user_id": (
                        str(getattr(usage_log, "user_id", None))
                        if getattr(usage_log, "user_id", None)
                        else None
                    ),
                    "workspace_id": (
                        str(getattr(usage_log, "workspace_id", None))
                        if getattr(usage_log, "workspace_id", None)
                        else None
                    ),
                    "llm_id": (
                        str(getattr(usage_log, "llm_id", None))
                        if getattr(usage_log, "llm_id", None)
                        else None
                    ),
                    "action": getattr(usage_log, "action", None),
                    "tokens_used": getattr(usage_log, "tokens_used", 0),
                    "cost": getattr(usage_log, "cost", 0.0),
                    "created_at": (
                        str(getattr(usage_log, "created_at", None))
                        if getattr(usage_log, "created_at", None)
                        else None
                    ),
                }

        except Exception as db_error:
            db.rollback()
            logger.error(f"Erro de banco ao criar log de uso: {str(db_error)}")
            raise HTTPException(
                status_code=500, detail="Erro ao salvar log de uso no banco de dados"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Erro inesperado ao criar log de uso para usuário {current_user.id}: {str(e)}"
        )
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get("/", summary="Listar logs de uso")
def list_usage_logs(
    user_id: Optional[UUID] = Query(None),
    workspace_id: Optional[UUID] = Query(None),
    llm_id: Optional[UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lista logs de uso com filtros opcionais"""
    try:
        logger.info(
            f"Listando logs de uso para usuário {current_user.id} - user_id: {user_id}, workspace_id: {workspace_id}, llm_id: {llm_id}"
        )

        try:
            # Build query with filters
            query = db.query(UsageLog)
            if user_id:
                query = query.filter(UsageLog.user_id == user_id)
            if workspace_id:
                query = query.filter(UsageLog.workspace_id == workspace_id)
            if llm_id:
                query = query.filter(UsageLog.llm_id == llm_id)

            # Execute query
            logs = query.order_by(UsageLog.created_at.desc()).limit(100).all()

            # Convert results safely
            try:
                result = []
                for log in logs:
                    try:
                        result.append(log.to_dict())
                    except Exception as log_error:
                        logger.warning(
                            f"Erro ao converter log {getattr(log, 'id', 'unknown')} para dict: {str(log_error)}"
                        )
                        # Add fallback dict
                        result.append(
                            {
                                "id": str(log.id) if hasattr(log, "id") else None,
                                "user_id": (
                                    str(getattr(log, "user_id", None))
                                    if getattr(log, "user_id", None)
                                    else None
                                ),
                                "workspace_id": (
                                    str(getattr(log, "workspace_id", None))
                                    if getattr(log, "workspace_id", None)
                                    else None
                                ),
                                "llm_id": (
                                    str(getattr(log, "llm_id", None))
                                    if getattr(log, "llm_id", None)
                                    else None
                                ),
                                "action": getattr(log, "action", None),
                                "tokens_used": getattr(log, "tokens_used", 0),
                                "cost": getattr(log, "cost", 0.0),
                                "created_at": (
                                    str(getattr(log, "created_at", None))
                                    if getattr(log, "created_at", None)
                                    else None
                                ),
                            }
                        )

                logger.info(
                    f"Retornados {len(result)} logs de uso para usuário {current_user.id}"
                )
                return result

            except Exception as conversion_error:
                logger.error(
                    f"Erro ao converter lista de logs de uso: {str(conversion_error)}"
                )
                return []  # Return empty list as fallback

        except Exception as db_error:
            logger.error(f"Erro de banco ao listar logs de uso: {str(db_error)}")
            raise HTTPException(
                status_code=500, detail="Erro ao buscar logs de uso no banco de dados"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Erro inesperado ao listar logs de uso para usuário {current_user.id}: {str(e)}"
        )
        raise HTTPException(status_code=500, detail="Erro interno do servidor")
