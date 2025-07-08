#!/usr/bin/env python3

import os
import re
import importlib.util
from pathlib import Path

def get_classes_from_file(file_path):
    """Extract class names from a Python file."""
    classes = []
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            # Find all class definitions
            class_matches = re.findall(r'^class\s+(\w+)', content, re.MULTILINE)
            classes.extend(class_matches)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    return classes

def fix_init_imports():
    """Fix all imports in __init__.py to match actual class names."""
    
    schemas_dir = Path("src/synapse/schemas")
    init_file = schemas_dir / "__init__.py"
    
    if not init_file.exists():
        print("__init__.py not found")
        return
    
    # Read current __init__.py
    with open(init_file, 'r') as f:
        content = f.read()
    
    # Find all schema files
    schema_files = []
    for file_path in schemas_dir.glob("*.py"):
        if file_path.name != "__init__.py":
            schema_files.append(file_path)
    
    # For each schema file, get actual classes and fix imports
    for schema_file in schema_files:
        module_name = schema_file.stem
        actual_classes = get_classes_from_file(schema_file)
        
        if not actual_classes:
            continue
            
        print(f"\nProcessing {module_name}.py")
        print(f"  Found classes: {actual_classes}")
        
        # Find the import block for this module
        import_pattern = rf'from \.{module_name} import \((.*?)\)'
        import_match = re.search(import_pattern, content, re.DOTALL)
        
        if import_match:
            # Extract current imports
            current_imports = import_match.group(1)
            current_class_names = [
                line.strip().rstrip(',') for line in current_imports.split('\n')
                if line.strip() and not line.strip().startswith('#')
            ]
            
            print(f"  Current imports: {current_class_names}")
            
            # Filter to only include classes that actually exist
            valid_imports = [cls for cls in current_class_names if cls in actual_classes]
            
            # Add any missing classes that should be imported
            for cls in actual_classes:
                if cls not in valid_imports and not cls.startswith('_'):  # Skip private classes
                    valid_imports.append(cls)
            
            print(f"  Valid imports: {valid_imports}")
            
            # Create new import block
            if valid_imports:
                new_import_block = f"from .{module_name} import (\n"
                for cls in sorted(valid_imports):
                    new_import_block += f"    {cls},\n"
                new_import_block += ")"
                
                # Replace in content
                content = re.sub(import_pattern, new_import_block, content, flags=re.DOTALL)
        
        # Also fix the __all__ export list
        all_pattern = rf'# {module_name.replace("_", " ").title()}.*?(?=# |$)'
        all_match = re.search(all_pattern, content, re.DOTALL)
        
        if all_match:
            # Extract current __all__ entries for this module
            all_block = all_match.group(0)
            all_entries = re.findall(r'"(\w+)"', all_block)
            
            # Filter to only include valid classes
            valid_all_entries = [cls for cls in all_entries if cls in actual_classes]
            
            # Add any missing classes
            for cls in actual_classes:
                if cls not in valid_all_entries and not cls.startswith('_'):
                    valid_all_entries.append(cls)
            
            if valid_all_entries:
                # Create new __all__ block
                new_all_block = f"    # {module_name.replace('_', ' ').title()}\n"
                for cls in sorted(valid_all_entries):
                    new_all_block += f'    "{cls}",\n'
                
                # Replace in content
                content = re.sub(all_pattern, new_all_block, content, flags=re.DOTALL)
    
    # Write updated content
    with open(init_file, 'w') as f:
        f.write(content)
    
    print("\nFixed all schema imports in __init__.py")

if __name__ == "__main__":
    fix_init_imports()
