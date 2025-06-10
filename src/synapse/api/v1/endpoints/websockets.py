"""
Endpoints WebSocket para monitoramento de execuções em tempo real
Criado por José - O melhor Full Stack do mundo
API WebSocket completa para comunicação real-time
"""

import asyncio
import logging
from typing import Optional, Dict, Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.synapse.database import get_db
from src.synapse.api.deps import get_current_user
from src.synapse.models.user import User
from src.synapse.models.workflow_execution import WorkflowExecution
from src.synapse.core.websockets.execution_manager import execution_websocket_manager
from src.synapse.core.auth.jwt import jwt_manager
from src.synapse.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ws", tags=["WebSocket"])


async def authenticate_websocket(
    websocket: WebSocket,
    token: str,
    db: Session
) -> Optional[User]:
    """
    Autentica um WebSocket usando JWT token
    """
    try:
        # Decodifica o token JWT
        payload = jwt_manager.decode_token(token)
        user_id = payload.get("user_id")
        
        if not user_id:
            return None
        
        # Busca o usuário no banco
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            return None
            
        return user
        
    except Exception as e:
        logger.warning(f"Erro na autenticação WebSocket: {str(e)}")
        return None


async def check_execution_access(
    user: User,
    execution_id: str,
    db: Session
) -> bool:
    """
    Verifica se o usuário tem acesso à execução
    """
    try:
        execution = db.query(WorkflowExecution).filter(
            WorkflowExecution.id == execution_id
        ).first()
        
        if not execution:
            return False
        
        # Verifica se é o dono da execução ou admin
        return execution.user_id == user.id or user.is_admin
        
    except Exception:
        return False


@router.websocket("/execution/{execution_id}")
async def websocket_execution_monitor(
    websocket: WebSocket,
    execution_id: str,
    token: str = Query(..., description="JWT token para autenticação"),
    db: Session = Depends(get_db)
):
    """
    WebSocket para monitorar uma execução específica
    """
    user = None
    
    try:
        # Autentica o usuário
        user = await authenticate_websocket(websocket, token, db)
        if not user:
            await websocket.close(code=4001, reason="Token inválido")
            return
        
        # Verifica acesso à execução
        if not await check_execution_access(user, execution_id, db):
            await websocket.close(code=4003, reason="Acesso negado à execução")
            return
        
        # Conecta ao sistema de monitoramento
        success = await execution_websocket_manager.connect_to_execution(
            websocket=websocket,
            execution_id=execution_id,
            user_id=user.id,
            metadata={
                "user_email": user.email,
                "connection_type": "execution_monitor"
            }
        )
        
        if not success:
            await websocket.close(code=1011, reason="Erro ao conectar")
            return
        
        logger.info(f"WebSocket conectado para execução {execution_id} (usuário {user.id})")
        
        # Loop de escuta para mensagens do cliente
        try:
            while True:
                # Recebe mensagens do cliente (heartbeat, comandos, etc.)
                message = await websocket.receive_text()
                
                # Processa mensagem se necessário
                await _process_client_message(websocket, message, execution_id, user, db)
                
        except WebSocketDisconnect:
            logger.info(f"WebSocket desconectado para execução {execution_id} (usuário {user.id})")
        
    except Exception as e:
        logger.error(f"Erro no WebSocket de execução: {str(e)}")
        try:
            await websocket.close(code=1011, reason="Erro interno")
        except:
            pass
    
    finally:
        # Desconecta do sistema
        if user:
            await execution_websocket_manager.disconnect(websocket)


@router.websocket("/global")
async def websocket_global_monitor(
    websocket: WebSocket,
    token: str = Query(..., description="JWT token para autenticação"),
    db: Session = Depends(get_db)
):
    """
    WebSocket para monitoramento global (admin)
    """
    user = None
    
    try:
        # Autentica o usuário
        user = await authenticate_websocket(websocket, token, db)
        if not user:
            await websocket.close(code=4001, reason="Token inválido")
            return
        
        # Verifica se é admin
        if not user.is_admin:
            await websocket.close(code=4003, reason="Acesso negado - apenas admins")
            return
        
        # Conecta ao sistema de monitoramento global
        success = await execution_websocket_manager.connect_global(
            websocket=websocket,
            user_id=user.id,
            metadata={
                "user_email": user.email,
                "connection_type": "global_monitor",
                "is_admin": True
            }
        )
        
        if not success:
            await websocket.close(code=1011, reason="Erro ao conectar")
            return
        
        logger.info(f"WebSocket global conectado (admin {user.id})")
        
        # Loop de escuta para mensagens do cliente
        try:
            while True:
                message = await websocket.receive_text()
                await _process_admin_message(websocket, message, user, db)
                
        except WebSocketDisconnect:
            logger.info(f"WebSocket global desconectado (admin {user.id})")
        
    except Exception as e:
        logger.error(f"Erro no WebSocket global: {str(e)}")
        try:
            await websocket.close(code=1011, reason="Erro interno")
        except:
            pass
    
    finally:
        if user:
            await execution_websocket_manager.disconnect(websocket)


