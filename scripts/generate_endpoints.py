#!/usr/bin/env python3
"""
Script automatizado para gerar endpoints REST completos.
Analisa os schemas existentes e gera endpoints CRUD padrão.
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Set
import re

# Adicionar src ao path
sys.path.insert(0, 'src')

class EndpointGenerator:
    def __init__(self):
        self.src_path = Path('src')
        self.schemas_path = self.src_path / 'synapse' / 'schemas'
        self.endpoints_path = self.src_path / 'synapse' / 'api' / 'v1' / 'endpoints'
        self.existing_endpoints = self._get_existing_endpoints()
        self.schemas_info = self._analyze_schemas()
        
    def _get_existing_endpoints(self) -> Set[str]:
        """Obter lista de endpoints já existentes."""
        existing = set()
        for file in self.endpoints_path.glob('*.py'):
            if file.name != '__init__.py':
                # Remover .py e converter para formato schema
                name = file.stem
                # Converter de plural para singular se necessário
                if name.endswith('s') and name != 'analytics':
                    name = name[:-1]
                existing.add(name)
        return existing

    def _analyze_schemas(self) -> Dict[str, Dict]:
        """Analisar schemas existentes para extrair informações."""
        schemas = {}
        
        for file in self.schemas_path.glob('*.py'):
            if file.name.startswith('__') or file.name in ['base.py', 'auth.py', 'error.py']:
                continue
                
            schema_name = file.stem
            schemas[schema_name] = self._extract_schema_info(file)
            
        return schemas

    def _extract_schema_info(self, file_path: Path) -> Dict:
        """Extrair informações de um arquivo de schema."""
        try:
            content = file_path.read_text()
            
            # Detectar classes principais
            classes = re.findall(r'class (\w+)\(.*?\):', content)
            
            # Identificar schemas principais
            create_class = next((c for c in classes if c.endswith('Create')), None)
            update_class = next((c for c in classes if c.endswith('Update')), None)
            response_class = next((c for c in classes if c.endswith('Response')), None)
            list_class = next((c for c in classes if c.endswith('ListResponse')), None)
            
            # Detectar modelo correspondente
            model_name = self._detect_model_name(file_path.stem, content)
            
            # Detectar se precisa de tenant_id
            needs_tenant = 'tenant_id' in content
            
            return {
                'file_name': file_path.stem,
                'create_class': create_class,
                'update_class': update_class,
                'response_class': response_class,
                'list_class': list_class,
                'model_name': model_name,
                'needs_tenant': needs_tenant,
                'classes': classes,
                'priority': self._calculate_priority(file_path.stem, content)
            }
        except Exception as e:
            print(f"❌ Erro ao analisar {file_path}: {e}")
            return {}

    def _detect_model_name(self, schema_name: str, content: str) -> str:
        """Detectar o nome do modelo correspondente."""
        # Tentar detectar do import
        model_match = re.search(r'from synapse\.models import (\w+)', content)
        if model_match:
            return model_match.group(1)
            
        # Fallback: converter schema name para model name
        # agent_quota -> AgentQuota
        words = schema_name.split('_')
        return ''.join(word.capitalize() for word in words)

    def _calculate_priority(self, schema_name: str, content: str) -> int:
        """Calcular prioridade do endpoint (1=alta, 3=baixa)."""
        critical_schemas = [
            'coupon', 'metric_type', 'agent_error_log', 'event_type',
            'plan_entitlement', 'tenant_feature', 'workflow_execution_metric',
            'conversation_llm', 'user_digitalocean', 'conversion_journey'
        ]
        
        important_schemas = [
            'plan_provider_mapping', 'payment_method', 'analytics_report',
            'analytics_event', 'analytics_metric', 'execution_status'
        ]
        
        if schema_name in critical_schemas:
            return 1
        elif schema_name in important_schemas:
            return 2
        else:
            return 3

    def generate_endpoint_template(self, schema_info: Dict) -> str:
        """Gerar template de endpoint baseado nas informações do schema."""
        schema_name = schema_info['file_name']
        model_name = schema_info['model_name']
        create_class = schema_info.get('create_class') or f'{model_name}Create'
        update_class = schema_info.get('update_class') or f'{model_name}Update'
        response_class = schema_info.get('response_class') or f'{model_name}Response'
        list_class = schema_info.get('list_class') or f'{model_name}ListResponse'
        
        # Garantir que não há None
        if not create_class or create_class == 'None':
            create_class = f'{model_name}Create'
        if not update_class or update_class == 'None':
            update_class = f'{model_name}Update'
        if not response_class or response_class == 'None':
            response_class = f'{model_name}Response'
        if not list_class or list_class == 'None':
            list_class = f'{model_name}ListResponse'
        
        # Converter schema_name para endpoint name (plural)
        endpoint_name = self._schema_to_endpoint_name(schema_name)
        
        # Detectar se é uma entidade que precisa de tenant_id
        tenant_filter = ""
        if schema_info.get('needs_tenant', False):
            tenant_filter = f", {model_name}.tenant_id == current_user.tenant_id"

        template = f'''"""
