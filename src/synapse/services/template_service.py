"""
Serviço de Templates de Workflows
Criado por José - um desenvolvedor Full Stack
Sistema completo de marketplace de templates
"""

import uuid
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy import and_, or_, desc, asc, func, text, select
from sqlalchemy.exc import IntegrityError

from synapse.models import (
    WorkflowTemplate,
    TemplateReview,
    TemplateDownload,
    TemplateFavorite,
    TemplateCollection,
    TemplateUsage,
)
from synapse.models.template import (
    TemplateStatus,
    TemplateLicense,
)
from synapse.models import Workflow, Node, User
from synapse.schemas.template import (
    TemplateCreate,
    TemplateUpdate,
    TemplateResponse,
    TemplateDetailResponse,
    TemplateListResponse,
    TemplateFilter,
    TemplateStats,
    UserTemplateStats,
    ReviewCreate,
    ReviewUpdate,
    ReviewResponse,
    FavoriteCreate,
    FavoriteResponse,
    CollectionCreate,
    CollectionUpdate,
    CollectionResponse,
    TemplateInstall,
    TemplateInstallResponse,
    MarketplaceStats,
)

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TemplateService:
    """
    Serviço principal para gerenciamento de templates
    """

    def __init__(self):
        self.logger = logger

    async def create_template(
        self,
        db: AsyncSession,
        template_data: TemplateCreate,
        author_id: int,
        tenant_id: uuid.UUID,
        workflow_id: Optional[int] = None,
    ) -> TemplateResponse:
        """
        Cria um novo template de workflow
        """
        try:
            # Gera ID único para o template
            template_id = str(uuid.uuid4())

            # Valida se o workflow existe (se fornecido)
            original_workflow = None
            if workflow_id:
                original_workflow = (
                    await db.execute(select(Workflow))
                    .filter(Workflow.id == workflow_id, Workflow.user_id == author_id, Workflow.tenant_id == tenant_id)
                    .scalar_one_or_none()
                )
                if not original_workflow:
                    raise ValueError(
                        "Workflow não encontrado ou não pertence ao usuário"
                    )

            # Cria o template
            template = WorkflowTemplate(
                template_id=template_id,
                name=template_data.name,
                title=template_data.title,
                description=template_data.description,
                short_description=template_data.short_description,
                author_id=author_id,
                original_workflow_id=workflow_id,
                category=template_data.category.value,
                tags=template_data.tags,
                license_type=template_data.license_type.value,
                price=template_data.price,
                workflow_data=template_data.workflow_data,
                nodes_data=template_data.nodes_data,
                connections_data=template_data.connections_data,
                required_variables=template_data.required_variables,
                optional_variables=template_data.optional_variables,
                default_config=template_data.default_config,
                estimated_duration=template_data.estimated_duration,
                complexity_level=template_data.complexity_level,
                keywords=template_data.keywords,
                use_cases=template_data.use_cases,
                industries=template_data.industries,
                documentation=template_data.documentation,
                setup_instructions=template_data.setup_instructions,
                status=TemplateStatus.DRAFT.value,
            )

            db.add(template)
            await db.commit()
            await db.refresh(template)

            self.logger.info(f"✅ Template {template.id} criado com sucesso")
            return TemplateResponse.from_orm(template)

        except Exception as e:
            self.logger.error(f"❌ Erro ao criar template: {str(e)}")
            await db.rollback()
            raise

    async def update_template(
        self,
        db: AsyncSession,
        template_id: uuid.UUID,
        template_data: TemplateUpdate,
        user_id: uuid.UUID,
        tenant_id: uuid.UUID,
    ) -> Optional[TemplateResponse]:
        """
        Atualiza um template existente
        """
        try:
            template = (
                await db.execute(select(WorkflowTemplate))
                .filter(
                    WorkflowTemplate.id == template_id,
                    WorkflowTemplate.author_id == user_id,
                )
                .scalar_one_or_none()
            )

            if not template:
                return None

            # Atualiza campos fornecidos
            update_data = template_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                if hasattr(template, field):
                    setattr(template, field, value)

            # Atualiza timestamp
            template.updated_at = datetime.utcnow()

            await db.commit()
            await db.refresh(template)

            self.logger.info(f"✅ Template {template_id} atualizado com sucesso")
            return TemplateResponse.from_orm(template)

        except Exception as e:
            self.logger.error(f"❌ Erro ao atualizar template {template_id}: {str(e)}")
            await db.rollback()
            raise

    async def publish_template(
        self, db: AsyncSession, template_id: uuid.UUID, user_id: uuid.UUID, tenant_id: uuid.UUID
    ) -> bool:
        """
        Publica um template (torna público)
        """
        try:
            template = (
                await db.execute(select(WorkflowTemplate))
                .filter(
                    WorkflowTemplate.id == template_id,
                    WorkflowTemplate.author_id == user_id,
                    WorkflowTemplate.tenant_id == tenant_id,
                )
                .scalar_one_or_none()
            )

            if not template:
                return False

            # Valida se o template está pronto para publicação
            if not template.workflow_data or not template.nodes_data:
                raise ValueError(
                    "Template deve ter dados de workflow e nós para ser publicado"
                )

            template.status = TemplateStatus.PUBLISHED.value
            template.is_public = True
            template.published_at = datetime.utcnow()

            await db.commit()

            self.logger.info(f"✅ Template {template_id} publicado com sucesso")
            return True

        except Exception as e:
            self.logger.error(f"❌ Erro ao publicar template {template_id}: {str(e)}")
            await db.rollback()
            raise

    async def get_template(
        self,
        db: AsyncSession,
        template_id: str,
        tenant_id: uuid.UUID,
        user_id: Optional[int] = None,
        include_private: bool = False,
    ) -> Optional[TemplateDetailResponse]:
        """
        Obtém detalhes de um template
        """
        try:
            query = (
                select(WorkflowTemplate)
                .options(
                    joinedload(WorkflowTemplate.author),
                    joinedload(WorkflowTemplate.reviews),
                    joinedload(WorkflowTemplate.favorites),
                )
                .filter(WorkflowTemplate.id == template_id, WorkflowTemplate.tenant_id == tenant_id)
            )

            # Filtro de visibilidade
            if not include_private:
                query = query.filter(
                    or_(
                        WorkflowTemplate.is_public == True,
                        WorkflowTemplate.author_id == user_id if user_id else False,
                    ),
                )

            template = query.scalar_one_or_none()

            if not template:
                return None

            # Incrementa contador de visualizações
            template.view_count += 1
            await db.commit()

            # Verifica se o usuário favoritou
            is_favorited = False
            if user_id:
                favorite = (
                    await db.execute(select(TemplateFavorite))
                    .filter(
                        TemplateFavorite.template_id == template.id,
                        TemplateFavorite.user_id == user_id,
                    )
                    .scalar_one_or_none()
                )
                is_favorited = favorite is not None

            # Calcula estatísticas recentes (últimos 30 dias)
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            recent_downloads = (
                await db.execute(select(TemplateDownload))
                .filter(
                    TemplateDownload.template_id == template.id,
                    TemplateDownload.downloaded_at >= thirty_days_ago,
                )
                .scalar()
            )

            recent_usage = (
                await db.execute(select(TemplateUsage))
                .filter(
                    TemplateUsage.template_id == template.id,
                    TemplateUsage.used_at >= thirty_days_ago,
                )
                .scalar()
            )

            # Monta resposta detalhada
            response_data = TemplateResponse.from_orm(template).dict()
            response_data.update(
                {
                    "workflow_data": template.workflow_data,
                    "nodes_data": template.nodes_data,
                    "connections_data": template.connections_data,
                    "required_variables": template.required_variables,
                    "optional_variables": template.optional_variables,
                    "default_config": template.default_config,
                    "changelog": template.changelog,
                    "author_name": (
                        template.author.full_name if template.author else None
                    ),
                    "author_avatar": (
                        getattr(template.author, "avatar_url", None)
                        if template.author
                        else None
                    ),
                    "recent_downloads": recent_downloads,
                    "recent_usage": recent_usage,
                    "is_favorited": is_favorited,
                }
            )

            return TemplateDetailResponse(**response_data)

        except Exception as e:
            self.logger.error(f"❌ Erro ao obter template {template_id}: {str(e)}")
            raise

    async def search_templates(
        self,
        db: AsyncSession,
        filters: TemplateFilter,
        tenant_id: uuid.UUID,
        user_id: int | None = None,
    ) -> TemplateListResponse:
        """
        Busca templates com filtros avançados
        """
        try:
            query = await db.execute(select(WorkflowTemplate)).options(
                joinedload(WorkflowTemplate.author),
            )

            # Filtro de visibilidade (apenas públicos por padrão)
            query = query.filter(WorkflowTemplate.is_public == True)
            query = query.filter(
                WorkflowTemplate.status == TemplateStatus.PUBLISHED.value
            )

            # Filtros de busca
            if filters.search:
                search_term = f"%{filters.search}%"
                query = query.filter(
                    or_(
                        WorkflowTemplate.title.ilike(search_term),
                        WorkflowTemplate.description.ilike(search_term),
                        WorkflowTemplate.short_description.ilike(search_term),
                        WorkflowTemplate.keywords.contains([filters.search.lower()]),
                    ),
                )

            if filters.category:
                categories = [cat.value for cat in filters.category]
                query = query.filter(WorkflowTemplate.category.in_(categories))

            if filters.tags:
                for tag in filters.tags:
                    query = query.filter(WorkflowTemplate.tags.contains([tag]))

            if filters.license_type:
                licenses = [lic.value for lic in filters.license_type]
                query = query.filter(WorkflowTemplate.license_type.in_(licenses))

            if filters.price_min is not None:
                query = query.filter(WorkflowTemplate.price >= filters.price_min)

            if filters.price_max is not None:
                query = query.filter(WorkflowTemplate.price <= filters.price_max)

            if filters.rating_min is not None:
                query = query.filter(
                    WorkflowTemplate.rating_average >= filters.rating_min
                )

            if filters.complexity_min is not None:
                query = query.filter(
                    WorkflowTemplate.complexity_level >= filters.complexity_min
                )

            if filters.complexity_max is not None:
                query = query.filter(
                    WorkflowTemplate.complexity_level <= filters.complexity_max
                )

            if filters.is_featured is not None:
                query = query.filter(
                    WorkflowTemplate.is_featured == filters.is_featured
                )

            if filters.is_verified is not None:
                query = query.filter(
                    WorkflowTemplate.is_verified == filters.is_verified
                )

            if filters.author_id:
                query = query.filter(WorkflowTemplate.author_id == filters.author_id, WorkflowTemplate.tenant_id == tenant_id)

            if filters.created_after:
                query = query.filter(
                    WorkflowTemplate.created_at >= filters.created_after
                )

            if filters.created_before:
                query = query.filter(
                    WorkflowTemplate.created_at <= filters.created_before
                )

            if filters.industries:
                for industry in filters.industries:
                    query = query.filter(
                        WorkflowTemplate.industries.contains([industry])
                    )

            if filters.use_cases:
                for use_case in filters.use_cases:
                    query = query.filter(
                        WorkflowTemplate.use_cases.contains([use_case])
                    )

            # Ordenação
            if filters.sort_by == "rating":
                order_col = WorkflowTemplate.rating_average
            elif filters.sort_by == "downloads":
                order_col = WorkflowTemplate.download_count
            elif filters.sort_by == "name":
                order_col = WorkflowTemplate.title
            elif filters.sort_by == "price":
                order_col = WorkflowTemplate.price
            elif filters.sort_by == "updated_at":
                order_col = WorkflowTemplate.updated_at
            else:
                order_col = WorkflowTemplate.created_at

            if filters.sort_order == "desc":
                query = query.order_by(desc(order_col))
            else:
                query = query.order_by(asc(order_col))

            # Contagem total
            total = query.scalar()

            # Paginação
            offset = (filters.page - 1) * filters.per_page
            templates = query.offset(offset).limit(filters.per_page).scalars().all()

            # Calcula informações de paginação
            pages = (total + filters.per_page - 1) // filters.per_page
            has_next = filters.page < pages
            has_prev = filters.page > 1

            return TemplateListResponse(
                templates=[TemplateResponse.from_orm(t) for t in templates],
                total=total,
                page=filters.page,
                per_page=filters.per_page,
                pages=pages,
                has_next=has_next,
                has_prev=has_prev,
            )

        except Exception as e:
            self.logger.error(f"❌ Erro na busca de templates: {str(e)}")
            raise

    async def download_template(
        self,
        db: AsyncSession,
        template_id: str,
        user_id: int,
        tenant_id: uuid.UUID,
        download_type: str = "full",
    ) -> bool:
        """
        Registra download de template
        """
        try:
            template = (
                await db.execute(select(WorkflowTemplate))
                .filter(
                    WorkflowTemplate.id == template_id,
                    WorkflowTemplate.is_public == True,
                )
                .scalar_one_or_none()
            )

            if not template:
                return False

            # Registra o download
            download = TemplateDownload(
                template_id=template.id,
                user_id=user_id,
                download_type=download_type,
                template_version=template.version,
                tenant_id=tenant_id,
            )

            db.add(download)

            # Incrementa contador
            template.download_count += 1
            template.last_used_at = datetime.utcnow()

            await db.commit()

            self.logger.info(
                f"✅ Download do template {template_id} registrado para usuário {user_id}"
            )
            return True

        except Exception as e:
            self.logger.error(f"❌ Erro ao registrar download: {str(e)}")
            await db.rollback()
            raise

    async def install_template(
        self,
        db: AsyncSession,
        install_data: TemplateInstall,
        user_id: int,
        tenant_id: uuid.UUID,
    ) -> TemplateInstallResponse:
        """
        Instala um template como novo workflow
        """
        try:
            template = (
                await db.execute(select(WorkflowTemplate))
                .filter(
                    WorkflowTemplate.id == install_data.template_id,
                    WorkflowTemplate.is_public == True,
                )
                .scalar_one_or_none()
            )

            if not template:
                raise ValueError("Template não encontrado")

            # Nome do workflow
            workflow_name = (
                install_data.workflow_name or f"{template.title} (Instalado)"
            )

            # Cria novo workflow baseado no template
            workflow_data = template.workflow_data.copy()
            workflow_data["name"] = workflow_name

            # Aplica variáveis customizadas
            if install_data.custom_variables:
                workflow_data["variables"] = install_data.custom_variables

            # Aplica configurações customizadas
            if install_data.modify_config:
                workflow_data.update(install_data.modify_config)

            # Cria o workflow
            new_workflow = Workflow(
                name=workflow_name,
                description=f"Criado a partir do template: {template.title}",
                user_id=user_id,
                config=workflow_data,
                is_active=True,
            )

            db.add(new_workflow)
            db.flush()  # Para obter o ID

            # Cria os nós
            modifications_applied = []
            warnings = []
            errors = []

            for i, node_data in enumerate(template.nodes_data):
                try:
                    node = Node(
                        name=node_data.get("name", f"Node {i+1}"),
                        type=node_data.get("type", "generic"),
                        description=node_data.get("description", ""),
                        workflow_id=new_workflow.id,
                        user_id=user_id,
                        config=node_data.get("config", {}),
                        position=i,
                        is_active=True,
                    )
                    db.add(node)
                    modifications_applied.append(f"Nó '{node.name}' criado")
                except Exception as e:
                    errors.append(f"Erro ao criar nó {i+1}: {str(e)}")

            # Registra uso do template
            usage = TemplateUsage(
                template_id=template.id,
                user_id=user_id,
                workflow_id=new_workflow.id,
                usage_type="create",
                success=len(errors) == 0,
                template_version=template.version,
                modifications_made=install_data.dict(),
                tenant_id=tenant_id,
            )

            db.add(usage)

            # Incrementa contador de uso
            template.usage_count += 1
            template.last_used_at = datetime.utcnow()

            await db.commit()

            self.logger.info(
                f"✅ Template {template.id} instalado como workflow {new_workflow.id}"
            )

            return TemplateInstallResponse(
                success=len(errors) == 0,
                workflow_id=new_workflow.id,
                workflow_name=workflow_name,
                template_id=template.id,
                template_name=template.title,
                modifications_applied=modifications_applied,
                warnings=warnings,
                errors=errors,
            )

        except Exception as e:
            self.logger.error(f"❌ Erro ao instalar template: {str(e)}")
            await db.rollback()
            raise

    async def add_to_favorites(
        self,
        db: AsyncSession,
        favorite_data: FavoriteCreate,
        user_id: int,
        tenant_id: uuid.UUID,
    ) -> FavoriteResponse | None:
        """
        Adiciona template aos favoritos
        """
        try:
            # Verifica se já está nos favoritos
            existing = (
                await db.execute(select(TemplateFavorite))
                .filter(
                    TemplateFavorite.template_id == favorite_data.template_id,
                    TemplateFavorite.user_id == user_id,
                )
                .scalar_one_or_none()
            )

            if existing:
                return None  # Já está nos favoritos

            # Verifica se o template existe
            template = (
                await db.execute(select(WorkflowTemplate))
                .filter(
                    WorkflowTemplate.id == favorite_data.template_id,
                    WorkflowTemplate.is_public == True,
                )
                .scalar_one_or_none()
            )

            if not template:
                raise ValueError("Template não encontrado")

            favorite = TemplateFavorite(
                template_id=favorite_data.template_id,
                user_id=user_id,
                notes=favorite_data.notes,
                tenant_id=tenant_id,
            )

            db.add(favorite)
            await db.commit()
            await db.refresh(favorite)

            # Monta resposta
            response_data = {
                "id": favorite.id,
                "template_id": favorite.template_id,
                "user_id": favorite.user_id,
                "notes": favorite.notes,
                "created_at": favorite.created_at,
                "template_name": template.name,
                "template_title": template.title,
                "template_category": template.category,
            }

            return FavoriteResponse(**response_data)

        except Exception as e:
            self.logger.error(f"❌ Erro ao adicionar favorito: {str(e)}")
            await db.rollback()
            raise

    async def get_user_favorites(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        tenant_id: uuid.UUID,
        page: int = 1,
        per_page: int = 20,
    ) -> list[FavoriteResponse]:
        """
        Obtém favoritos do usuário
        """
        try:
            offset = (page - 1) * per_page

            favorites = (
                await db.execute(select(TemplateFavorite))
                .options(
                    joinedload(TemplateFavorite.template),
                )
                .filter(
                    TemplateFavorite.user_id == user_id,
                    TemplateFavorite.tenant_id == tenant_id,
                )
                .order_by(desc(TemplateFavorite.created_at))
                .offset(offset)
                .limit(per_page)
                .scalars()
                .all()
            )

            return [
                FavoriteResponse(
                    id=fav.id,
                    template_id=fav.template_id,
                    user_id=fav.user_id,
                    notes=fav.notes,
                    created_at=fav.created_at,
                    template_name=fav.template.name,
                    template_title=fav.template.title,
                    template_category=fav.template.category,
                )
                for fav in favorites
            ]

        except Exception as e:
            self.logger.error(f"❌ Erro ao obter favoritos: {str(e)}")
            raise

    async def get_template_stats(self, db: AsyncSession) -> TemplateStats:
        """
        Obtém estatísticas gerais de templates
        """
        try:
            # Contadores básicos
            total = await db.execute(select(WorkflowTemplate)).scalar()
            published = (
                await db.execute(select(WorkflowTemplate))
                .filter(
                    WorkflowTemplate.status == TemplateStatus.PUBLISHED.value,
                )
                .scalar()
            )
            featured = (
                await db.execute(select(WorkflowTemplate))
                .filter(
                    WorkflowTemplate.is_featured == True,
                )
                .scalar()
            )
            verified = (
                await db.execute(select(WorkflowTemplate))
                .filter(
                    WorkflowTemplate.is_verified == True,
                )
                .scalar()
            )
            free = (
                await db.execute(select(WorkflowTemplate))
                .filter(
                    WorkflowTemplate.license_type == TemplateLicense.FREE.value,
                )
                .scalar()
            )
            premium = (
                await db.execute(select(WorkflowTemplate))
                .filter(
                    WorkflowTemplate.license_type.in_(
                        [
                            TemplateLicense.PREMIUM.value,
                            TemplateLicense.ENTERPRISE.value,
                        ]
                    ),
                    WorkflowTemplate.tenant_id == tenant_id,
                )
                .scalar()
            )

            # Estatísticas agregadas
            total_downloads = (
                await db.execute(
                    select(func.sum(WorkflowTemplate.download_count))
                ).scalar()
                or 0
            )
            total_reviews = await db.execute(select(TemplateReview)).scalar()
            avg_rating = (
                await db.execute(
                    select(func.avg(WorkflowTemplate.rating_average)).filter(WorkflowTemplate.tenant_id == tenant_id)
                ).scalar()
                or 0.0
            )

            # Distribuição por categorias
            categories = (
                await db.execute(
                    select(
                        WorkflowTemplate.category, func.count(WorkflowTemplate.id)
                    ).label("count"),
                )
                .filter(
                    WorkflowTemplate.status == TemplateStatus.PUBLISHED.value,
                )
                .group_by(WorkflowTemplate.category)
                .scalars()
                .all()
            )

            categories_distribution = {cat[0]: cat[1] for cat in categories}

            # Top templates (mais baixados)
            top_templates = (
                await db.execute(select(WorkflowTemplate))
                .filter(
                    WorkflowTemplate.is_public == True,
                )
                .order_by(
                    desc(WorkflowTemplate.download_count),
                )
                .limit(10)
                .scalars()
                .all()
            )

            # Templates recentes
            recent_templates = (
                await db.execute(select(WorkflowTemplate))
                .filter(
                    WorkflowTemplate.is_public == True,
                )
                .order_by(
                    desc(WorkflowTemplate.created_at),
                )
                .limit(10)
                .scalars()
                .all()
            )

            return TemplateStats(
                total_templates=total,
                published_templates=published,
                featured_templates=featured,
                verified_templates=verified,
                free_templates=free,
                premium_templates=premium,
                total_downloads=total_downloads,
                total_reviews=total_reviews,
                average_rating=round(avg_rating, 2),
                categories_distribution=categories_distribution,
                top_templates=[TemplateResponse.from_orm(t) for t in top_templates],
                recent_templates=[
                    TemplateResponse.from_orm(t) for t in recent_templates
                ],
            )

        except Exception as e:
            self.logger.error(f"❌ Erro ao obter estatísticas: {str(e)}")
            raise

    async def get_user_template_stats(
        self, db: AsyncSession, user_id: int
    ) -> UserTemplateStats:
        """
        Obtém estatísticas de templates do usuário
        """
        try:
            created = (
                await db.execute(select(WorkflowTemplate))
                .filter(
                    WorkflowTemplate.author_id == user_id,
                )
                .scalar()
            )

            published = (
                await db.execute(select(WorkflowTemplate))
                .filter(
                    WorkflowTemplate.author_id == user_id,
                    WorkflowTemplate.status == TemplateStatus.PUBLISHED.value,
                )
                .scalar()
            )

            # Downloads dos templates do usuário
            total_downloads = (
                await db.execute(select(func.sum(WorkflowTemplate.download_count)))
                .filter(
                    WorkflowTemplate.author_id == user_id,
                )
                .scalar()
                or 0
            )

            # Reviews dos templates do usuário
            total_reviews = (
                await db.execute(select(TemplateReview))
                .join(WorkflowTemplate)
                .filter(
                    WorkflowTemplate.author_id == user_id,
                )
                .scalar()
            )

            # Rating médio
            avg_rating = (
                await db.execute(select(func.avg(WorkflowTemplate.rating_average)))
                .filter(
                    WorkflowTemplate.author_id == user_id,
                )
                .scalar()
                or 0.0
            )

            # Favoritos do usuário
            favorites = (
                await db.execute(select(TemplateFavorite))
                .filter(
                    TemplateFavorite.user_id == user_id,
                    TemplateFavorite.tenant_id == tenant_id,
                )
                .scalar()
            )

            # Coleções do usuário
            collections = (
                await db.execute(select(TemplateCollection))
                .filter(
                    TemplateCollection.creator_id == user_id,
                )
                .scalar()
            )

            # Ganhos (templates premium)
            earnings = (
                await db.execute(
                    select(
                        func.sum(
                            WorkflowTemplate.price * WorkflowTemplate.download_count,
                        )
                    ),
                )
                .filter(
                    WorkflowTemplate.author_id == user_id,
                    WorkflowTemplate.license_type.in_(
                        [
                            TemplateLicense.PREMIUM.value,
                            TemplateLicense.ENTERPRISE.value,
                        ]
                    ),
                )
                .scalar()
                or 0.0
            )

            return UserTemplateStats(
                created_templates=created,
                published_templates=published,
                total_downloads=total_downloads,
                total_reviews=total_reviews,
                average_rating=round(avg_rating, 2),
                favorite_templates=favorites,
                template_collections=collections,
                total_earnings=round(earnings, 2),
            )

        except Exception as e:
            self.logger.error(f"❌ Erro ao obter estatísticas do usuário: {str(e)}")
            raise

    async def count_authors(self, db: AsyncSession) -> int:
        """
        Conta o número total de autores únicos
        """
        try:
            result = await db.execute(
                select(func.count(func.distinct(WorkflowTemplate.author_id))).where(
                    WorkflowTemplate.status == TemplateStatus.PUBLISHED.value
                )
            )
            return result.scalar() or 0
        except Exception as e:
            self.logger.error(f"❌ Erro ao contar autores: {str(e)}")
            return 0

    async def get_trending_templates(
        self, db: AsyncSession, limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Obtém templates em tendência baseado em downloads recentes
        """
        try:
            # Últimos 7 dias
            recent_date = datetime.utcnow() - timedelta(days=7)

            result = await db.execute(
                select(WorkflowTemplate)
                .where(
                    and_(
                        WorkflowTemplate.status == TemplateStatus.PUBLISHED.value,
                        WorkflowTemplate.created_at >= recent_date,
                    )
                )
                .order_by(
                    desc(WorkflowTemplate.downloads), desc(WorkflowTemplate.rating)
                )
                .limit(limit)
            )
            templates = result.scalars().all()

            return [
                {
                    "id": template.id,
                    "name": template.name,
                    "downloads": template.downloads,
                    "rating": template.rating,
                }
                for template in templates
            ]
        except Exception as e:
            self.logger.error(f"❌ Erro ao obter templates em tendência: {str(e)}")
            return []

    async def get_top_categories(
        self, db: AsyncSession, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Obtém as principais categorias por número de templates
        """
        try:
            result = await db.execute(
                select(
                    WorkflowTemplate.category,
                    func.count(WorkflowTemplate.id).label("count"),
                )
                .where(WorkflowTemplate.status == TemplateStatus.PUBLISHED.value)
                .group_by(WorkflowTemplate.category)
                .order_by(desc("count"))
                .limit(limit)
            )
            rows = result.all()

            return [{"category": row.category, "count": row.count} for row in rows]
        except Exception as e:
            self.logger.error(f"❌ Erro ao obter principais categorias: {str(e)}")
            return []

    async def get_top_authors(
        self, db: AsyncSession, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Obtém os principais autores por número de templates publicados
        """
        try:
            result = await db.execute(
                select(
                    WorkflowTemplate.author_id,
                    User.username,
                    func.count(WorkflowTemplate.id).label("template_count"),
                    func.sum(WorkflowTemplate.downloads).label("total_downloads"),
                )
                .join(User, WorkflowTemplate.author_id == User.id)
                .where(WorkflowTemplate.status == TemplateStatus.PUBLISHED.value)
                .group_by(WorkflowTemplate.author_id, User.username)
                .order_by(desc("template_count"))
                .limit(limit)
            )
            rows = result.all()

            return [
                {
                    "author_id": row.author_id,
                    "username": row.username,
                    "template_count": row.template_count,
                    "total_downloads": row.total_downloads or 0,
                }
                for row in rows
            ]
        except Exception as e:
            self.logger.error(f"❌ Erro ao obter principais autores: {str(e)}")
            return []
