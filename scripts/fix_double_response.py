#!/usr/bin/env python3

import os
import re
from pathlib import Path

def fix_double_response():
    """Fix ResponseResponse issues in endpoint files."""
    
    endpoints_dir = Path('src/synapse/api/v1/endpoints')
    
    for file_path in endpoints_dir.glob('*.py'):
        if file_path.name == '__init__.py':
            continue
            
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Fix ResponseResponse issues
            original_content = content
            content = re.sub(r'(\w+)ResponseResponse(\w*)', r'\1Response\2', content)
            
            if content != original_content:
                with open(file_path, 'w') as f:
                    f.write(content)
                print(f"✅ Fixed ResponseResponse in {file_path.name}")
            else:
                print(f"ℹ️  {file_path.name} - no ResponseResponse issues")
                
        except Exception as e:
            print(f"❌ Error processing {file_path.name}: {e}")

if __name__ == "__main__":
    fix_double_response()
