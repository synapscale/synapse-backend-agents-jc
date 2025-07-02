#!/usr/bin/env python3
"""
Test Scripts Cleanup Analysis for SynapScale

This script analyzes all test files in the repository root and provides:
1. Categorization of test files (keep, remove, consolidate)
2. File size and complexity analysis
3. Cleanup recommendations
4. Generate cleanup script
"""

import os
import re
import json
import ast
from datetime import datetime
from typing import Dict, List, Any, Tuple
from pathlib import Path


def get_file_info(filepath: str) -> Dict[str, Any]:
    """Get detailed information about a file"""
    try:
        stat = os.stat(filepath)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        return {
            'size_bytes': stat.st_size,
            'size_kb': round(stat.st_size / 1024, 1),
            'lines': len(content.splitlines()),
            'last_modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'content_preview': content[:500] + '...' if len(content) > 500 else content
        }
    except Exception as e:
        return {
            'error': str(e),
            'size_bytes': 0,
            'size_kb': 0,
            'lines': 0,
            'last_modified': None,
            'content_preview': ''
        }


def analyze_python_file(filepath: str) -> Dict[str, Any]:
    """Analyze Python file structure and complexity"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse AST to analyze structure
        tree = ast.parse(content)
        
        functions = []
        classes = []
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                functions.append(node.name)
            elif isinstance(node, ast.ClassDef):
                classes.append(node.name)
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                for alias in node.names:
                    imports.append(f"{module}.{alias.name}")
        
        # Check for test patterns
        test_patterns = {
            'pytest': 'pytest' in content or '@pytest' in content,
            'unittest': 'unittest' in content or 'TestCase' in content,
            'async_tests': 'async def test_' in content or 'await' in content,
            'fastapi_client': 'TestClient' in content or 'client =' in content,
            'database_tests': 'session' in content.lower() or 'db' in content.lower(),
            'mock_tests': 'mock' in content.lower() or 'patch' in content.lower()
        }
        
        return {
            'functions': functions,
            'classes': classes,
            'imports': imports,
            'function_count': len(functions),
            'class_count': len(classes),
            'import_count': len(imports),
            'test_patterns': test_patterns,
            'has_main': '__main__' in content,
            'has_docstrings': '"""' in content or "'''" in content
        }
        
    except Exception as e:
        return {
            'error': str(e),
            'functions': [],
            'classes': [],
            'imports': [],
            'function_count': 0,
            'class_count': 0,
            'import_count': 0,
            'test_patterns': {},
            'has_main': False,
            'has_docstrings': False
        }


def categorize_test_file(filename: str, file_info: Dict[str, Any], analysis: Dict[str, Any]) -> Tuple[str, str, List[str]]:
    """Categorize test file based on patterns and analysis"""
    recommendations = []
    
    # File patterns analysis
    if 'debug' in filename.lower():
        return 'REMOVE', 'Debug/temporary file', ['Delete - appears to be debug/temporary file']
    
    if 'simple' in filename.lower() and file_info['size_kb'] < 5:
        return 'REMOVE', 'Simple/basic test file', ['Delete - likely superseded by comprehensive tests']
    
    if 'temp' in filename.lower() or 'backup' in filename.lower():
        return 'REMOVE', 'Temporary/backup file', ['Delete - temporary or backup file']
    
    if filename.startswith('test_') and 'comprehensive' in filename:
        return 'KEEP', 'Comprehensive test suite', ['Keep - appears to be main test suite']
    
    if filename.startswith('test_') and any(pattern in filename for pattern in ['auth', 'llm', 'endpoints']):
        return 'KEEP', 'Core functionality test', ['Keep - tests core functionality']
    
    if filename.startswith('validate_') or filename.startswith('check_'):
        return 'REVIEW', 'Validation/analysis script', ['Review - might be useful for validation']
    
    if filename.startswith('analyze_') or filename.startswith('comprehensive_'):
        return 'REVIEW', 'Analysis script', ['Review - analysis tool that might be useful']
    
    if 'model' in filename and 'test' in filename:
        return 'REVIEW', 'Model validation test', ['Review - might be consolidated with other model tests']
    
    if file_info['size_kb'] > 50:
        return 'REVIEW', 'Large file', ['Review - large file, check if it can be split or consolidated']
    
    if analysis.get('function_count', 0) < 3 and file_info['size_kb'] < 10:
        return 'REMOVE', 'Small/minimal test', ['Delete - minimal test that might be redundant']
    
    # Default categorization
    if filename.startswith('test_'):
        return 'REVIEW', 'Test file', ['Review - assess if needed or can be consolidated']
    else:
        return 'REVIEW', 'Other script', ['Review - assess purpose and necessity']