Endpoints for managing {model_name}s.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import List, Optional
import uuid

from synapse.api.deps import get_current_active_user
from synapse.database import get_async_db
from synapse.schemas.{schema_name} import (
    {create_class},
    {update_class},
    {response_class},
    {list_class},
)
from synapse.models import {model_name}, User

router = APIRouter()


@router.post("/", response_model={response_class}, status_code=status.HTTP_201_CREATED)
async def create_{schema_name}(
    item_in: {create_class},
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a new {schema_name.replace('_', ' ')}."""
    create_data = item_in.model_dump()
    {self._generate_tenant_assignment(schema_info)}
    db_item = {model_name}(**create_data)
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)
    return db_item


@router.get("/{{item_id}}", response_model={response_class})
async def get_{schema_name}(
    item_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a specific {schema_name.replace('_', ' ')} by its ID."""
    result = await db.execute(
        select({model_name}).where({model_name}.id == item_id{tenant_filter})
    )
    item = result.scalar_one_or_none()

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="{model_name} not found"
        )
    return item


@router.get("/", response_model={list_class})
async def list_{endpoint_name}(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    search: Optional[str] = Query(None, description="Search term"),
):
    """List all {endpoint_name.replace('_', ' ')} for the current user."""
    query = select({model_name}){self._generate_tenant_where_clause(schema_info)}
    
    if search:
        search_term = f"%{{search}}%"
        # Add search logic here based on model fields
        pass

    count_query = select(func.count()).select_from(query.subquery())
    count_result = await db.execute(count_query)
    total = count_result.scalar()

    query = query.offset((page - 1) * size).limit(size)
    result = await db.execute(query)
    items = result.scalars().all()

    return {list_class}(
        items=items,
        total=total,
        page=page,
        size=size,
    )


@router.put("/{{item_id}}", response_model={response_class})
async def update_{schema_name}(
    item_id: uuid.UUID,
    item_in: {update_class},
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update an existing {schema_name.replace('_', ' ')}."""
    result = await db.execute(
        select({model_name}).where({model_name}.id == item_id{tenant_filter})
    )
    db_item = result.scalar_one_or_none()

    if not db_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="{model_name} not found"
        )

    update_data = item_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_item, field, value)

    await db.commit()
    await db.refresh(db_item)
    return db_item


@router.delete("/{{item_id}}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_{schema_name}(
    item_id: uuid.UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Delete a {schema_name.replace('_', ' ')}."""
    result = await db.execute(
        select({model_name}).where({model_name}.id == item_id{tenant_filter})
    )
    db_item = result.scalar_one_or_none()

    if not db_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="{model_name} not found"
        )

    await db.delete(db_item)
    await db.commit()
