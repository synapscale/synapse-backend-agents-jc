"""
Endpoints completos de autenticação e autorização
"""
from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
import secrets
import uuid

from src.synapse.database import get_db
from src.synapse.models.user import User, RefreshToken, PasswordResetToken, EmailVerificationToken
from src.synapse.api.deps import get_current_user, get_current_active_user
from src.synapse.core.email.service import email_service
from src.synapse.schemas.auth import (
    UserCreate, UserResponse, Token, RefreshTokenRequest,
    PasswordResetRequest, PasswordResetConfirm, EmailVerificationRequest
)
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Registra um novo usuário"""
    
    # Verificar se email já existe
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já está registrado"
        )
    
    # Criar novo usuário
    user = User(
        email=user_data.email,
        first_name=user_data.first_name,
        last_name=user_data.last_name
    )
    user.set_password(user_data.password)
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Gerar token de verificação de email
    verification_token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
    
    email_token = EmailVerificationToken(
        token=verification_token,
        user_id=user.id,
        expires_at=expires_at
    )
    db.add(email_token)
    db.commit()
    
    # Enviar email de verificação
    try:
        await email_service.send_verification_email(
            email=user.email,
            token=verification_token,
            user_name=user.full_name
        )
    except Exception as e:
        logger.error(f"Erro ao enviar email de verificação: {str(e)}")
        # Não falhar o registro se o email não puder ser enviado
    
    return UserResponse.from_orm(user)

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Autentica usuário e retorna tokens"""
    
    # Buscar usuário por email
    user = db.query(User).filter(User.email == form_data.username).first()
    
    if not user or not user.verify_password(form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Conta desativada"
        )
    
    # Criar tokens
    access_token = jwt_manager.create_access_token(
        data={"sub": user.email, "user_id": str(user.id)}
    )
    refresh_token = jwt_manager.create_refresh_token(str(user.id), db)
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user=UserResponse.from_orm(user)
    )

@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """Renova token de acesso usando refresh token"""
    
    try:
        access_token = jwt_manager.refresh_access_token(refresh_data.refresh_token, db)
        
        # Buscar usuário para retornar dados atualizados
        token_record = db.query(RefreshToken).filter(
            RefreshToken.token == refresh_data.refresh_token
        ).first()
        
        user = db.query(User).filter(User.id == token_record.user_id).first()
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_data.refresh_token,
            token_type="bearer",
            user=UserResponse.from_orm(user)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao renovar token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Erro ao renovar token"
        )

@router.post("/logout")
async def logout(
    refresh_data: RefreshTokenRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Faz logout do usuário revogando o refresh token"""
    
    try:
        jwt_manager.revoke_refresh_token(refresh_data.refresh_token, db)
        return {"message": "Logout realizado com sucesso"}
    except Exception as e:
        logger.error(f"Erro ao fazer logout: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao fazer logout"
        )

@router.post("/logout-all")
async def logout_all(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Faz logout de todos os dispositivos revogando todos os refresh tokens"""
    
    try:
        jwt_manager.revoke_all_user_tokens(str(current_user.id), db)
        return {"message": "Logout de todos os dispositivos realizado com sucesso"}
    except Exception as e:
        logger.error(f"Erro ao fazer logout de todos os dispositivos: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao fazer logout"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Retorna informações do usuário atual"""
    return UserResponse.from_orm(current_user)

@router.post("/verify-email")
async def verify_email(
    verification_data: EmailVerificationRequest,
    db: Session = Depends(get_db)
):
    """Verifica email do usuário"""
    
    # Buscar token de verificação
    token_record = db.query(EmailVerificationToken).filter(
        EmailVerificationToken.token == verification_data.token
    ).first()
    
    if not token_record or not token_record.is_valid():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token de verificação inválido ou expirado"
        )
    
    # Buscar usuário
    user = db.query(User).filter(User.id == token_record.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    # Marcar email como verificado
    user.is_verified = True
    token_record.is_used = True
    
    db.commit()
    
    return {"message": "Email verificado com sucesso"}

@router.post("/resend-verification")
async def resend_verification_email(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Reenvia email de verificação"""
    
    if current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já está verificado"
        )
    
    # Gerar novo token
    verification_token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
    
    email_token = EmailVerificationToken(
        token=verification_token,
        user_id=current_user.id,
        expires_at=expires_at
    )
    db.add(email_token)
    db.commit()
    
    # Enviar email
    try:
        await email_service.send_verification_email(
            email=current_user.email,
            token=verification_token,
            user_name=current_user.full_name
        )
        return {"message": "Email de verificação enviado"}
    except Exception as e:
        logger.error(f"Erro ao enviar email de verificação: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro ao enviar email de verificação"
        )

@router.post("/forgot-password")
async def forgot_password(
    request_data: PasswordResetRequest,
    db: Session = Depends(get_db)
):
    """Solicita redefinição de senha"""
    
    # Buscar usuário
    user = db.query(User).filter(User.email == request_data.email).first()
    if not user:
        # Não revelar se o email existe ou não
        return {"message": "Se o email existir, você receberá instruções para redefinir a senha"}
    
    # Gerar token de redefinição
    reset_token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
    
    password_token = PasswordResetToken(
        token=reset_token,
        user_id=user.id,
        expires_at=expires_at
    )
    db.add(password_token)
    db.commit()
    
    # Enviar email
    try:
        await email_service.send_password_reset_email(
            email=user.email,
            token=reset_token,
            user_name=user.full_name
        )
    except Exception as e:
        logger.error(f"Erro ao enviar email de redefinição: {str(e)}")
    
    return {"message": "Se o email existir, você receberá instruções para redefinir a senha"}

@router.post("/reset-password")
async def reset_password(
    reset_data: PasswordResetConfirm,
    db: Session = Depends(get_db)
):
    """Redefine senha do usuário"""
    
    # Buscar token de redefinição
    token_record = db.query(PasswordResetToken).filter(
        PasswordResetToken.token == reset_data.token
    ).first()
    
    if not token_record or not token_record.is_valid():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token de redefinição inválido ou expirado"
        )
    
    # Buscar usuário
    user = db.query(User).filter(User.id == token_record.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado"
        )
    
    # Redefinir senha
    user.set_password(reset_data.new_password)
    token_record.is_used = True
    
    # Revogar todos os refresh tokens do usuário por segurança
    jwt_manager.revoke_all_user_tokens(str(user.id), db)
    
    db.commit()
    
    return {"message": "Senha redefinida com sucesso"}

@router.post("/change-password")
async def change_password(
    current_password: str = Form(...),
    new_password: str = Form(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Altera senha do usuário autenticado"""
    
    # Verificar senha atual
    if not current_user.verify_password(current_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Senha atual incorreta"
        )
    
    # Definir nova senha
    current_user.set_password(new_password)
    
    # Revogar todos os refresh tokens por segurança
    jwt_manager.revoke_all_user_tokens(str(current_user.id), db)
    
    db.commit()
    
    return {"message": "Senha alterada com sucesso"}

@router.delete("/account")
async def delete_account(
    password: str = Form(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Exclui conta do usuário"""
    
    # Verificar senha
    if not current_user.verify_password(password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Senha incorreta"
        )
    
    # Revogar todos os tokens
    jwt_manager.revoke_all_user_tokens(str(current_user.id), db)
    
    # Marcar usuário como inativo (soft delete)
    current_user.is_active = False
    
    db.commit()
    
    return {"message": "Conta excluída com sucesso"}