def generate_cleanup_script(analysis_results: Dict[str, Any]) -> str:
    """Generate shell script for cleanup operations"""
    script_lines = [
        "#!/bin/bash",
        "# SynapScale Test Files Cleanup Script",
        "# Generated automatically - review before executing",
        "",
        "echo '🧹 Starting SynapScale test files cleanup...'",
        "echo '⚠️  WARNING: This will DELETE files. Make sure you have backups!'",
        "echo",
        "read -p 'Continue? (y/N): ' -n 1 -r",
        "echo",
        "if [[ ! $REPLY =~ ^[Yy]$ ]]; then",
        "    echo 'Cleanup cancelled.'",
        "    exit 1",
        "fi",
        "",
        "# Create backup directory",
        "mkdir -p backup/test_files_$(date +%Y%m%d_%H%M%S)",
        "BACKUP_DIR=\"backup/test_files_$(date +%Y%m%d_%H%M%S)\"",
        "",
        "echo '📁 Creating backup directory: $BACKUP_DIR'",
        ""
    ]
    
    # Files to remove
    remove_files = [f for f, data in analysis_results['files'].items() 
                   if data['category'] == 'REMOVE']
    
    if remove_files:
        script_lines.extend([
            "# Files to remove (backup first)",
            "echo '🗑️  Removing deprecated/temporary test files...'",
            ""
        ])
        
        for filename in remove_files:
            script_lines.extend([
                f"if [ -f '{filename}' ]; then",
                f"    echo '  Backing up and removing: {filename}'",
                f"    cp '{filename}' \"$BACKUP_DIR/\"",
                f"    rm '{filename}'",
                f"fi",
                ""
            ])
    
    # Files to review (move to review directory)
    review_files = [f for f, data in analysis_results['files'].items() 
                   if data['category'] == 'REVIEW' and 'consolidate' in data['reason'].lower()]
    
    if review_files:
        script_lines.extend([
            "# Files to review/consolidate",
            "mkdir -p review_for_consolidation",
            "echo '📋 Moving files that need review to review_for_consolidation/...'",
            ""
        ])
        
        for filename in review_files:
            script_lines.extend([
                f"if [ -f '{filename}' ]; then",
                f"    echo '  Moving for review: {filename}'",
                f"    mv '{filename}' review_for_consolidation/",
                f"fi",
                ""
            ])
    
    # Archive analysis files
    analysis_files = [f for f in os.listdir('.') if f.endswith('.json') and 'analysis' in f]
    if analysis_files:
        script_lines.extend([
            "# Archive analysis reports",
            "mkdir -p archive/analysis_reports",
            "echo '📊 Archiving analysis reports...'",
            ""
        ])
        
        for filename in analysis_files:
            script_lines.extend([
                f"if [ -f '{filename}' ]; then",
                f"    echo '  Archiving: {filename}'",
                f"    mv '{filename}' archive/analysis_reports/",
                f"fi",
                ""
            ])
    
    script_lines.extend([
        "echo '✅ Cleanup completed!'",
        "echo '📁 Backup created in: $BACKUP_DIR'",
        "echo '📋 Files for review in: review_for_consolidation/'",
        "echo '📊 Analysis reports in: archive/analysis_reports/'",
        ""
    ])
    
    return '\n'.join(script_lines)


