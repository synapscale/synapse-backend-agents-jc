#!/usr/bin/env python3

import os
import re
from pathlib import Path

def fix_user_imports():
    """Fix User import issues in endpoint files."""
    
    endpoints_dir = Path('src/synapse/api/v1/endpoints')
    
    for file_path in endpoints_dir.glob('*.py'):
        if file_path.name == '__init__.py':
            continue
            
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Check if the file uses User but doesn't import it
            if ': User = ' in content or 'User' in content:
                # Check if User is already imported
                if 'from synapse.models.user import User' not in content:
                    # Find the line with deps import
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if 'from synapse.api.deps import' in line:
                            # Add User import after deps import
                            lines.insert(i + 1, 'from synapse.models.user import User')
                            break
                    
                    # Write back the file
                    with open(file_path, 'w') as f:
                        f.write('\n'.join(lines))
                    
                    print(f"✅ Fixed User import in {file_path.name}")
                else:
                    print(f"⚠️  {file_path.name} already has User import")
            else:
                print(f"ℹ️  {file_path.name} doesn't use User")
                
        except Exception as e:
            print(f"❌ Error processing {file_path.name}: {e}")

if __name__ == "__main__":
    fix_user_imports()
