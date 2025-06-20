"""
Endpoints completos de autenticação e autorização
"""

import logging
import secrets
from datetime import datetime, timedelta, timezone
from typing import Dict
import time

from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordRequestForm, HTTPBasicCredentials
from sqlalchemy.orm import Session

from synapse.api.deps import get_current_user, get_current_active_user, get_current_user_basic
from synapse.core.auth.jwt import jwt_manager
from synapse.core.email.service import email_service
from synapse.database import get_db
from synapse.models.user import (
    User,
    RefreshToken,
    PasswordResetToken,
    EmailVerificationToken,
)
from synapse.schemas.auth import (
    UserCreate,
    UserResponse,
    Token,
    RefreshTokenRequest,
    PasswordResetRequest,
    PasswordResetConfirm,
    EmailVerificationRequest,
)
from synapse.services.user_defaults import create_user_defaults

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/docs-login", 
    response_model=Token, 
    tags=["authentication"],
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
        401: {"description": "Credenciais inválidas"}
    }
)
async def docs_login(
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

        return {
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

    except Exception as e:
        logger.error(f"Erro no login via documentação: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno no servidor",
        )


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar novo usuário",
    response_description="Usuário registrado com sucesso",
    tags=["authentication"],
)
async def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
) -> UserResponse:
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
    existing_username = db.query(User).filter(User.username == user_data.username).first()
    if existing_username:
        logger.info(f"Tentativa de registro duplicado para username: {user_data.username}")
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
                logger.info(f"   - Workspace individual: {defaults_result['workspace']['name']}")
                logger.info(f"   - Plano: {defaults_result['subscription']['plan_name']}")
            else:
                logger.error(f"❌ Falha ao criar dados padrão: {defaults_result['error']}")
        except Exception as e:
            logger.error(f"❌ Erro ao criar dados padrão para usuário {user.email}: {str(e)}")
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
                email=str(user.email),
                token=verification_token,
                user_name=str(user.full_name),
            )
        except (ConnectionError, TimeoutError, OSError) as e:
            logger.error("Erro envio email verificação: %s", str(e))
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error("Erro inesperado envio email: %s", str(e))
        return UserResponse.from_orm(user)
    except Exception as e:
        db.rollback()
        logger.error(f"Erro inesperado no registro: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro interno ao registrar usuário")


@router.post("/login", response_model=Token, summary="Login do usuário", response_description="Tokens de acesso e refresh gerados", tags=["authentication"])
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> Token:
    """
    Autentica o usuário e retorna tokens de acesso e refresh.

    - **username**: Email do usuário
    - **password**: Senha do usuário

    Exemplo de corpo (x-www-form-urlencoded):
    ```
    username=usuario@exemplo.com&password=SenhaForte123!
    ```
    """
    # Buscar usuário por email
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not user.verify_password(form_data.password):
        logger.info(f"Tentativa de login inválida para email: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
        )
    if not user.is_active:
        logger.info(f"Tentativa de login em conta desativada: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Conta desativada",
        )
    # Criar tokens
    access_token = jwt_manager.create_access_token(
        data={"sub": user.email, "user_id": str(user.id)},
    )
    user_refresh_token = jwt_manager.create_refresh_token(str(user.id), db)
    return Token(
        access_token=access_token,
        refresh_token=user_refresh_token,
        token_type="bearer",
        user=UserResponse.from_orm(user),
    )


@router.post(
    "/refresh",
    response_model=Token,
    summary="Renovar token de acesso",
    response_description="Novo token de acesso gerado",
    tags=["authentication"],
)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: Session = Depends(get_db),
) -> Token:
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
            logger.info(f"Tentativa de refresh com token inválido: {refresh_data.refresh_token}")
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
            logger.info(f"Refresh token não encontrado no banco: {refresh_data.refresh_token}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido",
            )
        user = db.query(User).filter(User.id == token_record.user_id).first()
        return Token(
            access_token=access_token,
            refresh_token=refresh_data.refresh_token,
            token_type="bearer",
            user=UserResponse.from_orm(user),
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
    summary="Logout do usuário",
    response_description="Logout realizado com sucesso",
    tags=["authentication"],
)
async def logout(
    refresh_data: RefreshTokenRequest,
    _: User = Depends(get_current_user),  # Usado para autenticação
    db: Session = Depends(get_db),
) -> dict[str, str]:
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
        logger.info(f"Logout realizado para refresh token: {refresh_data.refresh_token}")
        return {"message": "Logout realizado com sucesso"}
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error("Erro ao fazer logout: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao fazer logout",
        ) from e


