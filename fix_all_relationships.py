#!/usr/bin/env python3
"""
Script para corrigir automaticamente TODOS os relacionamentos back_populates faltando
"""

import os
import re
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def find_missing_relationships():
    """Encontra todos os relacionamentos back_populates que estão faltando"""
    models_dir = Path("src/synapse/models")
    missing_relationships = {}
    
    # Buscar todos os back_populates nos arquivos de modelo
    for model_file in models_dir.glob("*.py"):
        if model_file.name in ["__init__.py"]:
            continue
            
        content = model_file.read_text()
        
        # Buscar padrões back_populates
        pattern = r'back_populates=["\']([\w_]+)["\']'
        matches = re.findall(pattern, content)
        
        # Buscar nome da classe do modelo
        class_pattern = r'class\s+(\w+)\(Base\)'
        class_matches = re.findall(class_pattern, content)
        
        if class_matches:
            current_model = class_matches[0]
            for relationship_name in matches:
                # Determinar modelo de destino baseado no relacionamento
                target_model = infer_target_model(model_file.stem, relationship_name)
                if target_model:
                    if target_model not in missing_relationships:
                        missing_relationships[target_model] = []
                    
                    missing_relationships[target_model].append({
                        'relationship_name': relationship_name,
                        'source_model': current_model,
                        'source_file': model_file.stem
                    })
    
    return missing_relationships

def infer_target_model(source_file, relationship_name):
    """Infere qual modelo precisa do relacionamento baseado no nome"""
    
    # Mapeamentos diretos conhecidos
    direct_mappings = {
        'users': 'User',
        'user': 'User',
        'tenants': 'Tenant', 
        'tenant': 'Tenant',
        'contacts': 'Contact',
        'workspaces': 'Workspace',
        'workspace': 'Workspace'
    }
    
    # Se o relacionamento aponta diretamente para um modelo conhecido
    if relationship_name in direct_mappings:
        return direct_mappings[relationship_name]
    
    # Lógica de inferência baseada no padrão do nome
    if relationship_name.endswith('_user') or relationship_name == 'owner' or relationship_name == 'creator':
        return 'User'
    elif relationship_name.endswith('_tenant') or relationship_name == 'tenant':
        return 'Tenant'
    elif relationship_name.endswith('_contact') or relationship_name.startswith('contact'):
        return 'Contact'
    elif relationship_name.endswith('_workspace') or relationship_name == 'workspace':
        return 'Workspace'
    
    return None

def generate_relationship_code(model_name, relationships):
    """Gera código para adicionar relacionamentos ao modelo"""
    code_lines = []
    
    for rel in relationships:
        rel_name = rel['relationship_name']
        source_model = rel['source_model']
        
        # Determinar se deve usar cascade
        cascade = 'cascade="all, delete-orphan"' if should_use_cascade(model_name, rel_name) else ''
        
        code_lines.append(f"""    # Relacionamento para {rel_name}
    {rel_name} = relationship(
        "{source_model}", back_populates="{get_back_populates_name(model_name, source_model)}"{',' if cascade else ''}
        {cascade}
    )""")
    
    return '\n\n'.join(code_lines)

def should_use_cascade(model_name, relationship_name):
    """Determina se deve usar cascade baseado no tipo de relacionamento"""
    # Relacionamentos que tipicamente usam cascade
    cascade_patterns = [
        'created_', 'owned_', 'user_', '_reports', '_events', '_metrics',
        '_executions', '_campaigns', '_journeys', '_alerts', '_exports'
    ]
    
    return any(pattern in relationship_name for pattern in cascade_patterns)

def get_back_populates_name(target_model, source_model):
    """Determina o nome correto do back_populates"""
    # Mapeamentos específicos
    mappings = {
        ('User', 'Campaign'): 'creator',
        ('User', 'AnalyticsAlert'): 'owner',
        ('User', 'AnalyticsReport'): 'owner',
        ('User', 'AnalyticsExport'): 'owner',
        ('Contact', 'ConversionJourney'): 'contact',
    }
    
    key = (target_model, source_model)
    if key in mappings:
        return mappings[key]
    
    # Padrão padrão
    return target_model.lower()

def main():
    """Função principal"""
    print("🔍 Encontrando relacionamentos faltando...")
    
    missing = find_missing_relationships()
    
    print(f"\n📋 Encontrados relacionamentos faltando em {len(missing)} modelos:")
    
    for model_name, relationships in missing.items():
        print(f"\n🔧 {model_name}:")
        for rel in relationships:
            print(f"   - {rel['relationship_name']} (from {rel['source_model']})")
    
    print("\n" + "="*60)
    print("🛠️  CÓDIGO PARA ADICIONAR AOS MODELOS:")
    print("="*60)
    
    for model_name, relationships in missing.items():
        print(f"\n# ===== ADICIONAR EM {model_name.upper()} =====")
        print(generate_relationship_code(model_name, relationships))

if __name__ == "__main__":
    main() 