def analyze_test_cleanup():
    """Main function to analyze test files and provide cleanup recommendations"""
    print("🔍 Starting Test Scripts Cleanup Analysis")
    print("=" * 60)
    
    # Get all Python files in root directory
    root_files = [f for f in os.listdir('.') if f.endswith('.py')]
    test_related_files = [f for f in root_files if any(keyword in f.lower() 
                         for keyword in ['test', 'validate', 'check', 'analyze', 'comprehensive', 'verify', 'temp', 'backup'])]
    
    print(f"📁 Found {len(root_files)} Python files in root directory")
    print(f"🧪 Found {len(test_related_files)} test/analysis related files")
    
    analysis_results = {
        'timestamp': datetime.now().isoformat(),
        'summary': {
            'total_files': len(test_related_files),
            'total_size_kb': 0,
            'categories': {
                'KEEP': 0,
                'REMOVE': 0,
                'REVIEW': 0
            }
        },
        'files': {},
        'recommendations': []
    }
    
    # Analyze each file
    for filename in test_related_files:
        print(f"  📄 Analyzing: {filename}")
        
        # Get file info
        file_info = get_file_info(filename)
        analysis_results['summary']['total_size_kb'] += file_info['size_kb']
        
        # Analyze Python structure
        python_analysis = analyze_python_file(filename)
        
        # Categorize file
        category, reason, recommendations = categorize_test_file(filename, file_info, python_analysis)
        analysis_results['summary']['categories'][category] += 1
        
        # Store analysis
        analysis_results['files'][filename] = {
            'category': category,
            'reason': reason,
            'recommendations': recommendations,
            'file_info': file_info,
            'python_analysis': python_analysis
        }
    
    # Generate summary recommendations
    total_remove_size = sum(data['file_info']['size_kb'] for data in analysis_results['files'].values() 
                           if data['category'] == 'REMOVE')
    
    analysis_results['recommendations'] = [
        f"Remove {analysis_results['summary']['categories']['REMOVE']} deprecated/temporary files ({total_remove_size:.1f} KB)",
        f"Review {analysis_results['summary']['categories']['REVIEW']} files for consolidation",
        f"Keep {analysis_results['summary']['categories']['KEEP']} core test files",
        "Consider consolidating model validation scripts into a single comprehensive test",
        "Move analysis reports to archive directory",
        "Create backup before any file deletion"
    ]
    
    # Save detailed analysis
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    analysis_filename = f"test_cleanup_analysis_{timestamp}.json"
    
    with open(analysis_filename, 'w') as f:
        json.dump(analysis_results, f, indent=2, default=str)
    
    # Generate cleanup script
    cleanup_script = generate_cleanup_script(analysis_results)
    script_filename = "cleanup_tests.sh"
    
    with open(script_filename, 'w') as f:
        f.write(cleanup_script)
    
    os.chmod(script_filename, 0o755)  # Make executable
    
    # Print summary
    print(f"\n📊 CLEANUP ANALYSIS SUMMARY")
    print(f"=" * 40)
    print(f"Total Files Analyzed: {analysis_results['summary']['total_files']}")
    print(f"Total Size: {analysis_results['summary']['total_size_kb']:.1f} KB")
    print(f"Files to Keep: {analysis_results['summary']['categories']['KEEP']}")
    print(f"Files to Remove: {analysis_results['summary']['categories']['REMOVE']} ({total_remove_size:.1f} KB)")
    print(f"Files to Review: {analysis_results['summary']['categories']['REVIEW']}")
    
    print(f"\n📋 FILES TO KEEP:")
    for filename, data in analysis_results['files'].items():
        if data['category'] == 'KEEP':
            print(f"  ✅ {filename:<40} | {data['file_info']['size_kb']:>6.1f} KB | {data['reason']}")
    
    print(f"\n📋 FILES TO REVIEW/CONSOLIDATE:")
    for filename, data in analysis_results['files'].items():
        if data['category'] == 'REVIEW':
            print(f"  📋 {filename:<40} | {data['file_info']['size_kb']:>6.1f} KB | {data['reason']}")
    
    print(f"\n🗑️  FILES TO REMOVE:")
    for filename, data in analysis_results['files'].items():
        if data['category'] == 'REMOVE':
            print(f"  ❌ {filename:<40} | {data['file_info']['size_kb']:>6.1f} KB | {data['reason']}")
    
    print(f"\n📄 RECOMMENDATIONS:")
    for i, rec in enumerate(analysis_results['recommendations'], 1):
        print(f"  {i}. {rec}")
    
    print(f"\n💾 Analysis saved to: {analysis_filename}")
    print(f"🧹 Cleanup script created: {script_filename}")
    print(f"   Run with: ./{script_filename}")
    
    return analysis_results


if __name__ == "__main__":
    try:
        results = analyze_test_cleanup()
        print(f"\n✅ Test cleanup analysis completed successfully!")
    except Exception as e:
        print(f"\n❌ Analysis failed: {e}")
        raise 