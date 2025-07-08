#!/usr/bin/env python3

import os
import re
from pathlib import Path

def regenerate_init_file():
    """Regenerate the __init__.py file with proper structure."""
    
    schemas_dir = Path("src/synapse/schemas")
    init_file = schemas_dir / "__init__.py"
    
    # Get all schema files
    schema_files = []
    for file_path in schemas_dir.glob("*.py"):
        if file_path.name != "__init__.py":
            schema_files.append(file_path)
    
    # Generate content
    content = []
    
    # Add file header
    content.append('"""')
    content.append('Synapse schemas module.')
    content.append('"""')
    content.append('')
    
    # Add imports for each schema file
    all_exports = []
    
    for schema_file in sorted(schema_files):
        module_name = schema_file.stem
        
        # Get classes from the file
        classes = []
        try:
            with open(schema_file, 'r') as f:
                file_content = f.read()
                # Find all class definitions
                class_matches = re.findall(r'^class\s+(\w+)', file_content, re.MULTILINE)
                classes = [cls for cls in class_matches if not cls.startswith('_')]
        except Exception as e:
            print(f"Error reading {schema_file}: {e}")
            continue
        
        if not classes:
            continue
            
        # Add import block
        content.append(f"# {module_name.replace('_', ' ').title()}")
        content.append(f"from .{module_name} import (")
        for cls in sorted(classes):
            content.append(f"    {cls},")
        content.append(")")
        content.append("")
        
        # Add to exports
        all_exports.extend(classes)
    
    # Add __all__ export
    content.append("__all__ = [")
    for export in sorted(all_exports):
        content.append(f'    "{export}",')
    content.append("]")
    
    # Write the file
    with open(init_file, 'w') as f:
        f.write('\n'.join(content))
    
    print(f"Regenerated {init_file} with {len(all_exports)} exports")

if __name__ == "__main__":
    regenerate_init_file()