@router.websocket("/user")
async def websocket_user_monitor(
    websocket: WebSocket,
    token: str = Query(..., description="JWT token para autenticação"),
    db: Session = Depends(get_db)
):
    """
    WebSocket para monitorar todas as execuções do usuário
    """
    user = None
    
    try:
        # Autentica o usuário
        user = await authenticate_websocket(websocket, token, db)
        if not user:
            await websocket.close(code=4001, reason="Token inválido")
            return
        
        # Conecta como global mas filtra por usuário
        success = await execution_websocket_manager.connect_global(
            websocket=websocket,
            user_id=user.id,
            metadata={
                "user_email": user.email,
                "connection_type": "user_monitor",
                "filter_user_id": user.id
            }
        )
        
        if not success:
            await websocket.close(code=1011, reason="Erro ao conectar")
            return
        
        logger.info(f"WebSocket de usuário conectado (usuário {user.id})")
        
        # Loop de escuta
        try:
            while True:
                message = await websocket.receive_text()
                await _process_user_message(websocket, message, user, db)
                
        except WebSocketDisconnect:
            logger.info(f"WebSocket de usuário desconectado (usuário {user.id})")
        
    except Exception as e:
        logger.error(f"Erro no WebSocket de usuário: {str(e)}")
        try:
            await websocket.close(code=1011, reason="Erro interno")
        except:
            pass
    
    finally:
        if user:
            await execution_websocket_manager.disconnect(websocket)


async def _process_client_message(
    websocket: WebSocket,
    message: str,
    execution_id: str,
    user: User,
    db: Session
):
    """
    Processa mensagens do cliente para execução específica
    """
    try:
        import json
        data = json.loads(message)
        
        message_type = data.get("type")
        
        if message_type == "heartbeat":
            # Responde ao heartbeat
            await websocket.send_text(json.dumps({
                "type": "heartbeat_response",
                "timestamp": data.get("timestamp"),
                "server_time": asyncio.get_event_loop().time()
            }))
            
        elif message_type == "get_stats":
            # Retorna estatísticas da execução
            stats = await execution_websocket_manager.get_execution_stats(execution_id)
            await websocket.send_text(json.dumps({
                "type": "stats_response",
                "data": stats
            }))
            
        elif message_type == "subscribe_logs":
            # Ativa/desativa logs detalhados
            # Implementar se necessário
            pass
            
    except Exception as e:
        logger.warning(f"Erro ao processar mensagem do cliente: {str(e)}")


async def _process_admin_message(
    websocket: WebSocket,
    message: str,
    user: User,
    db: Session
):
    """
    Processa mensagens do admin no monitoramento global
    """
    try:
        import json
        data = json.loads(message)
        
        message_type = data.get("type")
        
        if message_type == "get_global_stats":
            # Retorna estatísticas globais
            stats = await execution_websocket_manager.get_global_stats()
            await websocket.send_text(json.dumps({
                "type": "global_stats_response",
                "data": stats
            }))
            
        elif message_type == "get_execution_list":
            # Retorna lista de execuções ativas
            executions = db.query(WorkflowExecution).filter(
                WorkflowExecution.status.in_(["running", "pending"])
            ).all()
            
            execution_list = []
            for execution in executions:
                stats = await execution_websocket_manager.get_execution_stats(execution.id)
                execution_list.append({
                    "id": execution.id,
                    "workflow_id": execution.workflow_id,
                    "user_id": execution.user_id,
                    "status": execution.status,
                    "started_at": execution.started_at.isoformat() if execution.started_at else None,
                    "connections": stats.get("active_connections", 0)
                })
            
            await websocket.send_text(json.dumps({
                "type": "execution_list_response",
                "data": execution_list
            }))
            
    except Exception as e:
        logger.warning(f"Erro ao processar mensagem do admin: {str(e)}")


async def _process_user_message(
    websocket: WebSocket,
    message: str,
    user: User,
    db: Session
):
    """
    Processa mensagens do usuário no monitoramento pessoal
    """
    try:
        import json
        data = json.loads(message)
        
        message_type = data.get("type")
        
        if message_type == "get_my_executions":
            # Retorna execuções do usuário
            executions = db.query(WorkflowExecution).filter(
                WorkflowExecution.user_id == user.id,
                WorkflowExecution.status.in_(["running", "pending"])
            ).all()
            
            execution_list = []
            for execution in executions:
                stats = await execution_websocket_manager.get_execution_stats(execution.id)
                execution_list.append({
                    "id": execution.id,
                    "workflow_id": execution.workflow_id,
                    "status": execution.status,
                    "started_at": execution.started_at.isoformat() if execution.started_at else None,
                    "connections": stats.get("active_connections", 0)
                })
            
            await websocket.send_text(json.dumps({
                "type": "my_executions_response",
                "data": execution_list
            }))
            
    except Exception as e:
        logger.warning(f"Erro ao processar mensagem do usuário: {str(e)}")


# Endpoints HTTP para informações sobre WebSockets

@router.get("/stats/global")
async def get_websocket_global_stats(
    current_user: User = Depends(get_current_user)
):
    """
    Retorna estatísticas globais dos WebSockets (apenas admin)
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="Acesso negado - apenas admins"
        )
    
    stats = await execution_websocket_manager.get_global_stats()
    return {
        "success": True,
        "data": stats
    }


@router.get("/stats/execution/{execution_id}")
async def get_websocket_execution_stats(
    execution_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retorna estatísticas de uma execução específica
    """
    # Verifica acesso à execução
    if not await check_execution_access(current_user, execution_id, db):
        raise HTTPException(
            status_code=403,
            detail="Acesso negado à execução"
        )
    
    stats = await execution_websocket_manager.get_execution_stats(execution_id)
    return {
        "success": True,
        "data": stats
    }

