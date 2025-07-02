"""
Endpoints completos de autenticação e autorização
"""

import logging
import secrets
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional
import time

from fastapi import APIRouter, Depends, HTTPException, status, Form, Request
from fastapi.security import OAuth2PasswordRequestForm, HTTPBasicCredentials
from sqlalchemy.orm import Session

from synapse.api.deps import (
    get_current_user,
    get_current_active_user,
    get_current_user_basic,
)
from synapse.core.auth.jwt import jwt_manager
from synapse.core.email.service import email_service
from synapse.database import get_db
from synapse.models.user import User
from synapse.models.refresh_token import RefreshToken
from synapse.models.password_reset_token import PasswordResetToken
from synapse.models.email_verification_token import EmailVerificationToken
from synapse.schemas.auth import (
    UserCreate,
    UserResponse,
    UserLogin,
    Token,
    RefreshTokenRequest,
    PasswordResetRequest,
    PasswordResetConfirm,
    EmailVerificationRequest,
    UserRegister,
)
from synapse.services.user_defaults import create_user_defaults

logger = logging.getLogger(__name__)
router = APIRouter()


# ==================== HELPER FUNCTIONS ====================


def wrap_data_response(data: Any, message: str = "Success", request: Request = None) -> Dict[str, Any]:
    """Wrap data in standardized response format."""
    return {
        "status": "success",
        "message": message,
        "data": data,
        "request_id": getattr(request.state, "request_id", None) if request else None,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def wrap_empty_response(message: str = "Operation completed successfully", request: Request = None) -> Dict[str, Any]:
    """Wrap empty responses in standardized format."""
    return {
        "status": "success", 
        "message": message,
        "request_id": getattr(request.state, "request_id", None) if request else None,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.post(
    "/docs-login",
    response_model=Dict[str, Any],
    summary="🔐 Login para Documentação Swagger",
    description="""
    **Endpoint especial para facilitar o login na documentação Swagger**
    
    ## 📝 Como usar na documentação:
    
    ### ✅ Método Recomendado (2 passos):
    
    #### Passo 1: Obter Token
    1. **Clique no botão "Authorize"** 🔓 no topo da documentação
    2. **No modal de autorização**:
       - Encontre a seção **"HTTPBasic"**
       - Digite seu **email** no campo "Username"
       - Digite sua **senha** no campo "Password"  
       - Clique em **"Authorize"** nesta seção
    3. **Execute este endpoint** (/auth/docs-login) para obter o token JWT
    
    #### Passo 2: Usar Token
    4. **Copie o `access_token`** da resposta
    5. **No modal de autorização**:
       - Encontre a seção **"HTTPBearer"**
       - Cole o token no campo "Value"
       - Clique em **"Authorize"** nesta seção
    6. **Pronto!** Agora você pode usar todos os endpoints
    
    ## 🔄 Fluxo Alternativo:
    
    Use diretamente o endpoint `/auth/login` com form data se preferir.
    
    ## ⚠️ Importante:
    
    - Use **HTTPBasic** apenas para este endpoint
    - Use **HTTPBearer** para todos os outros endpoints
    - O token expira em 30 minutos
    """,
    dependencies=[],  # Remove security dependency to use explicit basic auth
    responses={
        200: {"description": "Login realizado com sucesso"},
        401: {"description": "Credenciais inválidas"},
    },
)
async def docs_login(
    request: Request,
    user: User = Depends(get_current_user_basic),
    db: Session = Depends(get_db),
):
    try:
        # Criar tokens JWT para o usuário
        access_token = jwt_manager.create_access_token(
            data={"user_id": str(user.id), "sub": user.email}
        )
        refresh_token = jwt_manager.create_refresh_token(str(user.id), db)

        logger.info(f"Login via documentação realizado: {user.email}")

        token_data = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": jwt_manager.access_token_expire_minutes * 60,
            "user": {
                "id": str(user.id),
                "email": user.email,
                "name": user.name,
                "is_active": user.is_active,
                "is_verified": user.is_verified,
            },
        }

        return wrap_data_response(
            data=token_data,
            message="Login via documentação realizado com sucesso",
            request=request,
        )

    except Exception as e:
        logger.error(f"Erro no login via documentação: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno no servidor",
        )


@router.post(
    "/register",
    response_model=Dict[str, Any],
    status_code=status.HTTP_201_CREATED,
    summary="Registrar novo usuário",
    response_description="Usuário registrado com sucesso"
)
async def register_user(
    request: Request,
    user_data: UserCreate,
    db: Session = Depends(get_db),
):
    """
    Registra um novo usuário na plataforma.

    - **email**: Email do usuário (único)
    - **username**: Nome de usuário (único)
    - **full_name**: Nome completo
    - **password**: Senha forte

    Exemplo de corpo de requisição:
    ```json
    {
      "email": "usuario@exemplo.com",
      "username": "joao_silva",
      "full_name": "João Silva",
      "password": "SenhaForte123!"
    }
    ```
    """
    # Verificar se email já existe
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        logger.info(f"Tentativa de registro duplicado para email: {user_data.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já está registrado",
        )

    # Verificar se username já existe
    existing_username = (
        db.query(User).filter(User.username == user_data.username).first()
    )
    if existing_username:
        logger.info(
            f"Tentativa de registro duplicado para username: {user_data.username}"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username já está em uso",
        )

    try:
        # Criar novo usuário
        user = User(
            email=user_data.email,
            username=user_data.username,
            full_name=user_data.full_name,
        )
        user.set_password(user_data.password)
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"Usuário criado com sucesso: {user.email} (ID: {user.id})")

        # Criar dados padrão para o novo usuário (workspace individual + plano FREE)
        try:
            defaults_result = create_user_defaults(db, user)
            if defaults_result["success"]:
                logger.info(f"✅ Dados padrão criados para usuário: {user.email}")
                logger.info(
                    f"   - Workspace individual: {defaults_result['workspace']['name']}"
                )
                logger.info(
                    f"   - Plano: {defaults_result['subscription']['plan_name']}"
                )
            else:
                logger.error(
                    f"❌ Falha ao criar dados padrão: {defaults_result['error']}"
                )
        except Exception as e:
            logger.error(
                f"❌ Erro ao criar dados padrão para usuário {user.email}: {str(e)}"
            )

        # Gerar token de verificação de email
        verification_token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
        email_token = EmailVerificationToken(
            token=verification_token,
            user_id=user.id,
            expires_at=expires_at,
        )
        db.add(email_token)
        db.commit()

        # Enviar email de verificação
        try:
            await email_service.send_verification_email(
                user.email,
                user.full_name,
                verification_token,
            )
            logger.info(f"Email de verificação enviado para: {user.email}")
        except Exception as e:
            logger.error(f"Erro ao enviar email de verificação: {e}")

        user_response = UserResponse.from_orm(user)
        return wrap_data_response(
            data=user_response.dict(),
            message="Usuário registrado com sucesso. Verifique seu email para ativar a conta.",
            request=request,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao registrar usuário: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao registrar usuário",
        )