@router.post(
    "/logout-all",
    summary="Logout de todos os dispositivos",
    response_description="Logout de todos os dispositivos realizado com sucesso",
    tags=["authentication"],
)
async def logout_all(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    """
    Faz logout de todos os dispositivos revogando todos os refresh tokens do usuário autenticado.

    Não requer corpo de requisição.
    """
    try:
        jwt_manager.revoke_all_user_tokens(str(current_user.id), db)
        logger.info(f"Logout de todos os dispositivos realizado para user_id: {current_user.id}")
        return {
            "message": "Logout de todos os dispositivos realizado com sucesso",
        }
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
    response_model=UserResponse,
    summary="Obter informações do usuário autenticado",
    response_description="Dados do usuário autenticado retornados com sucesso",
    tags=["authentication"],
)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """
    Retorna as informações do usuário atualmente autenticado.

    Não requer corpo de requisição.
    """
    return UserResponse.from_orm(current_user)


@router.post(
    "/verify-email",
    summary="Verificar email do usuário",
    response_description="Email verificado com sucesso",
    tags=["authentication"],
)
async def verify_email(
    verification_data: EmailVerificationRequest,
    db: Session = Depends(get_db),
) -> dict[str, str]:
    """
    Verifica o email do usuário usando o token de verificação enviado por email.

    - **token**: Token de verificação recebido por email

    Exemplo de corpo de requisição:
    ```json
    {
      "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    }
    ```
    """
    # Buscar token de verificação
    token_record = (
        db.query(EmailVerificationToken)
        .filter(EmailVerificationToken.token == verification_data.token)
        .first()
    )
    if not token_record or not token_record.is_valid():
        logger.info(f"Tentativa de verificação de email com token inválido ou expirado: {verification_data.token}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token de verificação inválido ou expirado",
        )
    # Buscar usuário
    user = db.query(User).filter(User.id == token_record.user_id).first()
    if not user:
        logger.info(f"Token de verificação válido, mas usuário não encontrado: {token_record.user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado",
        )
    # Marcar email como verificado
    user.is_verified = True  # type: ignore
    token_record.is_used = True  # type: ignore
    db.commit()
    logger.info(f"Email verificado com sucesso para user_id: {user.id}")
    return {"message": "Email verificado com sucesso"}


