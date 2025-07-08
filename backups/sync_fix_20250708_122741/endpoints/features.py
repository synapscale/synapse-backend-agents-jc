"""
Endpoints para gerenciamento do sistema de Features
Inclui features, plan_features, tenant_features e workspace_features
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from datetime import datetime

from synapse.api.deps import get_db, get_current_user, require_admin
from synapse.models.user import User
from synapse.models.feature import Feature, WorkspaceFeature
from synapse.models.plan_feature import PlanFeature
from synapse.models.tenant_feature import TenantFeature
from synapse.schemas.feature import (
    FeatureCreate,
    FeatureUpdate,
    FeatureResponse,
    FeatureListResponse,
    PlanFeatureCreate,
    PlanFeatureResponse,
    PlanFeatureListResponse,
    TenantFeatureCreate,
    TenantFeatureResponse,
    TenantFeatureListResponse,
    WorkspaceFeatureCreate,
    WorkspaceFeatureResponse,
    WorkspaceFeatureListResponse,
)
from synapse.schemas.base import PaginatedResponse

router = APIRouter()

# ====================
# FEATURES (Main table)
# ====================


@router.get("/", response_model=FeatureListResponse)
async def list_features(
    skip: int = Query(0, ge=0, description="Número de registros para pular"),
    limit: int = Query(100, ge=1, le=500, description="Número máximo de registros"),
    search: Optional[str] = Query(None, description="Buscar por nome ou descrição"),
    category: Optional[str] = Query(None, description="Filtrar por categoria"),
    is_active: Optional[bool] = Query(None, description="Filtrar por status ativo"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Listar todas as features disponíveis
    Acesso: Usuários autenticados
    """
    try:
        query = db.query(Feature)

        if search:
            query = query.filter(
                (Feature.name.ilike(f"%{search}%"))
                | (Feature.description.ilike(f"%{search}%"))
            )

        if category:
            query = query.filter(Feature.category == category)

        if is_active is not None:
            query = query.filter(Feature.is_active == is_active)

        total_count = query.count()
        features = query.offset(skip).limit(limit).all()

        feature_responses = [FeatureResponse.from_orm(feature) for feature in features]

        return FeatureListResponse(
            features=feature_responses,
            total_count=total_count,
            page=skip // limit + 1,
            page_size=limit,
            has_next=skip + limit < total_count,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao listar features: {str(e)}", extra={"error_type": type(e).__name__})
        raise


@router.post("/", response_model=FeatureResponse)
async def create_feature(
    feature_data: FeatureCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    Criar nova feature
    Acesso: Apenas administradores
    """
    try:
        # Verificar se já existe feature com mesmo código
        existing_feature = (
            db.query(Feature).filter(Feature.code == feature_data.code).first()
        )

        if existing_feature:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Já existe uma feature com este código",
            )

        # Criar nova feature
        feature = Feature(
            **feature_data.dict(),
            created_by=current_user.id,
            updated_by=current_user.id,
        )

        db.add(feature)
        db.commit()
        db.refresh(feature)

        return FeatureResponse.from_orm(feature)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao criar feature: {str(e)}", extra={"error_type": type(e).__name__})
        db.rollback()
        raise


@router.get("/{feature_id}", response_model=FeatureResponse)
async def get_feature(
    feature_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Obter feature por ID
    Acesso: Usuários autenticados
    """
    feature = db.query(Feature).filter(Feature.id == feature_id).first()

    if not feature:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Feature não encontrada"
        )

    return FeatureResponse.from_orm(feature)


@router.put("/{feature_id}", response_model=FeatureResponse)
async def update_feature(
    feature_id: uuid.UUID,
    feature_data: FeatureUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    Atualizar feature existente
    Acesso: Apenas administradores
    """
    try:
        feature = db.query(Feature).filter(Feature.id == feature_id).first()

        if not feature:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Feature não encontrada"
            )

        # Verificar conflito de código
        if feature_data.code and feature_data.code != feature.code:
            existing = (
                db.query(Feature)
                .filter(Feature.code == feature_data.code, Feature.id != feature_id)
                .first()
            )

            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Já existe uma feature com este código",
                )

        # Atualizar campos
        update_data = feature_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(feature, field, value)

        feature.updated_by = current_user.id
        feature.updated_at = datetime.utcnow()

        db.commit()
        db.refresh(feature)

        return FeatureResponse.from_orm(feature)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar feature: {str(e)}", extra={"error_type": type(e).__name__})
        db.rollback()
        raise


@router.delete("/{feature_id}")
async def delete_feature(
    feature_id: uuid.UUID,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    Deletar feature
    Acesso: Apenas administradores
    ATENÇÃO: Remove todas as associações com planos, tenants e workspaces
    """
    try:
        feature = db.query(Feature).filter(Feature.id == feature_id).first()

        if not feature:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Feature não encontrada"
            )

        # Remover associações primeiro
        db.query(PlanFeature).filter(PlanFeature.feature_id == feature_id).delete()
        db.query(TenantFeature).filter(TenantFeature.feature_id == feature_id).delete()
        db.query(WorkspaceFeature).filter(
            WorkspaceFeature.feature_id == feature_id
        ).delete()

        # Remover feature
        db.delete(feature)
        db.commit()

        return {"message": "Feature deletada com sucesso"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao deletar feature: {str(e)}", extra={"error_type": type(e).__name__})
        db.rollback()
        raise


# ========================
# PLAN FEATURES
# ========================


@router.get("/plans/{plan_id}/features", response_model=PlanFeatureListResponse)
async def list_plan_features(
    plan_id: uuid.UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Listar features de um plano específico
    Acesso: Usuários autenticados
    """
    try:
        query = db.query(PlanFeature).filter(PlanFeature.plan_id == plan_id)

        total_count = query.count()
        plan_features = query.offset(skip).limit(limit).all()

        plan_feature_responses = [
            PlanFeatureResponse.from_orm(pf) for pf in plan_features
        ]

        return PlanFeatureListResponse(
            plan_features=plan_feature_responses,
            total_count=total_count,
            page=skip // limit + 1,
            page_size=limit,
            has_next=skip + limit < total_count,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao listar features do plano: {str(e)}", extra={"error_type": type(e).__name__})
        raise


@router.post("/plans/{plan_id}/features", response_model=PlanFeatureResponse)
async def add_feature_to_plan(
    plan_id: uuid.UUID,
    plan_feature_data: PlanFeatureCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    Adicionar feature a um plano
    Acesso: Apenas administradores
    """
    try:
        # Verificar se já existe a associação
        existing = (
            db.query(PlanFeature)
            .filter(
                PlanFeature.plan_id == plan_id,
                PlanFeature.feature_id == plan_feature_data.feature_id,
            )
            .first()
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Feature já está associada a este plano",
            )

        # Criar associação
        plan_feature = PlanFeature(
            plan_id=plan_id,
            **plan_feature_data.dict(),
            created_by=current_user.id,
            updated_by=current_user.id,
        )

        db.add(plan_feature)
        db.commit()
        db.refresh(plan_feature)

        return PlanFeatureResponse.from_orm(plan_feature)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao adicionar feature ao plano: {str(e)}", extra={"error_type": type(e).__name__})
        db.rollback()
        raise


# ========================
# TENANT FEATURES
# ========================


@router.get("/tenants/{tenant_id}/features", response_model=TenantFeatureListResponse)
async def list_tenant_features(
    tenant_id: uuid.UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Listar features de um tenant específico
    Acesso: Usuários do tenant ou administradores
    """
    try:
        # Verificar se usuário tem acesso ao tenant
        if not current_user.is_superuser and current_user.tenant_id != tenant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Sem permissão para acessar features deste tenant",
            )

        query = db.query(TenantFeature).filter(TenantFeature.tenant_id == tenant_id)

        total_count = query.count()
        tenant_features = query.offset(skip).limit(limit).all()

        tenant_feature_responses = [
            TenantFeatureResponse.from_orm(tf) for tf in tenant_features
        ]

        return TenantFeatureListResponse(
            tenant_features=tenant_feature_responses,
            total_count=total_count,
            page=skip // limit + 1,
            page_size=limit,
            has_next=skip + limit < total_count,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao listar features do tenant: {str(e)}", extra={"error_type": type(e).__name__})
        raise


@router.post("/tenants/{tenant_id}/features", response_model=TenantFeatureResponse)
async def add_feature_to_tenant(
    tenant_id: uuid.UUID,
    tenant_feature_data: TenantFeatureCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    Adicionar feature a um tenant
    Acesso: Apenas administradores
    """
    try:
        # Verificar se já existe a associação
        existing = (
            db.query(TenantFeature)
            .filter(
                TenantFeature.tenant_id == tenant_id,
                TenantFeature.feature_id == tenant_feature_data.feature_id,
            )
            .first()
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Feature já está associada a este tenant",
            )

        # Criar associação
        tenant_feature = TenantFeature(
            tenant_id=tenant_id,
            **tenant_feature_data.dict(),
            created_by=current_user.id,
            updated_by=current_user.id,
        )

        db.add(tenant_feature)
        db.commit()
        db.refresh(tenant_feature)

        return TenantFeatureResponse.from_orm(tenant_feature)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao adicionar feature ao tenant: {str(e)}", extra={"error_type": type(e).__name__})
        db.rollback()
        raise


# ========================
# WORKSPACE FEATURES
# ========================


@router.get(
    "/workspaces/{workspace_id}/features", response_model=WorkspaceFeatureListResponse
)
async def list_workspace_features(
    workspace_id: uuid.UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Listar features de um workspace específico
    Acesso: Membros do workspace ou administradores
    """
    try:
        # TODO: Implementar verificação de acesso ao workspace
        # Por enquanto, verificamos apenas se o usuário está autenticado

        query = db.query(WorkspaceFeature).filter(
            WorkspaceFeature.workspace_id == workspace_id
        )

        total_count = query.count()
        workspace_features = query.offset(skip).limit(limit).all()

        workspace_feature_responses = [
            WorkspaceFeatureResponse.from_orm(wf) for wf in workspace_features
        ]

        return WorkspaceFeatureListResponse(
            workspace_features=workspace_feature_responses,
            total_count=total_count,
            page=skip // limit + 1,
            page_size=limit,
            has_next=skip + limit < total_count,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao listar features do workspace: {str(e)}", extra={"error_type": type(e).__name__})
        raise


@router.post(
    "/workspaces/{workspace_id}/features", response_model=WorkspaceFeatureResponse
)
async def add_feature_to_workspace(
    workspace_id: uuid.UUID,
    workspace_feature_data: WorkspaceFeatureCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    Adicionar feature a um workspace
    Acesso: Apenas administradores
    """
    try:
        # Verificar se já existe a associação
        existing = (
            db.query(WorkspaceFeature)
            .filter(
                WorkspaceFeature.workspace_id == workspace_id,
                WorkspaceFeature.feature_id == workspace_feature_data.feature_id,
            )
            .first()
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Feature já está associada a este workspace",
            )

        # Criar associação
        workspace_feature = WorkspaceFeature(
            workspace_id=workspace_id,
            **workspace_feature_data.dict(),
            created_by=current_user.id,
            updated_by=current_user.id,
        )

        db.add(workspace_feature)
        db.commit()
        db.refresh(workspace_feature)

        return WorkspaceFeatureResponse.from_orm(workspace_feature)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao adicionar feature ao workspace: {str(e)}", extra={"error_type": type(e).__name__})
        db.rollback()
        raise


# ========================
# UTILITY ENDPOINTS
# ========================


@router.get("/categories", response_model=List[str])
async def list_feature_categories(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """
    Listar todas as categorias de features disponíveis
    Acesso: Usuários autenticados
    """
    try:
        categories = (
            db.query(Feature.category)
            .distinct()
            .filter(Feature.category.isnot(None), Feature.is_active == True)
            .all()
        )

        return [cat[0] for cat in categories if cat[0]]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao listar categorias: {str(e)}", extra={"error_type": type(e).__name__})
        raise