@router.post(
    "/login",
    response_model=Dict[str, Any],
    summary="Login flexível do usuário",
    response_description="Tokens de acesso e refresh gerados",
    description="""
    **Endpoint de login flexível que aceita múltiplos formatos de entrada:**
    
    ## 🔄 Formatos Aceitos:
    
    ### 1. JSON (application/json):
    ```json
    {
        "username": "user@example.com",
        "password": "password123"
    }
    ```
    
    ### 2. Form Data (application/x-www-form-urlencoded):
    ```
    username=user@example.com&password=password123
    ```
    
    ### 3. Via cURL (qualquer formato):
    ```bash
    # JSON
    curl -X POST "http://localhost:8000/api/v1/auth/login" \
         -H "Content-Type: application/json" \
         -d '{"username":"user@example.com","password":"password123"}'
    
    # Form data
    curl -X POST "http://localhost:8000/api/v1/auth/login" \
         -H "Content-Type: application/x-www-form-urlencoded" \
         -d "username=user@example.com&password=password123"
    ```
    
    ## 🔑 Campos de Login:
    - **username**: Aceita tanto **email** quanto **username**
    - **password**: Senha do usuário
    
    O sistema automaticamente busca por email OU username na base de dados.
    """
)
async def login(
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Autentica o usuário com flexibilidade total de formato de entrada.
    
    Aceita automaticamente:
    - JSON com Content-Type: application/json
    - Form-data com Content-Type: application/x-www-form-urlencoded
    - Parâmetros diretos via form
    
    Busca o usuário por email OU username automaticamente.
    ROBUSTO: Funciona mesmo com problemas de relacionamento SQLAlchemy.
    """
    user_identifier = None
    user_password = None
    
    # Tentar extrair credenciais do corpo da requisição
    try:
        # Ler corpo da requisição
        body = await request.body()
        content_type = request.headers.get("content-type", "").lower()
        
        if "application/json" in content_type:
            # Parse JSON
            import json
            data = json.loads(body.decode())
            user_identifier = data.get("username") or data.get("email")
            user_password = data.get("password")
            
        elif "application/x-www-form-urlencoded" in content_type:
            # Parse form data
            from urllib.parse import parse_qs
            data = parse_qs(body.decode())
            user_identifier = data.get("username", [None])[0]
            user_password = data.get("password", [None])[0]
            
        else:
            # Tentar como form data padrão (para compatibilidade)
            try:
                from urllib.parse import parse_qs
                data = parse_qs(body.decode())
                user_identifier = data.get("username", [None])[0]
                user_password = data.get("password", [None])[0]
            except:
                pass
                
    except Exception as e:
        logger.warning(f"Erro ao extrair credenciais: {e}")
    
    # Validar se conseguimos extrair as credenciais
    if not user_identifier or not user_password:
        logger.warning("Tentativa de login sem credenciais completas")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username/email e senha são obrigatórios. Envie no formato JSON ou form-data.",
        )
    
    # ===== BUSCA ROBUSTA DE USUÁRIO (sem relacionamentos problemáticos) =====
    try:
        # Query simples e direta sem relacionamentos
        from sqlalchemy import text
        
        # Buscar usuário usando SQL direto para evitar problemas de relacionamento
        result = db.execute(
            text("""
                SELECT id, email, username, hashed_password, is_active, is_verified, tenant_id
                FROM synapscale_db.users 
                WHERE email = :identifier OR username = :identifier
                LIMIT 1
            """),
            {"identifier": user_identifier}
        ).fetchone()
        
        if not result:
            logger.info(f"Usuário não encontrado: {user_identifier}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email/username ou senha incorretos",
            )
        
        # Verificar senha usando método direto
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        if not pwd_context.verify(user_password, result.hashed_password):
            logger.info(f"Senha incorreta para: {user_identifier}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email/username ou senha incorretos",
            )
        
        # Verificar se conta está ativa
        if not result.is_active:
            logger.info(f"Conta desativada: {user_identifier}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Conta desativada",
            )
        
        # Criar dados do usuário para resposta
        user_data = {
            "id": str(result.id),
            "email": result.email,
            "username": result.username,
            "is_active": result.is_active,
            "is_verified": result.is_verified,
            "tenant_id": str(result.tenant_id) if result.tenant_id else None
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Erro na busca de usuário: {e}")
        # Fallback para query ORM simples
        try:
            user = db.query(User).filter(
                (User.email == user_identifier) | (User.username == user_identifier)
            ).first()
            
            if not user or not user.verify_password(user_password):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Email/username ou senha incorretos",
                )
            
            if not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Conta desativada",
                )
            
            user_data = {
                "id": str(user.id),
                "email": user.email,
                "username": user.username,
                "is_active": user.is_active,
                "is_verified": user.is_verified,
                "tenant_id": str(user.tenant_id) if user.tenant_id else None
            }
            
        except Exception as fallback_error:
            logger.error(f"Erro crítico no login: {fallback_error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno do servidor. Tente novamente.",
            )

    # ===== CRIAÇÃO DE TOKENS (método robusto) =====
    try:
        # Criar tokens
        access_token = jwt_manager.create_access_token(
            data={"sub": user_data["email"], "user_id": user_data["id"]},
        )
        
        # Tentar criar refresh token
        try:
            user_refresh_token = jwt_manager.create_refresh_token(user_data["id"], db)
        except Exception as refresh_error:
            logger.warning(f"Erro ao criar refresh token: {refresh_error}")
            # Continuar sem refresh token se houver problema
            user_refresh_token = None
        
        # Montar resposta
        response_data = {
            "access_token": access_token,
            "refresh_token": user_refresh_token,
            "token_type": "bearer",
            "user": user_data
        }

        logger.info(f"Login realizado com sucesso para: {user_data['email']} (identificado como: {user_identifier})")
        return wrap_data_response(
            data=response_data, 
            message="Login realizado com sucesso", 
            request=request
        )
        
    except Exception as token_error:
        logger.error(f"Erro na criação de tokens: {token_error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao gerar tokens de acesso.",
        )


@router.post(
    "/refresh",
    response_model=Dict[str, Any],
    summary="Renovar token de acesso",
    response_description="Novo token de acesso gerado"
)
async def refresh_token(
    request: Request,
    refresh_data: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    """
    Renova o token de acesso usando um refresh token válido.

    - **refresh_token**: Token de atualização válido

    Exemplo de corpo de requisição:
    ```json
    {
      "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    }
    ```
    """
    try:
        access_token = jwt_manager.refresh_access_token(
            refresh_data.refresh_token,
            db,
        )
        if not access_token:
            logger.info(
                f"Tentativa de refresh com token inválido: {refresh_data.refresh_token}"
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Erro ao gerar novo token de acesso",
            )

        # Buscar usuário para retornar dados atualizados
        token_record = (
            db.query(RefreshToken)
            .filter(RefreshToken.token == refresh_data.refresh_token)
            .first()
        )
        if not token_record:
            logger.info(
                f"Refresh token não encontrado no banco: {refresh_data.refresh_token}"
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido",
            )

        user = db.query(User).filter(User.id == token_record.user_id).first()
        token_data = Token(
            access_token=access_token,
            refresh_token=refresh_data.refresh_token,
            token_type="bearer",
            user=UserResponse.from_orm(user),
        )

        return wrap_data_response(
            data=token_data.dict(),
            message="Token renovado com sucesso",
            request=request,
        )

    except HTTPException:
        raise
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error("Erro ao renovar token: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Erro ao renovar token",
        ) from e


@router.post(
    "/logout",
    response_model=Dict[str, Any],
    summary="Logout do usuário",
    response_description="Logout realizado com sucesso"
)
async def logout(
    request: Request,
    refresh_data: RefreshTokenRequest,
    _: User = Depends(get_current_user),  # Usado para autenticação
    db: Session = Depends(get_db),
):
    """
    Faz logout do usuário revogando o refresh token informado.

    - **refresh_token**: Token de atualização a ser revogado

    Exemplo de corpo de requisição:
    ```json
    {
      "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    }
    ```
    """
    try:
        jwt_manager.revoke_refresh_token(refresh_data.refresh_token, db)
        logger.info(
            f"Logout realizado para refresh token: {refresh_data.refresh_token}"
        )

        return wrap_empty_response(
            message="Logout realizado com sucesso", request=request
        )

    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error("Erro ao fazer logout: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao fazer logout",
        ) from e


@router.post(
    "/logout-all",
    response_model=Dict[str, Any],
    summary="Logout de todos os dispositivos",
    response_description="Logout de todos os dispositivos realizado com sucesso"
)
async def logout_all(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Faz logout de todos os dispositivos revogando todos os refresh tokens do usuário autenticado.

    Não requer corpo de requisição.
    """
    try:
        jwt_manager.revoke_all_user_tokens(str(current_user.id), db)
        logger.info(
            f"Logout de todos os dispositivos realizado para user_id: {current_user.id}"
        )

        return wrap_empty_response(
            message="Logout de todos os dispositivos realizado com sucesso",
            request=request,
        )

    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error(
            "Erro ao fazer logout de todos os dispositivos: %s",
            str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao fazer logout",
        ) from e


@router.get(
    "/me",
    response_model=Dict[str, Any],
    summary="Obter informações do usuário autenticado",
    response_description="Dados do usuário autenticado retornados com sucesso"
)
async def get_current_user_info(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    """
    Retorna as informações do usuário atualmente autenticado.

    Não requer corpo de requisição.
    """
    user_response = UserResponse.from_orm(current_user)
    return wrap_data_response(
        data=user_response.dict(),
        message="Informações do usuário obtidas com sucesso",
        request=request,
    )


@router.post(
    "/verify-email",
    response_model=Dict[str, Any],
    summary="Verificar email do usuário",
    response_description="Email verificado com sucesso"
)
async def verify_email(
    request: Request,
    verification_data: EmailVerificationRequest,
    db: Session = Depends(get_db),
):
    """
    Verifica o email do usuário usando o token de verificação.

    - **token**: Token de verificação recebido por email

    Exemplo de corpo de requisição:
    ```json
    {
      "token": "abc123def456..."
    }
    ```
    """
    # Buscar token de verificação usando o método enhanced do modelo
    email_token = EmailVerificationToken.find_valid_token(db, verification_data.token)
    if not email_token:
        logger.info(
            f"Tentativa de verificação com token inválido: {verification_data.token}"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token de verificação inválido ou expirado",
        )

    # Buscar usuário
    user = db.query(User).filter(User.id == email_token.user_id).first()
    if not user:
        logger.info(
            f"Token de verificação válido, mas usuário não encontrado: {email_token.user_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado",
        )

    # Verificar email
    user.is_verified = True
    email_token.use_token()  # Usar método enhanced do modelo
    db.commit()
    logger.info(f"Email verificado com sucesso para user_id: {user.id}")

    return wrap_empty_response(message="Email verificado com sucesso", request=request)


@router.post(
    "/resend-verification",
    response_model=Dict[str, Any],
    summary="Reenviar email de verificação",
    response_description="Email de verificação reenviado com sucesso"
)
async def resend_verification_email(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Reenvia o email de verificação para o usuário autenticado.

    Não requer corpo de requisição.
    """
    if current_user.is_verified:
        return wrap_empty_response(message="Email já está verificado", request=request)

    # Invalidar tokens de verificação anteriores usando o método do modelo
    EmailVerificationToken.invalidate_user_tokens(db, str(current_user.id))

    # Gerar novo token usando o método enhanced do modelo
    email_token = EmailVerificationToken.create_for_user(
        user_id=str(current_user.id),
        email=current_user.email,
        expires_in_minutes=1440,  # 24 horas
    )
    db.add(email_token)
    db.commit()

    # Enviar email
    try:
        await email_service.send_verification_email(
            current_user.email,
            current_user.full_name,
            email_token.token,
        )
        logger.info(f"Email de verificação reenviado para: {current_user.email}")

        return wrap_empty_response(
            message="Email de verificação reenviado com sucesso", request=request
        )

    except Exception as e:
        logger.error(f"Erro ao reenviar email de verificação: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao enviar email de verificação",
        )


@router.post(
    "/forgot-password",
    response_model=Dict[str, Any],
    summary="Solicitar redefinição de senha",
    response_description="Instruções de redefinição enviadas se o email existir"
)
async def forgot_password(
    request: Request,
    request_data: PasswordResetRequest,
    db: Session = Depends(get_db),
):
    """
    Solicita redefinição de senha enviando um token por email.

    - **email**: Email do usuário

    Exemplo de corpo de requisição:
    ```json
    {
      "email": "usuario@exemplo.com"
    }
    ```
    """
    # Buscar usuário
    user = db.query(User).filter(User.email == request_data.email).first()
    if not user:
        # Por segurança, não revelamos se o email existe ou não
        logger.info(
            f"Solicitação de reset para email inexistente: {request_data.email}"
        )
        return wrap_empty_response(
            message="Se o email existir, instruções de redefinição foram enviadas",
            request=request,
        )

    # Invalidar tokens de reset anteriores usando o método do modelo
    PasswordResetToken.invalidate_user_tokens(db, str(user.id))

    # Gerar novo token usando o método enhanced do modelo
    password_token = PasswordResetToken.create_for_user(
        user_id=str(user.id), expires_in_minutes=60  # 1 hora
    )
    db.add(password_token)
    db.commit()

    # Enviar email
    try:
        await email_service.send_password_reset_email(
            user.email,
            user.full_name,
            password_token.token,
        )
        logger.info(f"Email de redefinição enviado para: {user.email}")
    except Exception as e:
        logger.error(f"Erro ao enviar email de redefinição: {e}")

    return wrap_empty_response(
        message="Se o email existir, instruções de redefinição foram enviadas",
        request=request,
    )


@router.post(
    "/reset-password",
    response_model=Dict[str, Any],
    summary="Redefinir senha do usuário",
    response_description="Senha redefinida com sucesso"
)
async def reset_password(
    request: Request,
    reset_data: PasswordResetConfirm,
    db: Session = Depends(get_db),
):
    """
    Redefine a senha do usuário usando o token de redefinição.

    - **token**: Token de redefinição recebido por email
    - **new_password**: Nova senha

    Exemplo de corpo de requisição:
    ```json
    {
      "token": "abc123def456...",
      "new_password": "NovaSenhaForte123!"
    }
    ```
    """
    # Buscar token de reset usando o método enhanced do modelo
    token_record = PasswordResetToken.find_valid_token(db, reset_data.token)
    if not token_record:
        logger.info(
            f"Tentativa de reset com token inválido ou expirado: {reset_data.token}"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token de redefinição inválido ou expirado",
        )

    # Buscar usuário
    user = db.query(User).filter(User.id == token_record.user_id).first()
    if not user:
        logger.info(
            f"Token de reset válido, mas usuário não encontrado: {token_record.user_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado",
        )

    # Redefinir senha
    user.set_password(reset_data.new_password)
    token_record.use_token()  # Usar método enhanced do modelo

    # Revogar todos os refresh tokens do usuário por segurança
    jwt_manager.revoke_all_user_tokens(str(user.id), db)
    db.commit()
    logger.info(f"Senha redefinida com sucesso para user_id: {user.id}")

    return wrap_empty_response(message="Senha redefinida com sucesso", request=request)


@router.post(
    "/change-password",
    response_model=Dict[str, Any],
    summary="Alterar senha do usuário autenticado",
    response_description="Senha alterada com sucesso"
)
async def change_password(
    request: Request,
    current_password: str = Form(...),
    new_password: str = Form(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Altera a senha do usuário autenticado.

    - **current_password**: Senha atual
    - **new_password**: Nova senha

    Exemplo de corpo (x-www-form-urlencoded):
    ```
    current_password=SenhaAtual123!&new_password=NovaSenhaForte123!
    ```
    """
    # Verificar senha atual
    if not current_user.verify_password(current_password):
        logger.info(
            f"Tentativa de alteração de senha com senha atual incorreta para user_id: {current_user.id}"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Senha atual incorreta",
        )

    # Definir nova senha
    current_user.set_password(new_password)

    # Revogar todos os refresh tokens por segurança
    jwt_manager.revoke_all_user_tokens(str(current_user.id), db)
    db.commit()
    logger.info(f"Senha alterada com sucesso para user_id: {current_user.id}")

    return wrap_empty_response(message="Senha alterada com sucesso", request=request)


@router.delete(
    "/account",
    response_model=Dict[str, Any],
    summary="Excluir conta do usuário autenticado",
    response_description="Conta excluída com sucesso"
)
async def delete_account(
    request: Request,
    password: str = Form(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Exclui a conta do usuário autenticado.

    - **password**: Senha do usuário para confirmação

    Exemplo de corpo (x-www-form-urlencoded):
    ```
    password=SenhaForte123!
    ```
    """
    # Verificar senha
    if not current_user.verify_password(password):
        logger.info(
            f"Tentativa de exclusão de conta com senha incorreta para user_id: {current_user.id}"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Senha incorreta",
        )

    # Revogar todos os tokens
    jwt_manager.revoke_all_user_tokens(str(current_user.id), db)

    # Excluir usuário
    db.delete(current_user)
    db.commit()
    logger.info(f"Conta excluída com sucesso para user_id: {current_user.id}")

    return wrap_empty_response(message="Conta excluída com sucesso", request=request)


@router.get(
    "/test-token",
    response_model=Dict[str, Any],
    summary="🧪 Teste de Token JWT",
    description="""
    **Endpoint para testar se a autenticação JWT está funcionando**
    
    Use este endpoint para verificar se:
    - Seu token JWT está válido
    - A autenticação está funcionando corretamente
    - O usuário está sendo identificado
    
    ## 📝 Como usar:
    1. Faça login com `/auth/docs-login` ou `/auth/login`
    2. Configure o token Bearer no botão "Authorize"
    3. Execute este endpoint para testar
    
    Se estiver funcionando, você verá suas informações de usuário.
    """,
)
async def test_token(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    """
    Testa se o token JWT está funcionando corretamente
    """
    test_data = {
        "message": "✅ Token JWT válido!",
        "user": {
            "id": str(current_user.id),
            "email": current_user.email,
            "name": (
                current_user.name
                if hasattr(current_user, "name")
                else current_user.full_name
            ),
            "is_active": current_user.is_active,
            "is_verified": current_user.is_verified,
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "authenticated",
    }

    return wrap_data_response(
        data=test_data, message="Token JWT testado com sucesso", request=request
    )


@router.get(
    "/test-hybrid-auth",
    response_model=Dict[str, Any],
    summary="🧪 Teste de Autenticação Híbrida",
    description="""
    **Endpoint para testar se a autenticação híbrida está funcionando**
    
    Este endpoint aceita **AMBOS** os métodos de autenticação:
    - **HTTPBearer**: Token JWT no header Authorization
    - **HTTPBasic**: Email/senha diretamente no modal de autorização
    
    ## 📝 Como usar:
    
    ### Opção 1: HTTPBearer (Token JWT)
    1. Faça login com `/auth/login` ou `/auth/docs-login`
    2. No modal "Authorize", seção **HTTPBearer**:
       - Cole o token JWT no campo "Value"
       - Clique "Authorize"
    3. Execute este endpoint
    
    ### Opção 2: HTTPBasic (Email/Senha)
    1. No modal "Authorize", seção **HTTPBasic**:
       - Digite seu **email** no campo "Username"
       - Digite sua **senha** no campo "Password"
       - Clique "Authorize"
    2. Execute este endpoint
    
    ## ✅ Resultado:
    Se funcionando corretamente, você verá suas informações de usuário
    independente do método de autenticação usado.
    """,
)
async def test_hybrid_authentication(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    """
    Testa se a autenticação híbrida (HTTPBasic + HTTPBearer) está funcionando
    """
    test_data = {
        "message": "✅ Autenticação híbrida funcionando corretamente!",
        "user": {
            "id": str(current_user.id),
            "email": current_user.email,
            "name": (
                current_user.name
                if hasattr(current_user, "name")
                else current_user.full_name
            ),
            "is_active": current_user.is_active,
            "is_verified": current_user.is_verified,
            "is_admin": (
                current_user.is_admin if hasattr(current_user, "is_admin") else False
            ),
        },
        "authentication": {
            "status": "authenticated",
            "methods_supported": [
                "HTTPBearer (JWT Token)",
                "HTTPBasic (Email/Password)",
            ],
            "note": "Este endpoint aceita ambos os métodos de autenticação automaticamente",
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "server_time": time.time(),
    }

    return wrap_data_response(
        data=test_data,
        message="Autenticação híbrida testada com sucesso",
        request=request,
    )
