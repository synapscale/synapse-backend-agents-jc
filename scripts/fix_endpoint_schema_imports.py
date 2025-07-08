#!/usr/bin/env python3

import os
import re
from pathlib import Path

def fix_schema_imports():
    """Fix schema import issues in endpoint files."""
    
    endpoints_dir = Path('src/synapse/api/v1/endpoints')
    
    # Common schema naming fixes
    import_fixes = {
        'NodeExecutionListResponse': 'NodeExecutionList',
        'NodeExecutionStatusListResponse': 'NodeExecutionStatusList',
        'NodeRatingListResponse': 'NodeRatingListResponse',
        'NodeCategoryListResponse': 'NodeCategoryListResponse',
        'NodeTemplateListResponse': 'NodeTemplateListResponse',
        'NodeTypeListResponse': 'NodeTypeListResponse',
        'BusinessMetricListResponse': 'BusinessMetricListResponse',
        'AuditLogListResponse': 'AuditLogListResponse',
        'MessageListResponse': 'MessageListResponse',
        'ProjectVersionListResponse': 'ProjectVersionListResponse',
        'ProjectCommentListResponse': 'ProjectCommentListResponse',
        'ProjectCollaboratorListResponse': 'ProjectCollaboratorListResponse',
        'CustomReportListResponse': 'CustomReportListResponse',
        'ComponentVersionListResponse': 'ComponentVersionListResponse',
        'EmailVerificationTokenListResponse': 'EmailVerificationTokenListResponse',
        'PasswordResetTokenListResponse': 'PasswordResetTokenListResponse',
        'WebhookLogListResponse': 'WebhookLogListResponse',
        'ModelListResponse': 'ModelListResponse',
        'AuditListResponse': 'AuditListResponse',
    }
    
    for file_path in endpoints_dir.glob('*.py'):
        if file_path.name == '__init__.py':
            continue
            
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            modified = False
            
            # Fix schema imports
            for old_import, new_import in import_fixes.items():
                if old_import in content:
                    content = content.replace(old_import, new_import)
                    modified = True
                    print(f"✅ Fixed {old_import} -> {new_import} in {file_path.name}")
            
            if modified:
                with open(file_path, 'w') as f:
                    f.write(content)
            else:
                print(f"ℹ️  {file_path.name} - no changes needed")
                
        except Exception as e:
            print(f"❌ Error processing {file_path.name}: {e}")

if __name__ == "__main__":
    fix_schema_imports()
