#!/usr/bin/env python3
"""
Script para analisar relacionamentos bidirecionais em modelos SQLAlchemy
"""
import os
import re
import glob
from collections import defaultdict

def extract_relationships_from_file(file_path):
    """Extrai relacionamentos de um arquivo de modelo"""
    relationships = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extrair nome da classe
    class_match = re.search(r'class (\w+)\(Base\):', content)
    if not class_match:
        return []
    
    class_name = class_match.group(1)
    
    # Extrair relacionamentos
    # Padrão: relationship("Target", back_populates="field")
    relationship_pattern = r'(\w+)\s*=\s*relationship\(\s*["\']([^"\']+)["\'](?:.*?back_populates\s*=\s*["\']([^"\']+)["\'])?'
    
    for match in re.finditer(relationship_pattern, content, re.MULTILINE | re.DOTALL):
        field_name = match.group(1)
        target_model = match.group(2)
        back_populates = match.group(3) if match.group(3) else None
        
        # Limpar nome do modelo (remover prefixo de módulo se houver)
        if '.' in target_model:
            target_model = target_model.split('.')[-1]
        
        relationships.append({
            'source_class': class_name,
            'source_field': field_name,
            'target_class': target_model,
            'back_populates': back_populates,
            'file': file_path
        })
    
    return relationships

def main():
    # Encontrar todos os arquivos de modelo
    model_files = glob.glob('src/synapse/models/*.py')
    model_files = [f for f in model_files if not f.endswith('__init__.py')]
    
    all_relationships = []
    relationships_by_target = defaultdict(list)
    
    print("🔍 Analisando relacionamentos em modelos SQLAlchemy...")
    
    for file_path in model_files:
        relationships = extract_relationships_from_file(file_path)
        all_relationships.extend(relationships)
        
        for rel in relationships:
            relationships_by_target[rel['target_class']].append(rel)
    
    print(f"\n📊 Total de relacionamentos encontrados: {len(all_relationships)}")
    
    # Verificar relacionamentos bidirecionais
    bidirectional_problems = []
    
    for rel in all_relationships:
        if rel['back_populates']:
            # Procurar o relacionamento reverso
            target_class = rel['target_class']
            back_field = rel['back_populates']
            
            # Procurar relacionamento reverso
            reverse_found = False
            for reverse_rel in all_relationships:
                if (reverse_rel['source_class'] == target_class and 
                    reverse_rel['source_field'] == back_field and 
                    reverse_rel['target_class'] == rel['source_class'] and 
                    reverse_rel['back_populates'] == rel['source_field']):
                    reverse_found = True
                    break
            
            if not reverse_found:
                bidirectional_problems.append(rel)
    
    if bidirectional_problems:
        print(f"\n❌ Problemas de relacionamento bidirecionais encontrados ({len(bidirectional_problems)}):")
        for problem in bidirectional_problems:
            print(f"  ⚠️  {problem['source_class']}.{problem['source_field']} -> {problem['target_class']}")
            print(f"      back_populates='{problem['back_populates']}' mas relacionamento reverso não encontrado")
            print(f"      arquivo: {problem['file']}")
    else:
        print("\n✅ Todos os relacionamentos bidirecionais parecem estar corretos!")
    
    # Verificar modelos sem relacionamentos
    model_classes = set()
    for rel in all_relationships:
        model_classes.add(rel['source_class'])
        model_classes.add(rel['target_class'])
    
    # Verificar se há modelos referenciados que não foram encontrados
    missing_models = set()
    for rel in all_relationships:
        if rel['target_class'] not in [r['source_class'] for r in all_relationships]:
            missing_models.add(rel['target_class'])
    
    if missing_models:
        print(f"\n⚠️ Modelos referenciados mas não encontrados nos arquivos ({len(missing_models)}):")
        for model in sorted(missing_models):
            print(f"  📝 {model}")
    
    # Estatísticas por modelo
    print(f"\n📈 Estatísticas por modelo:")
    model_stats = defaultdict(int)
    for rel in all_relationships:
        model_stats[rel['source_class']] += 1
    
    for model, count in sorted(model_stats.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  📊 {model}: {count} relacionamentos")

if __name__ == "__main__":
    main()
