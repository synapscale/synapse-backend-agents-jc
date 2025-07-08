#!/usr/bin/env python3

import re

def fix_init_structure():
    """Fix the structural issues in the __init__.py file."""
    
    init_file = "src/synapse/schemas/__init__.py"
    
    with open(init_file, 'r') as f:
        content = f.read()
    
    # Find where the __all__ section should start
    # Look for the last import statement and add __all__ after it
    
    # Split by lines to work with them
    lines = content.split('\n')
    
    # Find the end of imports and start of __all__
    all_start = -1
    for i, line in enumerate(lines):
        if line.strip() == '__all__ = [':
            all_start = i
            break
    
    if all_start == -1:
        print("Could not find __all__ section")
        return
    
    # Find the end of __all__ section
    all_end = -1
    for i in range(all_start + 1, len(lines)):
        if lines[i].strip() == ']':
            all_end = i
            break
    
    if all_end == -1:
        print("Could not find end of __all__ section")
        return
    
    # Remove any lines that are part of __all__ but appear before it
    # (these are the problematic lines)
    clean_lines = []
    skip_until_all = False
    
    for i, line in enumerate(lines):
        if i < all_start:
            # Before __all__ section - check if this line looks like an __all__ entry
            if line.strip().startswith('"') and line.strip().endswith('",'):
                # This looks like an __all__ entry that's in the wrong place
                # Skip it
                continue
            elif line.strip().startswith('# ') and not line.strip().startswith('from '):
                # This looks like a comment that should be in __all__
                # Skip it
                continue
            else:
                clean_lines.append(line)
        else:
            clean_lines.append(line)
    
    # Write the cleaned content
    with open(init_file, 'w') as f:
        f.write('\n'.join(clean_lines))
    
    print("Fixed __init__.py structure")

if __name__ == "__main__":
    fix_init_structure()
