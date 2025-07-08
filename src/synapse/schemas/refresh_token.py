"""
Schemas para RefreshToken - tokens de refresh de autenticação
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID


class RefreshTokenBase(BaseModel):
    """Schema base para RefreshToken"""
    
    # Relacionamentos
    user_id: UUID = Field(..., description="ID do usuário")
    
    # Token
    token: str = Field(..., description="Token de refresh")
    
    # Configurações
    is_active: bool = Field(True, description="Token ativo")
    is_revoked: bool = Field(False, description="Token revogado")
    
    # Datas
    expires_at: datetime = Field(..., description="Data de expiração")
    
    # Contexto
    tenant_id: UUID = Field(..., description="ID do tenant")
    
    # Informações de dispositivo/sessão
    device_info: Optional[Dict[str, Any]] = Field(None, description="Informações do dispositivo")
    ip_address: Optional[str] = Field(None, description="Endereço IP")
    user_agent: Optional[str] = Field(None, description="User agent")
    
    # Metadata
    metadata: Optional[Dict[str, Any]] = Field(None, description="Dados adicionais")


class RefreshTokenCreate(RefreshTokenBase):
    """Schema para criação de RefreshToken"""
    pass


class RefreshTokenUpdate(BaseModel):
    """Schema para atualização de RefreshToken"""
    
    is_active: Optional[bool] = Field(None, description="Token ativo")
    is_revoked: Optional[bool] = Field(None, description="Token revogado")
    expires_at: Optional[datetime] = Field(None, description="Data de expiração")
    
    device_info: Optional[Dict[str, Any]] = Field(None, description="Informações do dispositivo")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Dados adicionais")


class RefreshTokenResponse(RefreshTokenBase):
    """Schema para resposta de RefreshToken"""
    
    id: UUID = Field(..., description="ID único do token")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Data de atualização")
    
    # Informações relacionadas
    user_name: Optional[str] = Field(None, description="Nome do usuário")
    user_email: Optional[str] = Field(None, description="Email do usuário")
    
    # Token mascarado para segurança
    masked_token: Optional[str] = Field(None, description="Token mascarado")
    
    # Estatísticas
    usage_count: Optional[int] = Field(None, description="Número de usos")
    last_used_at: Optional[datetime] = Field(None, description="Último uso")
    
    # Status derivados
    is_expired: Optional[bool] = Field(None, description="Token expirado")
    days_until_expiry: Optional[int] = Field(None, description="Dias até expirar")
    
    model_config = ConfigDict(from_attributes=True)


class RefreshTokenList(BaseModel):
    """Schema para lista de RefreshToken"""
    
    items: List[RefreshTokenResponse] = Field(..., description="Lista de tokens")
    total: int = Field(..., description="Total de tokens")
    page: int = Field(1, description="Página atual")
    size: int = Field(10, description="Tamanho da página")
    
    model_config = ConfigDict(from_attributes=True)


class RefreshTokenUse(BaseModel):
    """Schema para uso de RefreshToken"""
    
    token: str = Field(..., description="Token de refresh")
    
    # Informações do uso
    ip_address: Optional[str] = Field(None, description="Endereço IP")
    user_agent: Optional[str] = Field(None, description="User agent")
    
    model_config = ConfigDict(from_attributes=True)


class RefreshTokenUseResult(BaseModel):
    """Schema para resultado do uso do token"""
    
    token_id: UUID = Field(..., description="ID do token")
    
    # Resultado
    is_valid: bool = Field(..., description="Token válido")
    new_access_token: Optional[str] = Field(None, description="Novo token de acesso")
    new_refresh_token: Optional[str] = Field(None, description="Novo token de refresh")
    
    # Informações
    expires_in: Optional[int] = Field(None, description="Expira em (segundos)")
    
    # Erro
    error_message: Optional[str] = Field(None, description="Mensagem de erro")
    
    model_config = ConfigDict(from_attributes=True)


class RefreshTokenRevoke(BaseModel):
    """Schema para revogação de RefreshToken"""
    
    token_id: Optional[UUID] = Field(None, description="ID do token específico")
    user_id: Optional[UUID] = Field(None, description="ID do usuário (revogar todos)")
    
    # Motivo da revogação
    revocation_reason: Optional[str] = Field(None, description="Motivo da revogação")
    
    model_config = ConfigDict(from_attributes=True)


class RefreshTokenRevokeResult(BaseModel):
    """Schema para resultado da revogação"""
    
    revoked_tokens: List[UUID] = Field(..., description="IDs dos tokens revogados")
    revoked_count: int = Field(..., description="Número de tokens revogados")
    
    model_config = ConfigDict(from_attributes=True)


class RefreshTokenValidation(BaseModel):
    """Schema para validação de RefreshToken"""
    
    token: str = Field(..., description="Token a validar")
    
    model_config = ConfigDict(from_attributes=True)


class RefreshTokenValidationResult(BaseModel):
    """Schema para resultado da validação"""
    
    is_valid: bool = Field(..., description="Token válido")
    
    # Informações do token
    token_id: Optional[UUID] = Field(None, description="ID do token")
    user_id: Optional[UUID] = Field(None, description="ID do usuário")
    
    # Status
    is_expired: bool = Field(..., description="Token expirado")
    is_revoked: bool = Field(..., description="Token revogado")
    
    # Datas
    expires_at: Optional[datetime] = Field(None, description="Data de expiração")
    
    # Erro
    error_message: Optional[str] = Field(None, description="Mensagem de erro")
    
    model_config = ConfigDict(from_attributes=True)


class RefreshTokenCleanup(BaseModel):
    """Schema para limpeza de RefreshToken"""
    
    # Critérios de limpeza
    cleanup_expired: bool = Field(True, description="Limpar tokens expirados")
    cleanup_revoked: bool = Field(True, description="Limpar tokens revogados")
    cleanup_older_than_days: Optional[int] = Field(None, description="Limpar tokens mais antigos que X dias")
    
    # Contexto
    tenant_id: Optional[UUID] = Field(None, description="ID do tenant específico")
    
    model_config = ConfigDict(from_attributes=True)


class RefreshTokenCleanupResult(BaseModel):
    """Schema para resultado da limpeza"""
    
    cleaned_tokens: int = Field(..., description="Tokens limpos")
    
    # Detalhes
    expired_tokens_cleaned: int = Field(..., description="Tokens expirados limpos")
    revoked_tokens_cleaned: int = Field(..., description="Tokens revogados limpos")
    old_tokens_cleaned: int = Field(..., description="Tokens antigos limpos")
    
    model_config = ConfigDict(from_attributes=True)


class RefreshTokenStatistics(BaseModel):
    """Schema para estatísticas de RefreshToken"""
    
    # Totais
    total_tokens: int = Field(..., description="Total de tokens")
    active_tokens: int = Field(..., description="Tokens ativos")
    expired_tokens: int = Field(..., description="Tokens expirados")
    revoked_tokens: int = Field(..., description="Tokens revogados")
    
    # Por usuário
    tokens_by_user: Dict[str, int] = Field(..., description="Tokens por usuário")
    
    # Por dispositivo
    tokens_by_device: Dict[str, int] = Field(..., description="Tokens por dispositivo")
    
    # Uso
    total_usage: int = Field(..., description="Total de usos")
    average_usage_per_token: float = Field(..., description="Uso médio por token")
    
    # Período
    period_start: datetime = Field(..., description="Início do período")
    period_end: datetime = Field(..., description="Fim do período")
    
    model_config = ConfigDict(from_attributes=True)


class RefreshTokenSecurity(BaseModel):
    """Schema para segurança de RefreshToken"""
    
    # Configurações de segurança
    max_tokens_per_user: int = Field(5, description="Máximo de tokens por usuário")
    token_lifetime_days: int = Field(30, description="Tempo de vida do token em dias")
    
    # Detecção de anomalias
    detect_multiple_locations: bool = Field(True, description="Detectar múltiplas localizações")
    detect_device_changes: bool = Field(True, description="Detectar mudanças de dispositivo")
    
    model_config = ConfigDict(from_attributes=True)


class RefreshTokenAlert(BaseModel):
    """Schema para alertas de RefreshToken"""
    
    alert_type: str = Field(..., description="Tipo de alerta")
    user_id: UUID = Field(..., description="ID do usuário")
    
    # Detalhes do alerta
    message: str = Field(..., description="Mensagem do alerta")
    severity: str = Field(..., description="Severidade do alerta")
    
    # Contexto
    token_id: Optional[UUID] = Field(None, description="ID do token")
    ip_address: Optional[str] = Field(None, description="Endereço IP")
    
    # Timestamp
    triggered_at: datetime = Field(..., description="Data do alerta")
    
    model_config = ConfigDict(from_attributes=True)