@router.post(
    "/resend-verification",
    summary="Reenviar email de verificação",
    response_description="Email de verificação reenviado com sucesso",
    tags=["authentication"],
)
async def resend_verification_email(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    """
    Reenvia o email de verificação para o usuário autenticado.

    Não requer corpo de requisição.
    """
    if current_user.is_verified:
        logger.info(f"Tentativa de reenvio de verificação para email já verificado: {current_user.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já está verificado",
        )
    # Gerar novo token
    verification_token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
    email_token = EmailVerificationToken(
        token=verification_token,
        user_id=current_user.id,
        expires_at=expires_at,
    )
    db.add(email_token)
    db.commit()
    # Enviar email
    try:
        await email_service.send_verification_email(
            email=str(current_user.email),
            token=verification_token,
            user_name=str(current_user.full_name),
        )
        logger.info(f"Email de verificação reenviado para user_id: {current_user.id}")
        return {"message": "Email de verificação enviado"}
    except (ConnectionError, TimeoutError, OSError) as e:
        logger.error("Erro envio email verificação: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao enviar email de verificação",
        ) from e
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error("Erro inesperado envio email: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao enviar email de verificação",
        ) from e


@router.post(
    "/forgot-password",
    summary="Solicitar redefinição de senha",
    response_description="Instruções de redefinição enviadas se o email existir",
    tags=["authentication"],
)
async def forgot_password(
    request_data: PasswordResetRequest,
    db: Session = Depends(get_db),
) -> dict[str, str]:
    """
    Solicita redefinição de senha para o email informado.

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
        logger.info(f"Solicitação de reset para email inexistente: {request_data.email}")
        return {
            "message": (
                "Se o email existir, você receberá instruções para redefinir a senha"
            ),
        }
    # Gerar token de redefinição
    reset_token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
    password_token = PasswordResetToken(
        token=reset_token,
        user_id=user.id,
        expires_at=expires_at,
    )
    db.add(password_token)
    db.commit()
    # Enviar email
    try:
        await email_service.send_password_reset_email(
            email=str(user.email),
            token=reset_token,
            user_name=str(user.full_name),
        )
        logger.info(f"Email de reset enviado para user_id: {user.id}")
    except (ConnectionError, TimeoutError, OSError) as e:
        logger.error("Erro envio email redefinição: %s", str(e))
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error("Erro inesperado envio email: %s", str(e))
    return {
        "message": (
            "Se o email existir, você receberá instruções para redefinir a senha"
        ),
    }


@router.post(
    "/reset-password",
    summary="Redefinir senha do usuário",
    response_description="Senha redefinida com sucesso",
    tags=["authentication"],
)
async def reset_password(
    reset_data: PasswordResetConfirm,
    db: Session = Depends(get_db),
) -> dict[str, str]:
    """
    Redefine a senha do usuário usando o token de redefinição enviado por email.

    - **token**: Token de redefinição recebido por email
    - **new_password**: Nova senha

    Exemplo de corpo de requisição:
    ```json
    {
      "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "new_password": "NovaSenhaForte123!"
    }
    ```
    """
    # Buscar token de redefinição
    token_record = (
        db.query(PasswordResetToken)
        .filter(PasswordResetToken.token == reset_data.token)
        .first()
    )
    if not token_record or not token_record.is_valid():
        logger.info(f"Tentativa de reset com token inválido ou expirado: {reset_data.token}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token de redefinição inválido ou expirado",
        )
    # Buscar usuário
    user = db.query(User).filter(User.id == token_record.user_id).first()
    if not user:
        logger.info(f"Token de reset válido, mas usuário não encontrado: {token_record.user_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado",
        )
    # Redefinir senha
    user.set_password(reset_data.new_password)
    token_record.is_used = True  # type: ignore
    # Revogar todos os refresh tokens do usuário por segurança
    jwt_manager.revoke_all_user_tokens(str(user.id), db)
    db.commit()
    logger.info(f"Senha redefinida com sucesso para user_id: {user.id}")
    return {"message": "Senha redefinida com sucesso"}


@router.post(
    "/change-password",
    summary="Alterar senha do usuário autenticado",
    response_description="Senha alterada com sucesso",
    tags=["authentication"],
)
async def change_password(
    current_password: str = Form(...),
    new_password: str = Form(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> dict[str, str]:
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
        logger.info(f"Tentativa de alteração de senha com senha atual incorreta para user_id: {current_user.id}")
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
    return {"message": "Senha alterada com sucesso"}


@router.delete(
    "/account",
    summary="Excluir conta do usuário autenticado",
    response_description="Conta excluída com sucesso",
    tags=["authentication"],
)
async def delete_account(
    password: str = Form(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> dict[str, str]:
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
        logger.info(f"Tentativa de exclusão de conta com senha incorreta para user_id: {current_user.id}")
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
    return {"message": "Conta excluída com sucesso"}


@router.get(
    "/test-token",
    tags=["authentication"],
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
    """
)
async def test_token(
    current_user: User = Depends(get_current_user),
):
    """
    Testa se o token JWT está funcionando corretamente
    """
    return {
        "message": "✅ Token JWT válido!",
        "user": {
            "id": str(current_user.id),
            "email": current_user.email,
            "name": current_user.name if hasattr(current_user, 'name') else current_user.full_name,
            "is_active": current_user.is_active,
            "is_verified": current_user.is_verified,
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "authenticated"
    }


@router.get(
    "/test-hybrid-auth",
    tags=["authentication"],
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
    """
)
async def test_hybrid_authentication(
    current_user: User = Depends(get_current_user),
):
    """
    Testa se a autenticação híbrida (HTTPBasic + HTTPBearer) está funcionando
    """
    return {
        "message": "✅ Autenticação híbrida funcionando corretamente!",
        "user": {
            "id": str(current_user.id),
            "email": current_user.email,
            "name": current_user.name if hasattr(current_user, 'name') else current_user.full_name,
            "is_active": current_user.is_active,
            "is_verified": current_user.is_verified,
            "is_admin": current_user.is_admin if hasattr(current_user, 'is_admin') else False,
        },
        "authentication": {
            "status": "authenticated",
            "methods_supported": [
                "HTTPBearer (JWT Token)",
                "HTTPBasic (Email/Password)"
            ],
            "note": "Este endpoint aceita ambos os métodos de autenticação automaticamente"
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "server_time": time.time()
    }