'''

        return template

    def _schema_to_endpoint_name(self, schema_name: str) -> str:
        """Converter nome do schema para nome do endpoint (plural)."""
        # Casos especiais
        special_cases = {
            'analytics': 'analytics',
            'analytics_event': 'analytics_events',
            'analytics_report': 'analytics_reports',
            'analytics_metric': 'analytics_metrics',
        }
        
        if schema_name in special_cases:
            return special_cases[schema_name]
            
        # Regra geral: adicionar 's' se não terminar com 's'
        if not schema_name.endswith('s'):
            return f"{schema_name}s"
        return schema_name

    def _generate_tenant_assignment(self, schema_info: Dict) -> str:
        """Gerar código para assignar tenant_id se necessário."""
        if schema_info.get('needs_tenant', False):
            return "if 'tenant_id' not in create_data:\n        create_data['tenant_id'] = current_user.tenant_id"
        return ""

    def _generate_tenant_where_clause(self, schema_info: Dict) -> str:
        """Gerar cláusula WHERE para tenant se necessário."""
        if schema_info.get('needs_tenant', False):
            model_name = schema_info['model_name']
            return f".where({model_name}.tenant_id == current_user.tenant_id)"
        return ""

    def get_missing_endpoints(self) -> List[Dict]:
        """Obter lista de schemas que não têm endpoints correspondentes."""
        missing = []
        
        for schema_name, schema_info in self.schemas_info.items():
            # Verificar se já existe endpoint
            endpoint_exists = any(
                existing in schema_name or schema_name in existing 
                for existing in self.existing_endpoints
            )
            
            if not endpoint_exists and schema_info.get('create_class'):
                missing.append(schema_info)
                
        # Ordenar por prioridade
        missing.sort(key=lambda x: x.get('priority', 3))
        return missing

    def generate_missing_endpoints(self, limit: int = None) -> int:
        """Gerar todos os endpoints que estão faltando."""
        missing = self.get_missing_endpoints()
        
        if limit:
            missing = missing[:limit]
            
        print(f"🚀 Gerando {len(missing)} endpoints...")
        generated = 0
        
        for schema_info in missing:
            try:
                schema_name = schema_info['file_name']
                endpoint_content = self.generate_endpoint_template(schema_info)
                
                # Nome do arquivo endpoint (plural)
                endpoint_filename = self._schema_to_endpoint_name(schema_name) + '.py'
                endpoint_path = self.endpoints_path / endpoint_filename
                
                # Verificar se já existe
                if endpoint_path.exists():
                    print(f"⚠️  {endpoint_filename} já existe, pulando...")
                    continue
                
                # Criar arquivo
                endpoint_path.write_text(endpoint_content)
                print(f"✅ Criado: {endpoint_filename}")
                generated += 1
                
            except Exception as e:
                print(f"❌ Erro ao gerar endpoint para {schema_info.get('file_name', 'unknown')}: {e}")
        
        return generated

    def update_api_router(self, new_endpoints: List[str]):
        """Atualizar o arquivo api.py com os novos endpoints."""
        api_file = self.src_path / 'synapse' / 'api' / 'v1' / 'api.py'
        
        try:
            content = api_file.read_text()
            
            # Adicionar imports
            import_section = "from synapse.api.v1.endpoints import ("
            import_end = ")"
            
            # Encontrar seção de imports
            import_start_pos = content.find(import_section)
            import_end_pos = content.find(import_end, import_start_pos)
            
            if import_start_pos != -1 and import_end_pos != -1:
                current_imports = content[import_start_pos:import_end_pos + 1]
                
                # Adicionar novos imports
                for endpoint in new_endpoints:
                    import_name = endpoint.replace('.py', '')
                    if import_name not in current_imports:
                        # Adicionar import antes do )
                        content = content.replace(
                            import_end,
                            f"    {import_name},  # 🆕 Auto-generated\n{import_end}"
                        )
            
            api_file.write_text(content)
            print(f"✅ Atualizou api.py com {len(new_endpoints)} novos imports")
            
        except Exception as e:
            print(f"❌ Erro ao atualizar api.py: {e}")

    def generate_report(self):
        """Gerar relatório do que será criado."""
        missing = self.get_missing_endpoints()
        
        print("📊 RELATÓRIO DE ENDPOINTS FALTANTES")
        print("=" * 60)
        print(f"📁 Endpoints existentes: {len(self.existing_endpoints)}")
        print(f"📋 Schemas analisados: {len(self.schemas_info)}")
        print(f"🆕 Endpoints para criar: {len(missing)}")
        print()
        
        if missing:
            print("🔴 PRIORIDADE ALTA:")
            high = [s for s in missing if s.get('priority', 3) == 1]
            for schema in high:
                print(f"   - {schema['file_name']} -> {self._schema_to_endpoint_name(schema['file_name'])}.py")
            
            print("\n🟡 PRIORIDADE MÉDIA:")
            medium = [s for s in missing if s.get('priority', 3) == 2]
            for schema in medium:
                print(f"   - {schema['file_name']} -> {self._schema_to_endpoint_name(schema['file_name'])}.py")
            
            print("\n🟢 PRIORIDADE BAIXA:")
            low = [s for s in missing if s.get('priority', 3) == 3]
            for schema in low:
                print(f"   - {schema['file_name']} -> {self._schema_to_endpoint_name(schema['file_name'])}.py")


def main():
    generator = EndpointGenerator()
    
    # Gerar relatório
    generator.generate_report()
    
    print("\n🤖 GERAÇÃO AUTOMÁTICA DE ENDPOINTS")
    print("=" * 60)
    
    # Gerar apenas endpoints de alta prioridade primeiro
    missing = generator.get_missing_endpoints()
    high_priority = [s for s in missing if s.get('priority', 3) == 1]
    low_priority = [s for s in missing if s.get('priority', 3) == 3]
    
    print(f"🚀 Gerando {len(high_priority)} endpoints de ALTA PRIORIDADE...")
    
    # Gerar endpoints de alta prioridade
    generated = 0
    for schema_info in high_priority:
        try:
            schema_name = schema_info['file_name']
            endpoint_content = generator.generate_endpoint_template(schema_info)
            
            # Nome do arquivo endpoint (plural)
            endpoint_filename = generator._schema_to_endpoint_name(schema_name) + '.py'
            endpoint_path = generator.endpoints_path / endpoint_filename
            
            # Verificar se já existe
            if endpoint_path.exists():
                print(f"⚠️  {endpoint_filename} já existe, pulando...")
                continue
            
            # Criar arquivo
            endpoint_path.write_text(endpoint_content)
            print(f"✅ Criado: {endpoint_filename}")
            generated += 1
            
        except Exception as e:
            print(f"❌ Erro ao gerar endpoint para {schema_info.get('file_name', 'unknown')}: {e}")
    
    print(f"\n🎉 Gerados {generated} novos endpoints de alta prioridade!")
    
    # Generate low priority endpoints as well
    print(f"\n🚀 Gerando endpoints de BAIXA PRIORIDADE...")
    low_priority_generated = 0
    
    for schema_info in low_priority:
        try:
            schema_name = schema_info['file_name']
            endpoint_content = generator.generate_endpoint_template(schema_info)
            
            # Nome do arquivo endpoint (plural)
            endpoint_filename = generator._schema_to_endpoint_name(schema_name) + '.py'
            endpoint_path = generator.endpoints_path / endpoint_filename
            
            # Verificar se já existe
            if endpoint_path.exists():
                print(f"⚠️  {endpoint_filename} já existe, pulando...")
                continue
            
            # Criar arquivo
            endpoint_path.write_text(endpoint_content)
            print(f"✅ Criado: {endpoint_filename}")
            low_priority_generated += 1
            
        except Exception as e:
            print(f"❌ Erro ao gerar endpoint para {schema_info.get('file_name', 'unknown')}: {e}")
    
    print(f"\n🎉 Gerados {low_priority_generated} novos endpoints de baixa prioridade!")
    
    if generated > 0 or low_priority_generated > 0:
        print("\n🔧 Próximos passos:")
        print("1. Adicionar os novos endpoints ao api.py")
        print("2. Testar importação da aplicação")
        print("3. Executar testes para validar funcionalidade")

if __name__ == "__main__":
    main()
