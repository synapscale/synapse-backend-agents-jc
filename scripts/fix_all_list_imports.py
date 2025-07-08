#!/usr/bin/env python3

import os
import re
from pathlib import Path

def get_actual_classes(schema_file):
    """Get actual class names from a schema file."""
    try:
        with open(schema_file, 'r') as f:
            content = f.read()
        
        # Find all class definitions
        classes = re.findall(r'^class\s+(\w+)', content, re.MULTILINE)
        return classes
    except Exception as e:
        print(f"Error reading {schema_file}: {e}")
        return []

def fix_list_imports():
    """Fix list response imports in endpoint files."""
    
    schemas_dir = Path('src/synapse/schemas')
    endpoints_dir = Path('src/synapse/api/v1/endpoints')
    
    # Build a mapping of schema names to actual list classes
    schema_to_list_class = {}
    
    for schema_file in schemas_dir.glob('*.py'):
        if schema_file.name in ['__init__.py', 'base.py', 'auth.py', 'error.py']:
            continue
            
        schema_name = schema_file.stem
        classes = get_actual_classes(schema_file)
        
        # Find the list class (could be List, ListResponse, etc.)
        list_class = None
        for cls in classes:
            if 'List' in cls and 'Response' in cls:
                list_class = cls
                break
        
        if not list_class:
            for cls in classes:
                if cls.endswith('List') and not cls.endswith('ListResponse'):
                    list_class = cls
                    break
        
        if list_class:
            schema_to_list_class[schema_name] = list_class
    
    print("Schema to list class mappings:")
    for schema, list_class in schema_to_list_class.items():
        print(f"  {schema} -> {list_class}")
    
    # Fix endpoint files
    for file_path in endpoints_dir.glob('*.py'):
        if file_path.name == '__init__.py':
            continue
            
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            modified = False
            
            # Look for schema imports
            for schema_name, list_class in schema_to_list_class.items():
                # Check if this endpoint imports from this schema
                if f'from synapse.schemas.{schema_name} import' in content:
                    # Look for wrong list class names
                    wrong_names = [
                        f'{schema_name.title().replace("_", "")}ListResponse',
                        f'{schema_name.title().replace("_", "")}List',
                        f'{schema_name.replace("_", "").title()}ListResponse',
                        f'{schema_name.replace("_", "").title()}List'
                    ]
                    
                    for wrong_name in wrong_names:
                        if wrong_name in content and wrong_name != list_class:
                            content = content.replace(wrong_name, list_class)
                            modified = True
                            print(f"✅ Fixed {wrong_name} -> {list_class} in {file_path.name}")
            
            if modified:
                with open(file_path, 'w') as f:
                    f.write(content)
                
        except Exception as e:
            print(f"❌ Error processing {file_path.name}: {e}")

if __name__ == "__main__":
    fix_list_imports()
